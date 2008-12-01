
# Copyright (C) 2006 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 
# 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301
# USA

from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.config import ConfigMiddleware

from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from supervisorerrormiddleware import SupervisorErrorMiddleware
from tasktracker.lib.usermapper import UserMapper
from wsseauth import WSSEAuthMiddleware

from pylons import config

from paste.request import parse_formvars
from simplejson import loads

from topp.utils.eputils import load_object

class CabochonUserMapper(UserMapper):
    def project_members(self):
        return [{'username' : 'admin', 'roles' : ['ProjectAdmin']}]

def cabochon_to_tt_middleware(app):

    def middleware(environ, start_response):

        if environ.get('AUTHENTICATION_METHOD') != 'WSSE':
            return app(environ, start_response)

        params = parse_formvars(environ)
        for param, value in params.items():
            params[param] = loads(value)
        environ['REMOTE_USER'] = 'admin'
        environ['topp.project_name'] = params['id']
        environ['topp.project_permission_level'] = 'closed_policy'
        environ['topp.user_info'] = {'roles' : ['ProjectAdmin']}
        environ['topp.project_members'] = CabochonUserMapper()
        
        return app(environ, start_response)        
    return middleware

def translate_environ_middleware(app, global_conf, app_conf):
    kw = dict()
    for key, val in app_conf.items():
        if key.startswith("translate_environ "):
            kw[key.split()[1]] = val
    def middleware(environ, start_response):
        for name, value in kw.items():
            if value in environ:
                environ[name] = environ[value]
        return app(environ, start_response)
    return middleware

def fill_environ_middleware(app, global_conf, app_conf):
    kw = dict()
    for key, val in app_conf.items():
        if key.startswith("fill_environ "):
            kw[key.split()[1]] = val
    def middleware(environ, start_response):
        for name, value in kw.items():
            if name not in environ:
                environ[name] = value
        return app(environ, start_response)
    return middleware

def make_app(global_conf, **app_conf):
    """Create a WSGI application and return it
    
    global_conf is a dict representing the Paste configuration options, the
    paste.deploy.converters should be used when parsing Paste config options
    to ensure they're treated properly.
    
    """
    # Load our Pylons configuration defaults
    from tasktracker.config.environment import load_environment    
    load_environment(global_conf, app_conf)

    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp()
    app = ConfigMiddleware(app, {'app_conf':app_conf,
        'global_conf':global_conf})

    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath

    app = SupervisorErrorMiddleware(app)

    # @@@ Change HTTPExceptions to HTTP responses @@@
    app = httpexceptions.make_middleware(app, global_conf)
    
    # @@@ Error Handling @@@
    app = ErrorHandler(app, global_conf, error_template=error_template, **config['pylons.errorware'])
    
    # @@@ Static Files in public directory @@@
    static_app = StaticURLParser(config['pylons.paths']['static_files'])

    # @@@ WebHelper's static javascript files @@@
    javascripts_app = StaticJavascripts()
    
    # @@@ Cascade @@@ 
    app = Cascade([static_app, javascripts_app, app])
    
    # @@@ Display error documents for 401, 403, 404 status codes (if debug is disabled also
    # intercepts 500) @@@
    app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
    
    # @@@ Establish the Registry for this application @@@
    app = RegistryManager(app)

    app = cabochon_to_tt_middleware(app)

    try:
        openplans_wrapper = app_conf['openplans_wrapper']
    except KeyError:
        raise ValueError('No openplans_wrapper specified in [app:tasktracker] configuration')
    openplans_wrapper = load_object(openplans_wrapper)
    app = openplans_wrapper(app, app_conf)

    #handle cabochon messages
    login_file = app_conf.get('cabochon_password_file')

    if login_file:
        username, password = file(login_file).read().strip().split(":")

        if username:
            app = WSSEAuthMiddleware(app, {username : password}, required=False)    

    app = translate_environ_middleware(app, global_conf, app_conf)
    app = fill_environ_middleware(app, global_conf, app_conf)
    return app
