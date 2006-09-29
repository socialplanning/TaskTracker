class ZWSGIFakeEnv(object):
    def __init__(self, app, users):
        self.app = app
        self.users = users

    def authenticate (self, environ):
        try:
            basic, encoded = environ['HTTP_AUTHORIZATION'].split(" ")
            if basic != "Basic": return False
            username, password = encoded.decode("base64").split(":")
            
            if self.users.has_key(username):
                environ['topp.username'] = username
                environ['topp.project'] = 'theproject'
                environ['topp.role'] = self.users[username]
            else:
                return False

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




