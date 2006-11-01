
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

class UserFoo:
    def __init__(self, username, address):
        self.username = username
        user, domain = address.split("@")
        self.email_address = "%s+%s@%s" % (user, username, domain)

class UserMapper:
    def __init__(self, address):
        self.address = address

    def __call__(self, username):
        return UserFoo(username, self.address)

class ZWSGIFakeEnv(object):
    def __init__(self, app, users, test_email_address):
        self.app = app
        self.users = users
        self.test_email_address = test_email_address
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

            environ['topp.project_members'] = UserMapper(self.test_email_address)
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




