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
    def __init__(self, app, users, test_email_address, config=None):
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
            
            environ['topp.usermapper'] = UserMapper(self.test_email_address)
            environ['topp.project'] = 'theproject'
            if self.users.has_key(username):
                environ['topp.username'] = username
                environ['topp.project'] = 'theproject'
                environ['topp.role'] = self.users[username]
            else:
                environ['topp.username'] = username
                environ['topp.role'] = 'ProjectMember'

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




