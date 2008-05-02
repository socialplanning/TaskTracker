# Copyright (C) 2006-2007 The Open Planning Project

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

from paste.wsgilib import intercept_output
from paste.request import construct_url

from urllib import quote, unquote, urlencode

from cookieauth import UserMapper, get_secret, get_info_for_project, get_users_for_project, ProjectNotFoundError

from signedheaders import HeaderSignatureCheckingMiddleware

from tasktracker.lib import urireader 

class _SignedHeaderAuth(object):
    def __init__(self, app, app_conf):
        self.app = app
        self.openplans_instance = urireader.get_openplans_instance(app_conf)
        self.login_uri = urireader.get_login_uri(app_conf)
        self.homepage_uri = urireader.get_homepage_uri(app_conf)
        self.profile_uri = urireader.get_profile_uri(app_conf)

        if self.profile_uri.count('%s') != 1:
            raise Exception("Badly formatted profile_uri: must include a single '%s'")

        admin_file = app_conf['topp_admin_info_filename']
        self.admin_info = tuple(file(admin_file).read().strip().split(":"))
        if len(self.admin_info) != 2:
            raise Exception("Bad format in administrator info file")

    def authenticate(self, environ):
        username = environ.get('REMOTE_USER') 
        if username:
            environ['topp.user_info'] = dict(username = username, 
                                             roles = ['Authenticated'],
                                             email = '%s@example.com' % username)
            return True
        
    def needs_redirection(self, status, headers):
        return status.startswith('401') or status.startswith('403')

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].strip("/").startswith("_debug"):
            return self.app(environ, start_response)
        
	username = ''
        environ['topp.user_info'] = dict(username = '', roles = ['Anonymous'], email = 'null@example.com')
	try:
	    authenticated = self.authenticate(environ)
        except BadCookieError:
            status = "401 Unauthorized"
            start_response(status, [])
            return ["Please delete your brower's cookies and login again."]

        if authenticated:
            username = environ['REMOTE_USER']

        if 'topp.project_name' in environ:
            project_name = environ['topp.project_name']

            environ['topp.project_members'] = umapper = UserMapper(environ, project_name,
                                                                   self.openplans_instance,
                                                                   self.admin_info, self.profile_uri)
            if username in umapper.project_member_names():
                environ['topp.user_info']['roles'].extend(umapper.project_member_roles(username))

            try:
                info = get_info_for_project(project_name, self.openplans_instance, self.admin_info)
                environ['topp.project_permission_level'] = info['policy']
                environ['topp.app_installed'] = info['installed']
            except ProjectNotFoundError: #assume the most restrictive
                environ['topp.project_permission_level'] = dict(policy='closed_policy')
                environ['topp.app_installed'] = True # this should prob be false, but i don't want to change behavior

        status, headers, body = intercept_output(environ, self.app, self.needs_redirection, start_response)

        if status:
            if status.startswith('401'):
                status = "303 See Other"
                url = construct_url(environ)
                headers = [('Location', '%s?came_from=%s' % (self.login_uri, quote(url)))]
                start_response(status, headers)
                return []
            elif status.startswith('403'):
                status = "303 See Other"
                url = construct_url(environ)
                headers = [('Location', '%s?portal_status_message=You+have+insufficient+privileges.' % self.homepage_uri)]
                start_response(status, headers)
            return []        
        else:
            return body

def SignedHeaderAuth(app, app_conf):
    app = _SignedHeaderAuth(app, app_conf)
    secret = get_secret(app_conf)
    return HeaderSignatureCheckingMiddleware(app, secret)

def make_cookie(username):
    from pylons import config
    secret = get_secret(config['app_conf'])
    auth = hmac.new(secret, username, sha).hexdigest()
    cookie = quote(("%s\0%s" % (username, auth)).encode("base64")).strip()
    return ('__ac', cookie)
