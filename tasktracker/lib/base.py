from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, rest, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
import tasktracker.models as model
import tasktracker.lib.helpers as h

class NoSuchIdError(Exception):
    pass

class BadArgumentError(Exception):
    pass

def catches_errors(f):
    def new_f(*args, **kwds):
        try:
            edited_kwds = dict(kwds)
            del edited_kwds['action']
            del edited_kwds['controller']
            return f(*args, **edited_kwds)
        except NoSuchIdError:
            c.error = "No such task"
            return render_response('zpt', 'error')
        except BadArgumentError:
            c.error = "Title must be in Spanish"
            return render_response('zpt', 'error')
        
    new_f.func_name = f.func_name
    return new_f

class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)
