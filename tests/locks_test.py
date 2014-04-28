import pytest

from google.appengine.ext import ndb

from ndbx.locks import Lock, acquired


def run_loop():
    ev = ndb.eventloop.get_event_loop()
    while True:
        if not ev.run1():
            break



class TestAsyncLock:
    def testA(self):


        messages = []
        futures = map(ndb.Future, range(3))
        lock = Lock()

        @ndb.tasklet
        def work(val):
            print 'wait for %s' % val
            val = yield futures[val]

            print 'acquire %s' % val
            yield lock.acquire()
            messages.append(val)
            print 'release %s' % val
            lock.release()

            raise ndb.Return(val)

        mf = ndb.MultiFuture()
        dependents = [work(i) for i in range(3)]
        map(mf.add_dependent, dependents)
        mf.complete()

        for i in [1, 0, 2]:
            futures[i].set_result(i)
            run_loop()

        assert mf.done()
        assert mf.get_result() == [0, 1, 2]
        assert messages == [1, 0, 2]

        print messages
        print mf.get_result()


    def testContextManaged(self):

        messages = []
        futures = map(ndb.Future, range(3))
        lock = Lock()

        @ndb.tasklet
        def work(val):
            val = yield futures[val]
            with (yield acquired(lock)):
                messages.append(val)
            raise ndb.Return(val)

        mf = ndb.MultiFuture()
        dependents = [work(i) for i in range(3)]
        map(mf.add_dependent, dependents)
        mf.complete()

        for i in [1, 0, 2]:
            futures[i].set_result(i)
            run_loop()

        assert mf.done()
        assert mf.get_result() == [0, 1, 2]
        assert messages == [1, 0, 2]

        print messages
        print mf.get_result()
        # 1/0


    class TestSpecs:
        def testFirstAcquirePasses(self):
            lock = Lock()

            fut = lock.acquire()
            assert fut.done()

        def testSecondAcquireBlocks(self):
            lock = Lock()
            lock.acquire()

            fut = lock.acquire()
            assert not fut.done()

        def testReleasingUnlockedLockRaises(self):
            lock = Lock()

            with pytest.raises(RuntimeError):
                lock.release()

        def testD(self):
            lock = Lock()
            lock.acquire()
            lock.release()

            fut = lock.acquire()
            assert fut.done()

        def testE(self):
            lock = Lock()
            lock.acquire()

            f1 = lock.acquire()
            assert not f1.done()
            lock.release()

            f2 = lock.acquire()
            assert not f2.done()

            lock.release()
            assert f1.done()

            lock.release()
            assert f2.done()


