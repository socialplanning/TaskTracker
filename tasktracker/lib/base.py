
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

#fixme: uncomment next line, remove line after, and remove section
#below when paste includes non-exception redirect_to 

#from pylons import Request, c, g, cache, request, session
from pylons import c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, rest, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from tasktracker.models import *
from tasktracker.controllers import *
from tasktracker.lib.watchers import *
from paste.deploy.converters import asbool
from paste.deploy.config import CONFIG
#import tasktracker.lib.helpers as h

from threading import local

#remove this bit when paste includes non-exception redirect_to
from paste.wsgiwrappers import WSGIResponse
from routes import url_for
class Response(WSGIResponse):
    @classmethod
    def redirect_to(cls, *args, **params):
        if len(args) == 0:
            url = url_for(**params)
        elif len(args) == 1:
            url = args[0]
        else:
            raise TypeError("redirect_to() takes at most 1 positional argument (%s given)" % len(args))
        rparams = {}
        rparams['code'] = params.get('code', 303)

        resp = WSGIResponse(code=rparams['code'], content="You are now being redirected to <a href=\"%s\">%s</a>.  Do not be alarmed." % (url, url))
        resp.headers['Location'] = url
        return resp

class NoSuchIdError(Exception):
    pass

class MissingArgumentError(Exception):
    pass

class NotInitializedException(Exception):
    pass

def catches_errors(f):
    def new_f(*args, **kwds):
        try:
            edited_kwds = dict(kwds)
            edited_kwds.pop('action', None)
            edited_kwds.pop('controller', None)
            return f(*args, **edited_kwds)
        except NoSuchIdError, exception:
            c.error = "No such task: %s" % exception.args
            return render_response('error')
        except MissingArgumentError, exception:
            c.error = "A required argument was not provided: %s" % exception.args
            return render_response('error')
        
    new_f.func_name = f.func_name
    return new_f

from tasktracker.lib.secure_forms import authenticate

def attrs(**kwds):
    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])
        return f
    return decorate

def render_text(text, **args):
    resp = Response(**args)
    resp.content_type = "text/plain"
    resp.content = [text]
    return resp 

class SecurityException(Exception):
    pass

class MissingSecurityException(Exception):
    pass

def _getRole(environ):
    if not environ.get('REMOTE_USER', None):
        return 'Anonymous'
    userRoles = set(environ['topp.user_info']['roles'])
    interestingRoles = ['ProjectMember', 'ProjectAdmin']
    best = 'Authenticated' #if we get this far, we're authenticated
    for role in interestingRoles:
        if role in userRoles:
            best = role

    return best

