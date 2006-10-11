from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, rest, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from tasktracker.models import *
from tasktracker.controllers import *
import tasktracker.lib.helpers as h


class NoSuchIdError(Exception):
    pass

class MissingArgumentError(Exception):
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
            return render_response('zpt', 'error')
        except MissingArgumentError, exception:
            c.error = "A required argument was not provided: %s" % exception.args
            return render_response('zpt', 'error')
        
    new_f.func_name = f.func_name
    return new_f

def attrs(**kwds):
    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])
        return f
    return decorate

def render_text(text):
    resp = Response()
    resp.content_type = "text/plain"
    resp.content = [text]
    return resp 

class SecurityException(Exception):
    pass

class NotInitializedException(Exception):
    pass

class MissingSecurityException(Exception):
    pass

class BaseController(WSGIController):

    def __before__(self, action, **params):
        project = Project.getProject(self._req.environ['topp.project'])
        c.project = project
        c.users = 'admin, listowner, member, auth, Fred, George, Kate, Larry, Curly, Moe, Raven, Buffy, Sal, Thomas, Tanaka, Nobu, Hargattai, Mowbray, Sinbad, Louis, Matthew, Dev'.split(', ')
        c.id = params.get('id')

        if not self._authorize(project, action, params):
            redirect_to(controller='project', action='show_not_permitted')
            #raise SecurityException("IMPROPER AUTHENTICATION")

    @classmethod
    def _has_permission(cls, controller, action_name, params):        
        #special case for creating task lists
        if action_name == 'tasklist_create':
            return c.project.create_list_permission >= c.level

        if controller == 'tasklist':
            task_list = TaskList.get(params['id'])
        elif controller == 'task':
            if action_name == 'task_create':
                controller = 'task_list'
                task_list = TaskList.get(params['task_listID'])
            else:
                try: 
                    task = Task.get(int(params['id']))
                except TypeError:
                    import pdb; pdb.set_trace()
                task_list = TaskList.get(task.task_listID)
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
                    return False

        if controller == 'task' and local_level > Role.getLevel('TaskOwner'):
            if task.isOwnedBy(params['username']):
                local_level = Role.getLevel('TaskOwner')

        action = Action.selectBy(action=action_name)

        if not action.count():
            print "unknown action %s" % action_name
            return False

        action = action[0]
        
        tl_permissions = TaskListPermission.selectBy(task_listID=task_list.id,
                                                     actionID=action.id)

        if not tl_permissions.count():
            #shouldn't get here, because tasklists should always have
            #some permission row for each action.  If we do, reset
            #the permissions to the strictest level.
            task_list.rescuePermissions()
            tl_permissions = TaskListPermission.selectBy(task_listID=task_list.id,
                                                         actionID=action.id)
            
        return tl_permissions[0].min_level >= local_level


    def _initialize_project(self, action_name):
        if action_name == 'project_initialize':
            if c.level <= Role.getLevel('ProjectAdmin'):
                return True #OK, let admins initialize the project.
            else:
                raise NotInitializedException
        elif action_name == 'project_show_uninitialized':
            return True #always let people see the not initialized message


        if not c.project.initialized:
            if c.level <= Role.getLevel('ProjectAdmin'):
                redirect_to(controller='project', action='show_initialize', id = c.project.id)
            else:
                redirect_to(controller='project', action='show_uninitialized', id = c.project.id)

    def _authorize(self, project, action, params):
        controller = params['controller']

        if controller == 'error':
            return True

        environ = self._req.environ

        role = Role.selectBy(name=environ['topp.role'])
        if not role.count():
            raise Exception("No such role %s" % environ['topp.role'])
        c.level = role[0].level

        username = environ['topp.username']
        c.username = username

        func = getattr(self, action)
        if not getattr(func, 'action', None):
            raise MissingSecurityException("Programmer forgot to give the action attribute to the function '%s' in the controller '%s'" % (action, controller))
        action_verb = func.action

        #methods can override controllers (but should do so rarely)
        controller = getattr(func, 'controller', controller)
        
        action_name = controller + '_' + action_verb

        #A few special cases follow, with the general permission case at the end.

        if self._initialize_project(action_name):
            return True

        if action_verb == 'open':
            return True

        if action == 'auto_complete_for_owner':
            return True

        params = dict(params)
        params['username'] = username
        params.update(request.params)
        return self._has_permission(controller, action_name, params)


    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

from tasktracker.controllers.layouts import render_response
