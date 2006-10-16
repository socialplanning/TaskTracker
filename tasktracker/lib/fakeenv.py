class User:
    def __init__(self, username, address):
        self.username = username
        user, domain = address.split("@")
        self.email_address = "%s+%s@%s" % (user, username, domain)

class UserMapper:
    def __init__(self, address):
        self.address = address

    def __call__(self, username):
        return User(username, self.address)

class ZWSGIFakeEnv(object):
    def __init__(self, app, users, test_email_address):
        self.app = app
        self.users = users
        self.test_email_address = test_email_address

    def authenticate (self, environ):
        try:
            basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
            if basic != "Basic": return False
            username, password = encoded.decode("base64").split(":")
            
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




