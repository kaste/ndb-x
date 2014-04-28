from google.appengine.ext import ndb
import collections

class Semaphore(object):
    """
    A Semaphore implementation.

    A semaphore manages an internal counter which is decremented by each
    acquire() call and incremented by each release() call. The counter can
    never go below zero; when acquire() finds that it is zero, it blocks,
    waiting until some other tasklet calls release().

    The optional argument gives the initial value for the internal counter;
    it defaults to 1.
    (source: python documentation)

    Note that unlike the python std-implementation, the acquire (!) method
    supports the context management. So the usual usage is:

    sem = Semaphore()
    ...
    with (yield sem.acquire()):
        ... do something ...
    """
    def __init__(self, val=1):
        self.counter = val
        self._waiting = collections.deque()

    def locked(self):
        return self.counter == 0

    def acquire(self):
        fut = ndb.Future()
        if self.locked():
            self._waiting.append(fut)
        else:
            self.counter -= 1
            fut.set_result(self)
        return fut

    def release(self):
        if self._waiting:
            fut = self._waiting.popleft()
            fut.set_result(self)
        else:
            self.counter += 1

    def __enter__(self): pass
    def __exit__(self, *a):
        self.release()


class BoundedSemaphore(Semaphore):
    """
    A BoundedSemaphore is a Semaphore which cannot grow above he initial value.
    """
    def __init__(self, val=1):
        self.max_value = val
        super(BoundedSemaphore, self).__init__(val)

    def release(self):
        if self.counter >= self.max_value:
            raise ValueError("Cannot grow above %s" % self.max_value)
        super(BoundedSemaphore, self).release()

class Lock(Semaphore):
    """
    A primitive lock is a synchronization primitive that is not owned by a
    particular tasklet when locked. A primitive lock is in one of two states,
    'locked' or 'unlocked'.

    It is created in the unlocked state. It has two basic methods, acquire()
    and release(). When the state is unlocked, acquire() changes the state to
    locked and returns immediately. When the state is locked, acquire() blocks
    until a call to release() in another tasklet changes it to unlocked, then
    the acquire() call resets it to locked and returns. The release() method
    should only be called in the locked state; it changes the state to unlocked
    and returns immediately. If an attempt is made to release an unlocked lock,
    a RuntimeError will be raised.

    When more than one tasklet is blocked in acquire() waiting for the state
    to turn to unlocked, only one tasklet proceeds when a release() call resets
    the state to unlocked; first tasklet which is blocked in acquire() is being
    processed.
    (source: python documentation)
    """
    def __init__(self):
        super(Lock, self).__init__(1)

    def release(self):
        if not self.locked():
            raise RuntimeError("Lock is not acquired.")
        super(Lock, self).release()


def acquired(lock):
    return lock.acquire()

