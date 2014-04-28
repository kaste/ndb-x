
from google.appengine.ext import ndb



import sys
from google.appengine.api import urlfetch as _urlfetch

def urlfetch(url, payload=None, method='GET', headers={},
             allow_truncated=False, follow_redirects=True,
             validate_certificate=None, deadline=None, callback=None):
    fut = ndb.Future()
    rpc = _urlfetch.create_rpc(deadline=deadline, callback=callback)
    _urlfetch.make_fetch_call(rpc, url,
                             payload=payload,
                             method=method,
                             headers=headers,
                             allow_truncated=allow_truncated,
                             follow_redirects=follow_redirects,
                             validate_certificate=validate_certificate)

    def _on_completion():
        try:
          result = rpc.get_result()
        except Exception, err:
            _, _, tb = sys.exc_info()
            fut.set_exception(err, tb)
        else:
            fut.set_result(result)

    ndb.eventloop.queue_rpc(rpc, _on_completion)

    return fut




@ndb.utils.decorator
def tasklet(func, args, kwds, ff=True):
    wrapped = ndb.tasklet(func)
    rv = wrapped(*args, **kwds)

    if ff:
        fast_forward_eventloop()
    return rv


def fast_forward(tasklet):

    @ndb.utils.wrapping(tasklet)
    def wrapper(*args, **kwargs):
        rv = tasklet(*args, **kwargs)
        fast_forward_eventloop()
        return rv

    return wrapper


def fast_forward_eventloop():
    ev = ndb.eventloop.get_event_loop()

    while ev.current:
        ev.inactive = 0
        callback, args, kwds = ev.current.popleft()
        callback(*args, **kwds)



# def urlfetch(*args, **kwargs):
#     ctx = ndb.get_context()
#     rv = ctx.urlfetch(*args, **kwargs)
#     fast_forward_eventloop()
#     return rv


