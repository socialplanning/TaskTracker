
# Copyright (C) 2006 The Open Planning Project

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

from tasktracker.lib.base import *
from tasktracker.models import *
from tasktracker.lib.helpers import filled_render

import formencode  

class CreateListForm(formencode.Schema): 
    pre_validators = [formencode.variabledecode.NestedVariables()]
    allow_extra_fields = True
    title = formencode.validators.NotEmpty()
    member_level = formencode.validators.Int()
    other_level = formencode.validators.Int()
    initial_assign = formencode.validators.Int()

class TasklistController(BaseController):
    @classmethod
    def _getVisibleTaskLists(cls, username):
        return [t for t in TaskList.selectBy(projectID = c.project.id)
                if cls._has_permission('tasklist', 'show', {'id':t.id, 'username':username, 'blah':'blah'})]

    @attrs(action='open')    
    def index(self):
        c.tasklists = self._getVisibleTaskLists(c.username)
        return render_response('zpt', 'tasklist.index')

    @attrs(action='show')
    @catches_errors
    def show(self, id, *args, **kwargs):
        c.tasklist = self._getTaskList(int(id))
        c.task_listID = id
        c.tasks = c.tasklist.topLevelTasks()
        c.depth = 0
        return render_response('zpt', 'task.list')

    @attrs(action='create')
    def show_create(self):
        c.managers = []
        c.administrators = [u['username'] for u in c.usermapper.project_members() if 'ProjectAdmin' in u['roles']]
        return render_response('zpt', 'tasklist.show_create')

    def _apply_role(self, members, tasklist, role):
        for member in members:
            if member:
                TaskListRole(task_listID = tasklist.id, username = member, role = Role.getByName("ListOwner"))


    def _setup_roles(self, p, tasklist):

        for permission in tasklist.permissions:
            permission.destroySelf()

        def make_permission(action_name, tasklist, level):
            TaskListPermission(action=Action.selectBy(action = action_name)[0], 
                               task_list=tasklist, min_level = level)

        other_level = Role.getLevel('Anonymous')
        auth_level = Role.getLevel('Authenticated')
        member_level = Role.getLevel('ProjectMember')
        manager_level = Role.getLevel('ListOwner')

        actions = ['', 'task_show', 'task_claim', 'task_create', 'task_update']
        for i in range(len(actions)):
            action = actions[i]
            if not action: continue
            if i <= p['other_level']:
                if action != 'task_claim' and action != 'task_comment':
                    level = other_level
                else:
                    level = auth_level
            elif i <= p['member_level']:
                level = member_level
            else:
                level = manager_level

            #task_show and tasklist_show are the same
            make_permission(action, tasklist, level)
            if action == 'task_show':
                make_permission('tasklist_show', tasklist, level)

        #anyone can change task status
        make_permission('task_change_status', tasklist, Role.getLevel('TaskOwner'))

        #only managers can assign and update list
        make_permission('task_assign', tasklist, Role.getLevel('ListOwner'))
        make_permission('tasklist_update', tasklist, Role.getLevel('ListOwner'))

        #anyone can comment
        make_permission('task_comment', tasklist, auth_level)

        list_owner = Role.selectBy(name='ListOwner')[0].id
        #demote old managers
        for user in tasklist.special_users:
            if user.roleID == list_owner: 
                user.destroySelf()

        administrators = [u['username'] for u in c.usermapper.project_members() if 'ProjectAdmin' in u['roles']]
        for manager in p['managers'].split(","):
            if manager and not manager in administrators:
                TaskListRole(task_listID=tasklist.id, username=manager,roleID=list_owner)

    @attrs(action='create')
    @validate(schema=CreateListForm(), form='show_create')  
    def create(self):
        assert self.form_result['member_level'] >= self.form_result['other_level']

        p = dict(self.form_result)
        p['username'] = c.username
        p['projectID'] = c.project.id
        c.tasklist = TaskList(**p)
        
        def add_feature(name, value = None):
            TaskListFeature(task_listID=c.tasklist.id, name=name, value=value)

        if p.get('feature_deadlines', None):
            add_feature('deadlines')
        if p.get('feature_custom_status', None):
            add_feature('custom_status', None) #statuses are stored normalized
        if p.get('feature_private_tasks', None):
            add_feature('private_tasks')

        self._setup_roles(p, c.tasklist)

        return Response.redirect_to(action='show',id=c.tasklist.id)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id, *args, **kwargs):
        c.tasklist = TaskList.get(id)
        c.managers = c.tasklist.managers()
        c.administrators = [u['username'] for u in c.usermapper.project_members() if 'ProjectAdmin' in u['roles']]
        c.update = True
        p = {}
        for feature in c.tasklist.features:
            p['feature_' + feature.name] = 1

        return filled_render('tasklist.show_update', c.tasklist, p)

    @validate(schema=CreateListForm(), form='show_update')  
    @attrs(action='update')
    @catches_errors
    def update(self, id, *args, **kwargs):
        c.tasklist = self._getTaskList(int(id))

        p = dict(self.form_result)

        c.tasklist.set(**p)

        self._setup_roles(p, c.tasklist)
        
        return Response.redirect_to(action='show',id=c.tasklist.id)

    def _getTaskList(self, id):
        try:
            return TaskList.get(int(id))
        except LookupError:
            raise NoSuchIdError("No such tasklist ID: %s" % id)

    @attrs(action='create')
    @catches_errors
    def destroy(self, id, *args, **kwargs):
        c.tasklist = self.getTaskList(int(id))
        c.tasklist.live = False
        c.flash = "Deleted."
        return Response.redirect_to(action='index')
    
    @attrs(action='private')
    def private(self):
        """This is a dummy method to deal with private tasks."""
        pass


