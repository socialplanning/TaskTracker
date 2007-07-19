
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


from eventserver import DummyEventServer, init_events
from threading import Thread


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
        self.obsolete_future_history_dir = app_conf['obsolete_future_history_dir']

        if app_conf.get('event_queue_directory', None):
            from cabochonclient import CabochonClient            
            self.event_server = CabochonClient(app_conf['event_queue_directory'], app_conf['event_server'])
            sender = self.event_server.sender()
            t = Thread(target=sender.send_forever)
            t.setDaemon(True)
            t.start()    
        else:
            print "WARNING, no Cabochon", app_conf
            self.event_server = DummyEventServer()
            
        self.queues = dict(create=self.event_server.queue("create_page"),
                           edit=self.event_server.queue("edit_page"))
        self.events = {}

        init_events()

    def __del__(self):
        """
        Put any cleanup code to be run when the application finally exits 
        here.
        """
        if hasattr(self, 'store'):
            self.store.running = False
