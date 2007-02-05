
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

from paste.wsgilib import intercept_output

import os
import base64

import hmac
import sha

from urllib import quote, unquote
from Cookie import BaseCookie

conf_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def _user_dict(name):
    return dict(username = name,
                email = "%s@topp.example.com" % name, 
                roles = 'Authenticated ProjectMember'.split(),
                )


secret = ""

def get_secret():
    global secret
    if not secret:
        secret_file_name = os.environ.get('TOPP_SECRET_FILENAME', '')
        assert secret_file_name

        f = open (secret_file_name)
        secret = f.readline().strip()
        f.close()
    return secret


from cache import get_cached
from project_members import *

def project_policy(*args):
    info = get_info_for_project(*args)
    return info['policy']

class UserMapper:
    def __init__(self, environ, project, server):
        self.project = project
        self.server = server
        self.environ = environ

    def project_members(self):
        return get_cached(self.environ, 'project_users', key=self.project, default_func=get_users_for_project, default_args=[self.project, self.server])



class CookieAuth(object):
    def __init__(self, app, openplans_instance):
        self.app = app
        self.conf = appconfig('config:development.ini', relative_to=conf_dir)
        CONFIG.push_process_config({'app_conf': self.conf.local_conf,
                                    'global_conf': self.conf.global_conf})

        self.openplans_instance = openplans_instance

    def authenticate (self, environ):
        try:
            #authenticate cookie
            
            cookie = BaseCookie(environ['HTTP_COOKIE'])
            morsel = cookie['__ac']

            username, auth = base64.decodestring(unquote(morsel.value)).split("\0")
            secret = get_secret()
            if not auth == hmac.new(secret, username, sha).hexdigest():
                return False


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
        

    def needs_redirection(self, status, headers):
        return status.startswith('403')

    def __call__(self, environ, start_response):

        self.authenticate(environ)

        project_name = 'p1'
        environ['topp.project_name'] = project_name
        environ['topp.project_members'] = UserMapper(environ, project_name, self.openplans_instance)
        environ['topp.project_permission_level'] = get_cached(environ, 'project_info', 
                                                              key=project_name, 
                                                              default_func=project_policy, default_args=[project_name, self.openplans_instance])

        status, headers, body = intercept_output(environ, self.app, self.needs_redirection, start_response)        

        if status:
            status = "303 See Other"
            url = 'http://%s%s' % (environ['HTTP_HOST'], environ['PATH_INFO'])
            headers = [('Location', '%s/login_form?came_from=%s' % (self.openplans_instance, quote(url)))]
            start_response(status, headers)
            return []
        else:
            return body