class BaseController(WSGIController):
    def __before__(self, action, **params):
        project = Project.getProject(request.environ['topp.project_name'])
        c.project = project
        c.id = params.get('id')
        c.compress_resources = asbool(CONFIG['app_conf'].get('compress_resources'))
        c.permission_cache = {}
        c.action_names = {}

        c.username = request.environ.get('REMOTE_USER', '')
        params['username'] = c.username

        func = getattr(self, action)
        restrict_remote_addr = getattr(func, 'restrict_remote_addr', False)
        if restrict_remote_addr:
            if request.environ['REMOTE_ADDR'] != '127.0.0.1':
                redirect_to(controller='error', action='document', message='Not permitted') # @@ ugh -egj

        if not self._authorize(project, action, params):
            if not c.username:
                #no username *and* needs more permissions -- maybe a login will help
                abort(403, 'Login required')
            else:
                #they're logged in but still don't have the necessary permissions
                redirect_to(controller='error', action='document', message='Not permitted') # @@ ugh -egj

        func = getattr(self, action)
        dog = getattr(func, 'watchdog', None)
        self.watchdog = local()

        if dog:
            self.watchdog.dog = dog()
            self.watchdog.dog.before(params)
            self.watchdog.action = action
        else:
            self.watchdog.dog = None

    def __after__(self, action, **params):
        if self.watchdog.dog:
            if self.watchdog.action == request.environ['pylons.routes_dict']['action']:
                self.watchdog.dog.after(params)

    @classmethod
    def _has_permission(cls, controller, action_verb, params):
        if callable(action_verb):
            action_verb = action_verb(params)

        action_name = controller + '_' + action_verb

        id = params.get('id')
        if not id:
            id = params.get('task_listID')
        key = (controller, id)
        if action_name != 'tasklist_create':
            permissions = c.permission_cache.get(key)
            if permissions:
                return action_name in permissions

        #special case for creating task lists
        if action_name == 'tasklist_create':
            if c.project_permission_level in ['open_policy', 'medium_policy']:
                return c.level <= Role.getLevel('ProjectMember')
            else:
                return c.level <= Role.getLevel('ProjectAdmin')

        if controller == 'tasklist':
            task_list = TaskList.get(params['id'])
        elif controller == 'task':
            if action_name == 'task_create':
                controller = 'tasklist'
                task_list = TaskList.get(params['task_listID'])
            else:
                task = Task.get(int(params['id'])) 
                task_list = task.task_list
        elif controller == 'project':
            # special case for lock/unlocking project's tt
            if action_verb == 'lock':
                return Role.getLevel('ProjectAdmin') >= c.level
        else:
            task_list = "I AM BROKEN"
            print "unknown controller %s" % controller
            return False

        local_level = c.level

        if c.level > Role.getLevel('ListOwner'):
            if task_list.isOwnedBy(params['username']):
                local_level = Role.getLevel('ListOwner')

        #special case for private tasks
        if controller == 'task':
            if task.private:
                if local_level > Role.getLevel('ListOwner') and not task.isOwnedBy(params['username']):
                    c.permission_cache[key] = set()
                    return False

        if controller == 'task' and local_level > Role.getLevel('TaskOwner'):
            if task.isOwnedBy(params['username']):
                local_level = Role.getLevel('TaskOwner')
        
        tl_permissions = TaskListPermission.select(AND(TaskListPermission.q.task_listID == task_list.id, TaskListPermission.q.min_level >= local_level))

        permissions = set((p.actionName() for p in tl_permissions))

        c.permission_cache[key] = permissions

        return action_name in permissions

    def _initialize_project(self, controller, action_verb, params):
        """
        Check for authorization relating to project initialization.
        Return true if authorization definitively succeeds at this step
        Return false if authorization needs to continue
        If authorization fails at this step, raise an exception or redirect.
        """

        if callable(action_verb):  #TODO: this isn't a good solution!
            return True
        
        action_name = controller + '_' + action_verb
        if action_name == 'project_initialize':
            if c.level <= Role.getLevel('ProjectAdmin'):
                return True #OK, let admins initialize the project.
            else:
                raise NotInitializedException
        elif action_name == 'project_show_uninitialized':
            return True

        if c.project.initialized:
            return False

        redirect_to(controller='project', action='show_uninitialized', id = c.project.id) # @@ ugh -egj
        
    def _authorize(self, project, action, params):
        controller = params['controller']
        if controller == 'error':
            return True
        environ = request.environ

        role_name = _getRole(environ)
        role = Role.selectBy(name=role_name)
        if not role.count():
            raise Exception("No such role %s" % role_name)
        c.level = role[0].level

        c.user_info = environ.get('topp.user_info', None)
        c.project_permission_level = environ.get('topp.project_permission_level', None)

        if c.project_permission_level == 'closed_policy':
            if not c.username:
                return False

        c.usermapper = environ['topp.project_members']

        func = getattr(self, action)
        if not getattr(func, 'action', None):
            raise MissingSecurityException("Programmer forgot to give the action attribute to the function '%s' in the controller '%s'" % 
                                           (action, controller))
        action_verb = func.action

        # if project is initializable by current user or we're displaying show_uninitialized msg, we're authorized
        # if function returns false, the project IS initialized, so we have to continue checking auth.
        #        if action_verb in ("initialize","show_uninitialized") or \
            #if "initialization_not_required" not in params['environ']:
        if self._initialize_project(controller, action_verb, params):
            return True            

        if project.readonly:
            only_reads = getattr(func, 'readonly', False)
            if not only_reads:
                return False  # or maybe a ReadOnlyException or something?

        #methods can override controllers (but should do so rarely)
        controller = getattr(func, 'controller', controller)
        
        #A few special cases follow, with the general permission case at the end.

        if callable(action_verb):  #TODO: this isn't a good solution!
            return True

        if action_verb == 'open':
            return True

        if action_verb == 'loggedin':
            if not c.username:
                abort(403, 'Forbidden')
            else:
                return True

        if action == 'auto_complete_for':
            return True

        params = dict(params)
        params.update(request.params)
        return self._has_permission(controller, action_verb, params)


    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)


