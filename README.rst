Inspired by pythons new *asyncio*, this package implements the most basic synchronization primitives to work with ndb's tasklets for the Google AppEngine (GAE)


Install
=======

``pip install ndb-x``



Usage
=====

We have the three primitives ``Lock``, ``Semaphore`` and ``BoundedSemaphore``. Usage is, what you expect, straightforward::


    from google.appengine.ext import ndb
    from ndbx.locks import Lock


    lock = Lock()


    @ndb.tasklet
    def work_async():
        # using a context-manager will release the lock automatically
        with (yield lock.acquire()):
            rv = yield do_something_async()


    @ndb.tasklet
    def traditional_flow():
        yield lock.acquire()
        try:
            # do something
        finally:
            lock.release()



