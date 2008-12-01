
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
from pylons.controllers.util import abort, redirect_to, etag_cache
from tasktracker.models import *
from tasktracker.controllers import *
from paste.deploy.converters import asbool
from paste.deploy.config import CONFIG
import sqlobject
from paste import httpexceptions
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

def safe_get(so_class, id, check_live=False):
    """
    Gets the object by the given ID.  If not found, raises HTTPNotFound *if*
    there is no HTTP Referer (if there is, lets the exception raise)
    
    Also, if the resulting instance has a .project attribute, and c.project is
    defined, then check that they match
    """
    not_live = False
    not_project = False
    if id is None:
        ### we use pylons.helpers.redirect_to here
        ### because we need to raise an exception
        redirect_to('home')
    try:
        id = int(id)
    except (ValueError, TypeError):
        raise httpexceptions.HTTPBadRequest(
            "The id %r is not a valid number" % id)
    try:
        obj = so_class.get(id)
        if (hasattr(obj, 'project')
            and hasattr(c, 'project')):
            not_project = True
            assert obj.project == c.project, (
                "Tried to fetch object %r which is from project %r, but we are "
                "in project %r" % (obj, obj.project, c.project))
        if check_live:
            not_live = True
            assert obj.live, (
                "The object %r is not live" % obj)
        return obj
    except (sqlobject.SQLObjectNotFound, AssertionError):
        if request.environ.get('HTTP_REFERER'):
            raise
        if not_live:
            msg = "This resource by the ID %s has been deleted" % id
        else:
            msg = "The %s by the ID %s does not exist" % (so_class.__name__, id)
        raise httpexceptions.HTTPNotFound(msg)

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
        try:
            project = Project.getProject(request.environ['topp.project_name'])
        except KeyError:
            abort(404, 'Not Found')
        c.project = project
        c.id = params.get('id')
        c.compress_resources = asbool(CONFIG['app_conf'].get('compress_resources'))
        c.permission_cache = {}
        c.action_names = {}

        c.username = request.environ.get('REMOTE_USER', '')

        params['username'] = c.username

        try:
            func = getattr(self, action)
        except AttributeError:
            abort(404, 'Not Found')
        restrict_remote_addr = getattr(func, 'restrict_remote_addr', False)
        if restrict_remote_addr:
            if request.environ['REMOTE_ADDR'] != '127.0.0.1':
                redirect_to(controller='error', action='document', message='Not permitted') # @@ ugh -egj - make it a 404

        if action == "show_authenticate":
            return True

        if not self._authorize(project, action, params):
            if not c.username:
                #no username *and* needs more permissions -- maybe a login will help
                abort(401, 'Login required')
            else:
                #they're logged in but still don't have the necessary permissions
                raise httpexceptions.HTTPForbidden("Access denied")

    def preload_permission_cache(self, tasklist):
        local_level = c.level

        if c.level > Role.getLevel('ListOwner'):
            if tasklist.isOwnedBy(c.username):
                local_level = Role.getLevel('ListOwner')

        #general permissions
        tl_permissions = TaskListPermission.select(AND(TaskListPermission.q.task_listID == tasklist.id, TaskListPermission.q.min_level >= local_level))
        permissions = set((p.actionName() for p in tl_permissions))

        for task in tasklist.tasks:
            key = ('task', task.id)
            extra_permissions = set()
            if local_level > Role.getLevel('TaskOwner') and 'task_show' in permissions and task.isOwnedBy(c.username):
                extra_permissions = set(['task_comment', 'task_change_status'])

            c.permission_cache[key] = permissions.union(extra_permissions)


    @classmethod
    def _zope_allows(cls, action_name, username, id):
        if c.project_permission_level == 'open_policy':
            return True
        elif c.project_permission_level == 'medium_policy':
            if action_name in ['task_show', 'tasklist_show']:
                return True
            if c.username in c.usermapper.project_member_names():
                return True
            if action_name == 'task_comment':
                return True
            if action_name == 'task_change_status':
                return safe_get(Task, id).isOwnedBy(username)
        elif c.project_permission_level == 'closed_policy':
            if c.username in c.usermapper.project_member_names():
                return True
        return False


    @classmethod
    def _has_permission(cls, controller, action_verb, params):

        if callable(action_verb):
            action_verb = action_verb(params)

        action_name = controller + '_' + action_verb
        id = params.get('id')
        if not id:
            id = params.get('task_listID')
        key = (controller, id)

        if not cls._zope_allows(action_name, params['username'], id):
            return False

        if action_name == 'tasklist_create':
            ### tasklist creation permissions are based entirely on the project permission level
            ### and conform to the text descriptions of security settings in opencore
            #if c.project_permission_level == 'open_policy':
            #    return c.level <= Role.getLevel('Authenticated')
            #else:

            # don't let project non-members create tasklists, ever!
            return c.level <= Role.getLevel('ProjectMember')
        
        permissions = c.permission_cache.get(key)
        if permissions:
            return action_name in permissions
        if controller == 'tasklist':
            task_list = safe_get(TaskList, params['id'])
        elif controller == 'task':
            if action_name == 'task_create':
                controller = 'tasklist'
                task_list = safe_get(TaskList, params['task_listID'])
            else:
                task = safe_get(Task, params['id'])
                task_list = task.task_list
        elif controller == 'project' or controller == 'migrate':
            return Role.getLevel('ProjectAdmin') >= c.level
        else:
            task_list = "I AM BROKEN"
            print "unknown controller %s" % controller
            return False

        local_level = c.level

        if c.level > Role.getLevel('ListOwner'):
            if task_list.isOwnedBy(params['username']):
                local_level = Role.getLevel('ListOwner')
      
        tl_permissions = TaskListPermission.select(AND(TaskListPermission.q.task_listID == task_list.id, TaskListPermission.q.min_level >= local_level))

        permissions = set((p.actionName() for p in tl_permissions))

        extra_permissions = set()
        if controller == 'task' and local_level > Role.getLevel('TaskOwner') and 'task_show' in permissions:
            if task.isOwnedBy(params['username']):
                extra_permissions = set(['task_comment', 'task_change_status'])

        permissions = permissions.union(extra_permissions)

        c.permission_cache[key] = permissions
        return action_name in permissions

    def _initialize_project(self, controller, action_verb, params):
        """
        Check for authorization relating to project initialization.
        Return true if authorization definitively succeeds at this step
        Return false if authorization needs to continue
        If authorization fails at this step, raise an exception or redirect.
        """

        ### if action_verb is callable, it has nothing to do with project initialization
        ### so authorization checks must continue
        if callable(action_verb):
            return False
        
        ### if we're initializing the project or displaying the uninitialized error message
        ### authorization can succeed or fail at this step
        action_name = controller + '_' + action_verb
        if action_name == 'project_initialize':
            if request.environ.get("HTTP_X_OPENPLANS_TASKTRACKER_INITIALIZE"):
                return True # let only admins initialize the project
            else:
                raise NotInitializedException
        elif action_name == 'project_show_uninitialized':
            return True

        #if the action is a project action, it doesn't matter if it's initialize
        if controller == 'project':
            return True

        ### if the project is already initialized, authorization procedures must continue
        if request.environ['topp.app_installed'] == True:
            return False

        ### the project is not initialized, so we redirect to the error message for uninitialized projects
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
        c.usermapper = environ['topp.project_members']

        func = getattr(self, action)
        if not getattr(func, 'action', None):
            raise MissingSecurityException("Programmer forgot to give the action attribute to the function '%s' in the controller '%s'" % 
                                           (action, controller))
        action_verb = func.action

        # if project is initializable by current user or we're displaying show_uninitialized msg, we're authorized
        # if function returns false, the project IS initialized, so we have to continue checking auth.
        if self._initialize_project(controller, action_verb, params):
            return True            

        # @@@ you know, readonly == GET, right? so there's some redundant information stored here
        ###   since routes is using a different procedure to check whether an action is GET-safe
        ###   (though i prefer this procedure since it's explicit)  -- egj
        if project.readonly:
            only_reads = getattr(func, 'readonly', False)
            if not only_reads:
                return False  # or maybe a ReadOnlyException or something?

        #methods can override controllers (but should do so rarely)
        controller = getattr(func, 'controller', controller)

        #A few special cases follow, with the general permission case at the end.

        if c.project_permission_level == 'closed_policy':
            if not c.username in c.usermapper.project_member_names():
                return False

        if action_verb == 'open':
            return True

        if action_verb == 'loggedin':
            if not c.username:
                abort(403, 'Forbidden')
            else:
                return True

        params = dict(params)
        params.update(request.params)

        return self._has_permission(controller, action_verb, params)


    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)


