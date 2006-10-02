from tasktracker.lib.base import *
from tasktracker.models import *

import formencode  

class CreateListForm(formencode.Schema):  
    allow_extra_fields = True  
    filter_extra_fields = True  
    #todo: add validators
    title = formencode.validators.NotEmpty()

class TasklistController(BaseController):


    def _clean_params(self, params):
        allowed_params = ("title", "text", "projectID")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean

    @attrs(action='open')    
    def index(self):
        c.tasklists = TaskList.getVisibleTaskLists(c.level)        
        return render_response('zpt', 'tasklist.index')

    @attrs(action='view')
    @catches_errors
    def view(self, id):
        c.tasklist = self._getTaskList(int(id))
        c.tasks = Task.selectBy(live=True, task_listID=c.tasklist.id)
        c.statuses = Status.selectBy(projectID = c.tasklist.projectID)
        return render_response('zpt', 'task.list')

    def _prepare_form(self):
        c.actions = Action.select()
        c.policies = SimpleSecurityPolicy.select()

    @attrs(action='create')
    def show_create(self):
        self._prepare_form()
        c.permissions = dict([(action.id, action.roles[0].level) for action in c.actions])
        c.security_policy_id = 1
        return render_response('zpt', 'tasklist.show_create')

    @attrs(action='create')
    @validate(schema=CreateListForm(), form='show_create')  
    def create(self):
        p = dict(request.params)
        p['username'] = c.username
        p['projectID'] = c.project.id
        c.tasklist = TaskList(**p)

        if p['mode'] == 'simple':
            policy = SimpleSecurityPolicy.get(p['policy'])
            p['security_policy'] = policy.id
            for action in policy.actions:
                p['action_%s' % action.action.action] = action.min_level
        else:
            p['security_policy'] = 0 #we don't need no steeking referential integrity

        return redirect_to(action='view',id=c.tasklist.id)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id):
        c.tasklist = self._getTaskList(int(id))
        c.permissions = dict([(perm.action.id, perm.min_level) for perm in c.tasklist.permissions])
        c.security_policy_id = c.tasklist.security_policyID
        self._prepare_form()

        return render_response('zpt', 'tasklist.show_update')

    @validate(schema=CreateListForm(), form='show_update')  
    @attrs(action='update')
    @catches_errors
    def update(self, id):
        c.tasklist = self._getTaskList(int(id))

        c.tasklist.set(**dict(request.params))

        return redirect_to(action='index')

    def _getTaskList(self, id):
        try:
            return TaskList.get(int(id))
        except LookupError:
            raise NoSuchIdError("No such tasklist ID: %s" % id)

    @attrs(action='create')
    @catches_errors
    def destroy(self, id):
        c.tasklist = self.getTaskList(int(id))
        c.tasklist.live = False
        c.flash = "Deleted."
        return redirect_to(action='index')
