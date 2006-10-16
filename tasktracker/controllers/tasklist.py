from tasktracker.lib.base import *
from tasktracker.models import *

import formencode  

class CreateListForm(formencode.Schema):  
    allow_extra_fields = True  
    filter_extra_fields = True  
    #todo: add validators
    title = formencode.validators.NotEmpty()


    TaskList.select(
        AND(TaskList.q.live==True, 
            TaskListPermission.q.task_listID == TaskList.q.id, 
            TaskListPermission.q.actionID == Action.q.id, 
            Action.q.action == 'tasklist_view'))
    
#TaskListPermission.q.min_level >= level))    



class TasklistController(BaseController):
    @classmethod
    def _getVisibleTaskLists(cls, username):
        return [t for t in TaskList.select() if cls._has_permission('tasklist', 'tasklist_view', {'id':t.id, 'username':username})]

    def _clean_params(self, params):
        allowed_params = ("title", "text", "projectID")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean

    @attrs(action='open')    
    def index(self):
        c.tasklists = self._getVisibleTaskLists(c.username)
        return render_response('zpt', 'tasklist.index')


    @attrs(action='open')
    def watch(self, id):
        c.task_list = self._getTaskList(int(id))
        if not c.task_list.isWatchedBy(c.username):
            Watcher(username=c.username, task_listID=c.task_list.id, taskID=0)
        return Response.redirect_to(action='view',controller='tasklist', id=c.task_list.id)

    @attrs(action='open')
    def stopwatch(self, id):
        c.task_list = self._getTaskList(int(id))
        Watcher.selectBy(username=c.username, task_list=int(id))[0].destroySelf()
        return Response.redirect_to(action='view',controller='tasklist', id=c.task_list.id)


    @attrs(action='view')
    @catches_errors
    def view(self, id):
        c.tasklist = self._getTaskList(int(id))
        c.tasks = c.tasklist.topLevelTasks()
        c.depth = 0
        return render_response('zpt', 'task.list')

    def _prepare_form(self):
        c.actions = Action.select()
        c.policies = SimpleSecurityPolicy.select()

    @attrs(action='create')
    def show_create(self):
        self._prepare_form()
        c.owners = []
        c.uneditableOwners = [c.username]
        c.permissions = dict([(action.id, action.roles[0].level) for action in c.actions])
        c.security_policy_id = 1
        return render_response('zpt', 'tasklist.show_create')

    def _set_security(self, p):
        if p['mode'] == 'simple':
            policy = SimpleSecurityPolicy.get(p['policy'])
            p['security_policy'] = policy.id
            for action in policy.actions:
                p['action_%s' % action.action.action] = action.min_level
        else:
            p['security_policy'] = 0 #we don't need no steeking referential integrity


    @attrs(action='create')
    @validate(schema=CreateListForm(), form='show_create')  
    def create(self):
        p = dict(request.params)
        p['username'] = c.username
        p['projectID'] = c.project.id
        owners = p.pop('owners').split(",")
        c.tasklist = TaskList(**p)

        for owner in owners:
            if not owner or owner == c.username:
                continue
            TaskListOwner(task_listID = c.tasklist.id, username = owner, sire='')

        self._set_security(p)

        return Response.redirect_to(action='view',id=c.tasklist.id)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id):
        c.tasklist = self._getTaskList(int(id))
        c.owners = [o.username for o in c.tasklist.owners if not o.username == c.username]
        if c.tasklist.isOwnedBy(c.username):
            c.uneditableOwners = [c.username]
        else:
            c.uneditableOwners = []
        c.permissions = dict([(perm.action.id, perm.min_level) for perm in c.tasklist.permissions])
        c.security_policy_id = c.tasklist.security_policyID
        self._prepare_form()

        return render_response('zpt', 'tasklist.show_update')

    @validate(schema=CreateListForm(), form='show_update')  
    @attrs(action='update')
    @catches_errors
    def update(self, id):
        c.tasklist = self._getTaskList(int(id))

        p = dict(request.params)
        self._set_security(p)

        c.tasklist.set(**p)
        
        if p['owners']:
            new_owners = p['owners'].split(",")
            for owner in c.tasklist.owners:
                if not owner in new_owners:
                    owner.destroySelf()
                    
            for owner in new_owners:
                if not owner:
                    continue
                if not owner in c.tasklist.owners:
                    TaskListOwner(task_listID = c.tasklist.id, username = owner, sire='')

        return Response.redirect_to(action='index')

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
        return Response.redirect_to(action='index')
    
    @attrs(action='private')
    def private(self):
        """This is a dummy method to deal with private tasks."""
        pass
