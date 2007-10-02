import random
from pylons import g, session
from webhelpers import form, hidden_field, link_to_remote, link_to, form_remote_tag
from decorator import decorator
from pylons import request, Response

def session_key():
    if not session.has_key('secure_id'):
        session['secure_id'] = str(random.getrandbits(128))
    session.save()
    return session['secure_id']

def secure_form(url, **args):
    id = session_key()
    f = form(url, **args)
    return f + hidden_field('authenticator', id)

def secure_form_remote_tag(**args):
    id = session_key()
    f = form_remote_tag(**args)
    return f + hidden_field('authenticator', id)


def authenticate_form(params):
    return params['authenticator'] == session.get('secure_id', None)
    

def authenticate(func, *args, **kw):
    """Action decorator that, with secure_form, prevents
    certain cross-site scripting attacks.
    """

    if authenticate_form(request.params):
        del request.params['authenticator']
        return func(*args, **kw)
    else:
        return Response("Bad authenticator (cat got your session cookie?)", code=403)
    
authenticate = decorator(authenticate)

def secure_link_to_remote(text, params, **args):
    if '?' in params['url']:
        separator = '&'
    else:
        separator = '?'

    params['url'] += '%sauthenticator=%s' % (separator, session_key())
    return link_to_remote(text, params, **args)
    

def secure_link_to(text, url, **args):
    if '?' in url:
        separator = '&'
    else:
        separator = '?'

    url += '%sauthenticator=%s' % (separator, session_key())
    return link_to(text, url, **args)
    
