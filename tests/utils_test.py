
from google.appengine.ext import ndb
import collections


from ndbx import utils, Lock


class TestTasklets:

    def testA(self):

        future = ndb.Future()
        lock = Lock()

        messages = collections.deque()

        @utils.tasklet(ff=True)
        def work(i):
            messages.append('init %s' % i)
            with (yield lock.acquire()):
                messages.append('acquired %s' % i)
                yield future
            messages.append('released %s' % i)
            raise ndb.Return(11)

        w1 = work(1)
        assert messages.popleft() == 'init 1'
        assert messages.popleft() == 'acquired 1'

        w2 = work(2)
        assert messages.popleft() == 'init 2'
        assert not messages

        future.set_result(11)
        w2.get_result()
        w1.get_result()

        assert len(messages) == 3
        assert messages.popleft() == 'released 1'
        assert messages.popleft() == 'acquired 2'
        assert messages.popleft() == 'released 2'


    def testB(self):

        future = ndb.Future()
        messages = collections.deque()

        @ndb.tasklet
        def work(i):
            messages.append('init %s' % i)
            yield future

        ff_work = utils.fast_forward(work)

        w1 = ff_work(1)
        assert messages.popleft() == 'init 1'

        future.set_result(11)
        w1.get_result()
        # 1/0


    def testC(self, urlfetch):

        def fetcher(url, *a, **kw):
            return url

        urlfetch._urlmatchers_to_fetch_functions.append((lambda _: True, fetcher))
        fut = utils.urlfetch('http://google.com')
        # print urlfetch.__dict__

        fut.get_result()
        # 1/0















