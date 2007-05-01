
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
from pylons import c
from paste import httpexceptions

def _user_dict(name):
    if name == "admin":
        roles = "Authenticated ProjectMember ProjectAdmin".split()
    elif name == "auth":
        roles = ["Authenticated"]
    elif name == "":
        roles = ["Anonymous"]
    else:
        roles = "Authenticated ProjectMember".split()
    return dict(username = name,
                email = "%s@topp.example.com" % name, 
                roles = roles,
                )

from tasktracker.lib import usermapper
class UserMapper(usermapper.UserMapper):
    """
    admin: ProjectAdmin of every project
    member: ProjectMember of every project
    auth: Authenticated sitewide, nonmember
    [emptystring]: Anonymous user
    """
    def project_members(self):
        # @@ let's make this usable somehow
        names = 'admin,member,auth'.split(',')
        names.extend([''])
        members = map(_user_dict, names)
        return members

class TestingEnv(object):
    def __init__(self, app, users):
        self.app = app
        self.users = users
        
    def authenticate(self, environ):
        try:
            basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
            if basic != "Basic": return False
            username, password = encoded.decode("base64").split(":")
            password = password.encode("base64")
            environ['REMOTE_USER'] = username
            environ['topp.user_info'] = _user_dict(username)

            return True

        except KeyError:
            return False            

    def memberlist(self, project):
        return self.users.keys()

    def __call__(self, environ, start_response):

        environ['topp.memberlist'] = self.memberlist
        environ['topp.project_members'] = UserMapper()
        environ['topp.project_name'] = environ.get("HTTP_X_OPENPLANS_PROJECT", 'theproject')
        environ['topp.project_permission_level'] = environ.get("HTTP_X_OPENPLANS_TTPOLICY", 'open_policy')

        if not self.authenticate(environ):
            status = "401 Authorization Required"
            headers = [('Content-type', 'text/plain'), ('WWW-Authenticate', 'Basic realm="www"')]
            start_response(status, headers)
            return []
        else:
            return self.app(environ, start_response)
