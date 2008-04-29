
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

from pylons import c
from paste import httpexceptions
from tasktracker.lib import usermapper

def _user_dict(name):
    if name == "admin":
        roles = "Authenticated ProjectMember ProjectAdmin".split()
    elif name == "auth":
        roles = ["Authenticated"]
    elif name == "anon":
        roles = ["Anonymous"]
        name = ''
    else:
        roles = "Authenticated ProjectMember".split()
    return dict(username = name,
                email = "%s@topp.example.com" % name, 
                roles = roles,
                )


class UserMapper(usermapper.UserMapper):
    """
    admin: ProjectAdmin of every project
    member: ProjectMember of every project
    auth: Authenticated sitewide, nonmember
    anon: Anonymous user
    """
    def project_members(self):
        # @@ let's make this usable somehow
        names = 'admin,member,darcy,novalis,porkfiend,hagrid,katya'.split(',')
        members = map(_user_dict, names)
        return members

class TestingEnv(object):
    users = {'anon' : 'Anonymous',
             'auth' : 'Authenticated',
             'member' : 'ProjectMember',
             'contentmanager' : 'ProjectContentManager',
             'admin' : 'ProjectAdmin'
             }
    
    def __init__(self, app, app_config_UNUSED):
        # @@ the unused app_config parameter is present only to match the
        # API of other openplans_wrapper wsgi applications.
        self.app = app
        
    def authenticate(self, environ):
        username = environ.get('REMOTE_USER')
        if username:
            return True
        
        try:
            basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
            if basic != "Basic": return False
            username, password = encoded.decode("base64").split(":")
            environ['REMOTE_USER'] = username
            if username == 'anon':
                environ['REMOTE_USER'] = ''
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
        environ['topp.project_permission_level'] = environ.get("openplans_ttpolicy", 'open_policy')
        environ['topp.app_installed'] = True

        environ['REMOTE_ADDR'] = '127.0.0.1'
        if not self.authenticate(environ):
            status = "401 Authorization Required"
            headers = [('Content-type', 'text/plain'), ('WWW-Authenticate', 'Basic realm="www"')]
            start_response(status, headers)
            return []
        else:
            return self.app(environ, start_response)
