
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

from tasktracker.config.environment import load_environment

from tasktracker.lib.testing_env import TestingEnv
from tasktracker.lib.cookieauth import CookieAuth

import tasktracker.lib.app_globals as app_globals
import tasktracker.lib.helpers

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
    config = load_environment()
    config.init_app(global_conf, app_conf, package='tasktracker')

    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp(config, 
	helpers=tasktracker.lib.helpers,
	g=app_globals.Globals)
    g = app.globals
    g.config = config
    app = ConfigMiddleware(app, {'app_conf':app_conf,
        'global_conf':global_conf})
    
    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath

    # @@@ Change HTTPExceptions to HTTP responses @@@
    app = httpexceptions.make_middleware(app, global_conf)
    
    # @@@ Error Handling @@@
    app = ErrorHandler(app, global_conf, error_template=error_template, **config.errorware)
    
    # @@@ Static Files in public directory @@@
    static_app = StaticURLParser(config.paths['static_files'])

    # @@@ WebHelper's static javascript files @@@
    javascripts_app = StaticJavascripts()
    
    # @@@ Cascade @@@ 
    app = Cascade([static_app, javascripts_app, app])
    
    # @@@ Display error documents for 401, 403, 404 status codes (if debug is disabled also
    # intercepts 500) @@@
    #app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)
    
    # @@@ Establish the Registry for this application @@@
    app = RegistryManager(app)

    if config.app_conf.get('openplans_wrapper') == 'TestingEnv':
        users = {'anon' : 'Anonymous',
                 'auth' : 'Authenticated',
                 'member' : 'ProjectMember',
                 'contentmanager' : 'ProjectContentManager',
                 'admin' : 'ProjectAdmin'
                 }
        
        app = TestingEnv(app, users)
        
    elif config.app_conf.get('openplans_wrapper') == 'CookieAuth':
        app = CookieAuth(app, app_conf)

    else:
        if not config.app_conf.get('openplans_wrapper'):
            raise ValueError(
                "openplans_wrapper not set")
        else:
            raise ValueError(
                "openplans_wrapper value not recognized (%r)" % config.app_conf.get('openplans_wrapper'))

    app = translate_environ_middleware(app, global_conf, app_conf)
    app = fill_environ_middleware(app, global_conf, app_conf)

    return app
