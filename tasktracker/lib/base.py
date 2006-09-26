from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, rest, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from tasktracker.models import *
from tasktracker.controllers import *
import tasktracker.lib.helpers as h

permission_names = {'task/view': 'task_view',
                    'task/show_update': 'task_update'}

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

class BaseController(WSGIController):

    def __before__(self, action, **params):
        project = Project.getProject(self._req.environ['topp.project'])
        c.projectID = project.id

        if not self._authorize(project, action, params):
            redirect_to(controller='project', action='show_not_permitted')
            #raise SecurityException("IMPROPER AUTHENTICATION")

    def _authorize(self, project, action, params):
        controller = params['controller']
        if controller == 'error':
            return True

        environ = self._req.environ

        level = Role.selectBy(name=environ['topp.role'])[0].level

        username = environ['topp.username']
        c.username = username

        action_name = getattr(self, action).action
        if action_name == 'open':
            return True
        
        action_name = controller + '_' + action_name

        #A few special cases follow, with the general permission case at the end.

        if action_name == 'project_initialize':
            if level <= Role.getLevel('ProjectAdmin'):
                return True #OK, let admins initialize the project.
            else:
                raise NotInitializedException
        elif action_name == 'project_show_uninitialized':
            return True #always let people see the not initialized message

        if not project.initialized:
            if level <= Role.getLevel('ProjectAdmin'):
                redirect_to(controller='project', action='show_initialize', id=project.id)
            else:
                redirect_to(controller='project', action='show_uninitialized', id=project.id)

        #now we know the project is initialized

        #special case for creating task lists
        if action_name == 'tasklist_create':
            return project.create_list_permission >= level

        if controller == 'tasklist':
            task_list = TaskList.get(params['id'])
        elif controller == 'task':
            if action_name == 'task_create':
                controller = 'task_list'
                task_list = TaskList.get(params['id'])
            else:
                task = Task.get(int(params['id']))
                task_list = TaskList.get(task.task_listID)
        else:
            task_list = "I AM BROKEN"

        if level > Role.getLevel('ListOwner'):
            if task_list.isOwnedBy(username):
                level = Role.getLevel('ListOwner')

        if controller == 'task' and level > Role.getLevel('TaskOwner'):
            if task.isOwnedBy(username):
                level = role.getLevel('TaskOwner')

        action = Action.selectBy(action=action_name)[0]
        
        tl_permission = TaskListPermission.selectBy(task_listID=task_list.id,
                                                    actionID=action.id)[0]
        return tl_permission.min_level >= level


    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

from tasktracker.controllers.layouts import render_response
