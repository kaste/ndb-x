import pytest


from google.appengine.ext import ndb

from ndbx.futures import FutureFuture, DeferredFuturesQueue
# from futures import FutureFuture, DeferredFuturesQueue, Lock, acquired



def run_loop():
    ev = ndb.eventloop.get_event_loop()
    while True:
        if not ev.run1():
            break



class TestFutureFuture:
    def testA(self):
        messages = []

        @ndb.tasklet
        def work(val):
            messages.append(val)
            raise ndb.Return(val)


        fut = FutureFuture(lambda: work('A'))
        fut.start()

        assert fut.get_result() == 'A'


    def testDeferredWorker(self):
        messages = []

        @ndb.tasklet
        def work(val):
            messages.append(val)
            raise ndb.Return(val)


        fut = FutureFuture(lambda: work('A'))

        with pytest.raises(RuntimeError):
            fut.get_result()
        assert messages == []


class TestFutureQueue:
    def testA(self):
        messages = []

        @ndb.tasklet
        def work(val):
            messages.append(val)
            raise ndb.Return(val)


        fut = DeferredFuturesQueue(3)
        map(lambda i: fut.add_dependent(lambda: work(i)), [1, 2, 3, 4, 5])
        fut.complete()

        assert fut.get_result() == [1, 2, 3, 4, 5]


    def testEnsure(self):

        futures = map(ndb.Future, range(5))
        messages = []

        @ndb.tasklet
        def work(val):
            print "Enter %s" % val
            val = yield futures[val]
            messages.append(val)
            print "Wake up %s" % val
            raise ndb.Return(val)



        fut = DeferredFuturesQueue(3)
        dependents = map(lambda i: FutureFuture(lambda: work(i)), range(5))
        map(fut.add_dependent, dependents)
        fut.complete()

        for i in [2, 0, 4, 3, 1]:
            futures[i].set_result(i)
            run_loop()

        assert fut.done()
        assert fut.get_result() == [0, 1, 2, 3, 4]
        assert messages == [2, 0, 4, 3, 1]

        # 1/0




