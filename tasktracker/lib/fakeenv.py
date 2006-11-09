
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

from tasktracker.models import *
from paste.deploy import CONFIG, appconfig
from pylons import c

import os, sys
conf_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _user_dict(name):
    return dict(username = name,
                email = "%s@topp.example.com" % name, 
                roles=('Authenticated, ProjectMember'),
                )

class UserMapper:
    def project_members(self):
        names = 'admin, listowner, member, auth, Fred, George, Kate, Larry, Curly, Moe, Raven, Buffy, Sal, Thomas, Tanaka, Nobu, Hargattai, Mowbray, Sinbad, Louis, Matthew, Dev, egj, dcrosta, shamoon, novalis, ltucker, magicbronson, jarasi, cholmes'.split(', ')
        return map (_user_dict, names)

class ZWSGIFakeEnv(object):
    def __init__(self, app, users):
        self.app = app
        self.users = users
        self.conf = appconfig('config:development.ini', relative_to=conf_dir)
        CONFIG.push_process_config({'app_conf': self.conf.local_conf,
                                    'global_conf': self.conf.global_conf})

    def authenticate (self, environ):
        try:
            basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
            if basic != "Basic": return False
            username, password = encoded.decode("base64").split(":")
            password = password.encode("base64")

            try:
                userquery = User.selectBy(username=username)[0]
                if password != userquery.password:
                    return False
            except IndexError:
                return False

            environ['topp.project_members'] = UserMapper()
            environ['topp.project_name'] = 'theproject'

            environ['REMOTE_USER'] = username

            environ['topp.user_info'] = dict(username = username, 
                                             roles = ['ProjectMember'],
                                             email = '%s@example.com' % username)

            #these are needed for tests
            if username == 'admin':
                environ['topp.user_info']['roles'] = ['ProjectAdmin']
            if username == 'auth':
                environ['topp.user_info']['roles'] = ['Authenticated']

            return True

        except KeyError:
            return False            

    def memberlist(self, project):
        return self.users.keys()

    def __call__(self, environ, start_response):

        environ['topp.memberlist'] = self.memberlist

        if self.authenticate(environ):
            return self.app(environ, start_response)
        else:
            status = "401 Authorization Required"
            headers = [('Content-type', 'text/plain'), ('WWW-Authenticate', 'Basic realm="www"')]
            start_response(status, headers)
            return []




