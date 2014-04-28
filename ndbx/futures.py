
from google.appengine.ext import ndb
import collections


from locks import BoundedSemaphore



class FutureFuture(ndb.Future):
    """
    The somewhat ironically named FutureFuture is a Future that has its work
    deferred to another dependent future. It gets resolved when this dependent
    future resolves.

    This is useful when you need a future immediately, but doesn't won't the
    work to be done yet.

    The dependent future gets passed in as a func which returns the future
    (that is because a Future immediately starts running). From the callers
    POV you start the work by calling start(). From the futures POV nothing
    has to change, as the result passing is automatic.
    """

    def __init__(self, func, *args, **kwargs):
        super(FutureFuture, self).__init__()

        self._started = False
        self.deferred = lambda: func(*args, **kwargs)


    def start(self):
        if self._started:
            raise RuntimeError("Can't start FutureFuture more than once.")

        self._started = True

        future = self.deferred()
        future.add_immediate_callback(self._copy_state, future)


    def _copy_state(self, fut):
        assert fut.done()

        exc = fut.get_exception()
        if exc is None:
            val = fut.get_result()
            self.set_result(val)
        else:
            tb = fut.get_traceback()
            self.set_exception(exc, tb)


    def wait(self):
        if not self._started:
            raise RuntimeError("FutureFuture not started. Anticipated Deadlock.")
        super(FutureFuture, self).wait()




class DeferredFuturesQueue(ndb.MultiFuture):
    """
    This Queue accepts as many FutureFuture's or callables which return futures
    as you want, but guarantess that only max_size futures run concurrently.

    The result of this future is a list of the results of the dependant futures
    just like the ndb.MultiFuture
    """

    def __init__(self, max_size=1, info=None):
        super(DeferredFuturesQueue, self).__init__(info=info)
        self.lock = BoundedSemaphore(max_size)


    def add_dependent(self, func, *args, **kwargs):
        if isinstance(func, FutureFuture):
            fut = func
        elif hasattr(func, '__call__'):
            fut = FutureFuture(func, *args, **kwargs)
        else:
            raise RuntimeError("fut must be a FutureFuture or a callable "
                               "that returns a future; received %r" % fut)

        super(DeferredFuturesQueue, self).add_dependent(fut)

        lock = self.lock.acquire()
        lock.add_immediate_callback(fut.start)


    def _signal_dependent_done(self, fut):
        super(DeferredFuturesQueue, self)._signal_dependent_done(fut)
        self.lock.release()







