
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
from pylons.helpers import redirect_to

from paste.wsgilib import intercept_output

import os, sys
import base64

import hmac
import sha

from urllib import unquote
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


class UserMapper:
    def project_members(self):
        names = 'admin, listowner, member, auth, Fred, George, Kate, Larry, Curly, Moe, Raven, Buffy, Sal, Thomas, Tanaka, Nobu, Hargattai, Mowbray, Sinbad, Louis, Matthew, Dev, egj, dcrosta, shamoon, novalis, ltucker, magicbronson, jarasi, cholmes'.split(', ')
        members = map (_user_dict, names)
        for member in members:
            if member['username'] == 'admin':
                member['roles'].append('ProjectAdmin')
        return members

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

            username, password, auth = base64.decodestring(unquote(morsel.value)).split("\0")
            secret = get_secret()
            if not auth == hmac.new(secret, username + password, sha).hexdigest():
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
            if username == 'anon':
                environ['topp.user_info']['roles'] = ['Anonymous']

            return True

        except KeyError:
            return False            
        

    def needs_redirection(self, status, headers):
        return status.startswith('403')

    def __call__(self, environ, start_response):

        self.authenticate(environ)

        environ['topp.project_name'] = 'theproject'
        environ['topp.project_members'] = UserMapper()
        environ['topp.project_permission_level'] = 'closed'

        status, headers, body = intercept_output(environ, self.app, self.needs_redirection, start_response)        

        if status:
            status = "303 See Other"
            url = 'http://%s/%s' % (environ['HTTP_HOST'], environ['PATH_INFO'])
            headers = [('Location', '%slogin_form?came_from=%s' % (self.openplans_instance, url))]
            start_response(status, headers)
            return []
        else:
            return body


        #if self.authenticate(environ):
        #    return 
        #else:
        #    status = "303 See Other"
        #    url = 'http://%s/%s' % (environ['HTTP_HOST'], environ['PATH_INFO'])
        #    headers = [('Location', '%slogin_form?came_from=%s' % (self.openplans_instance, url))]
        #    start_response(status, headers)
        #    return []


