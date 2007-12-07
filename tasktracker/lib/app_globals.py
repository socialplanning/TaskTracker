
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


from ConfigParser import ConfigParser

from eventserver import DummyEventServer, init_events
from threading import Thread

from pylons import config

class Globals(object):

    def __init__(self, setup_config=False):
        self.obsolete_future_history_dir = config['obsolete_future_history_dir']

        if config.get('event_queue_directory', None):
            from cabochonclient import CabochonClient

            base_conf = ConfigParser()
            base_conf.read(config['base_config'])
            cab_url = base_conf.get('applications', 'cabochon uri')

            cabochon_user_info = base_conf.get('general', 'cabochon_user_info')
            f = open(cabochon_user_info)
            username, password = f.readline().split(':')

            self.event_server = CabochonClient(config['event_queue_directory'], cab_url, username=username, password=password)
            if not setup_config:
                if not self.event_server.test_login():
                    print "Bad Cabochon login information"
                    import sys
                    sys.exit(0)

                sender = self.event_server.sender()
                t = Thread(target=sender.send_forever)
                t.setDaemon(True)
                t.start()    
        else:
            #print "WARNING, no Cabochon", config
            self.event_server = DummyEventServer()
            
        self.queues = dict(create=self.event_server.queue("create_page"),
                           edit=self.event_server.queue("edit_page"),
                           delete=self.event_server.queue("delete_page"))
        self.events = {}

        init_events()

    def __del__(self):
        """
        Put any cleanup code to be run when the application finally exits 
        here.
        """
        if hasattr(self, 'store'):
            self.store.running = False
