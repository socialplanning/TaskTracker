
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

import imp
from pylons import c

def require(*libs):
    for lib in libs:
        #attempt to load module
        module = imp.load_module(lib, *imp.find_module(lib))        


class Globals(object):

    def __init__(self, global_conf, app_conf, **extra):
        """
        You can put any objects which need to be initialised only once
        here as class attributes and they will be available as globals
        everywhere in your application and will be intialised only once,
        not on every request.
        
        ``global_conf``
            The same as variable used throughout ``config/middleware.py``
            namely, the variables from the ``[DEFAULT]`` section of the
            configuration file.
            
        ``app_conf``
            The same as the ``kw`` dictionary used throughout 
            ``config/middleware.py`` namely, the variables the section 
            in the config file for your application.
            
        ``extra``
            The configuration returned from ``load_config`` in 
            ``config/middleware.py`` which may be of use in the setup of 
            your global variables.
            
        """
        self.events = {}
        if app_conf.get('atom_store_link', None):
            from tasktracker.lib.store_notes import AtomStoreLink
            from tasktracker.config.notify import setup_notify
            require('atomixlib', 'httplib2')
            url = app_conf['atom_store_link']
            if url == 'self':
                #start an atom server
                from atomstore.atomstore import start_store
                self.store = start_store()
                url = "http://localhost:8080"
                import time
                time.sleep(1)
            self.atom_store_link = AtomStoreLink(url)
            setup_notify(self.events)

    def __del__(self):
        """
        Put any cleanup code to be run when the application finally exits 
        here.
        """
        if hasattr(self, 'store'):
            self.store.running = False

    def valid(self, environ, username, password):
        print "OK"
        from tasktracker.models import User
        if not username:
            print "No username provided"
            username = environ.get('REMOTE_USER', 'anonymous')
            c.username = username
            return False
        try: 
            user = User.selectBy(username=username)[0]
            if user.password == password.encode("base64"):
                print "Successfully logged in"
                environ['REMOTE_USER'] = username
                username = environ.get('REMOTE_USER', 'anonymous')
                c.username = username
                return True
            print "WRONG PW"
            username = environ.get('REMOTE_USER', 'anonymous')
            c.username = username
            return False
        except:
            print "No such user."
            username = environ.get('REMOTE_USER', 'anonymous')
            c.username = username
            return False
