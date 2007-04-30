
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

from tasktracker.lib.base import *
from tasktracker.models import *
from tasktracker.lib.helpers import filled_render, has_permission, SafeHTML

import formencode  

class CreateListForm(formencode.Schema): 
    pre_validators = [formencode.variabledecode.NestedVariables()]
    allow_extra_fields = True
    title = SafeHTML(not_empty = True)
    member_level = formencode.validators.Int()
    other_level = formencode.validators.Int()
    initial_assign = formencode.validators.Int()

def add_feature(name, value = None):
    f = TaskListFeature.selectBy(task_listID=c.tasklist.id, name=name)
    if f.count():
        f[0].value = value
    else:
        TaskListFeature(task_listID=c.tasklist.id, name=name, value=value)

def remove_feature(name, value = None):
    if name == 'private_tasks':
        for task in c.tasklist.tasks:
            task.private = False
    
    f = TaskListFeature.selectBy(task_listID=c.tasklist.id, name=name)
    if f.count():
        f[0].destroySelf()


def set_features(p):
    for feature in ['deadlines', 'custom_status', 'private_tasks']:
        if p.get('feature_%s' % feature, None):
            add_feature(feature)
        else:
            remove_feature(feature)

class TasklistController(BaseController):
    @classmethod
    def _getVisibleTaskLists(cls, username):
        return [t for t in TaskList.selectBy(projectID = c.project.id, live = True)
                if cls._has_permission('tasklist', 'show', {'id':t.id, 'username':username, 'blah':'blah'})]

    @attrs(action='open', readonly=True)
    def index(self):
        c.tasklists = self._getVisibleTaskLists(c.username)
        c.contextual_wrapper_class = 'tt-context-tasklist-index'
        return render_response('tasklist/index.myt')

    @attrs(action='show', readonly=True)
    @catches_errors
    def show(self, id, *args, **kwargs):
        c.tasklist = safe_get(TaskList, id, check_live=True)
        
        c.task_listID = id
        c.tasks = c.tasklist.topLevelTasks()
        c.parentID = 0
        c.depth = 0
        from tasktracker.lib import helpers as h
        c.permalink = h._get_permalink(request.GET)
        c.contextual_wrapper_class = 'tt-context-tasklist-show'
        return render_response('task/list.myt')

    @attrs(action='create', readonly=True)
    def show_create(self):
        c.managers = []
        c.administrators = c.usermapper.project_member_names("ProjectAdmin")
        if c.username not in c.administrators:
            c.administrators.append(c.username)
        c.contextual_wrapper_class = 'tt-context-tasklist-create'
        return render_response('tasklist/show_create.myt')

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
                if action == 'task_claim' or action == 'task_comment':
                    level = auth_level
                else:
                    level = other_level
            elif i <= p['member_level']:
                level = member_level
            else:
                level = manager_level

            #task_show and tasklist_show are the same
            make_permission(action, tasklist, level)
            if action == 'task_show':
                make_permission('tasklist_show', tasklist, level)

            #change_status is just another kind of update
            if action == 'task_update':
                make_permission('task_change_status', tasklist, level)

        #only managers can assign and update list and deal with private tasks
        #and delete tasklists
        make_permission('task_assign', tasklist, Role.getLevel('ListOwner'))
        make_permission('task_private', tasklist, Role.getLevel('ListOwner'))
        make_permission('tasklist_update', tasklist, Role.getLevel('ListOwner'))
        make_permission('tasklist_delete', tasklist, Role.getLevel('ListOwner'))
        
        #anyone can comment
        make_permission('task_comment', tasklist, auth_level)

        list_owner = Role.selectBy(name='ListOwner')[0].id
        #demote old managers
        for user in tasklist.special_users:
            if user.roleID == list_owner: 
                user.destroySelf()

        administrators = c.usermapper.project_member_names("ProjectAdmin")
        for manager in p['managers'].split(","):
            # ignore submitted managers who aren't project members
            # @@ this currently works silently.. should it error?
            if manager and manager not in administrators and manager in c.usermapper.project_member_names():
                TaskListRole(task_listID=tasklist.id, username=manager,roleID=list_owner)

    @authenticate
    @attrs(action='create', readonly=False)
    @validate(schema=CreateListForm(), form='show_create')  
    def create(self):
        assert self.form_result['member_level'] >= self.form_result['other_level']

        p = dict(self.form_result)
        p['username'] = c.username
        p['projectID'] = c.project.id
        if "feature_custom_status" not in p and "statuses" in p:
            del p['statuses']
        c.tasklist = TaskList(**p)
        
        set_features(p)
        self._setup_roles(p, c.tasklist)
        return Response.redirect_to(action='show',id=c.tasklist.id)

    @attrs(action='show', readonly=True)
    @catches_errors
    def show_update(self, id, *args, **kwargs):
        c.tasklist = safe_get(TaskList, id, check_live=True)
        c.managers = c.tasklist.managers()
        c.administrators = c.usermapper.project_member_names("ProjectAdmin")
        c.update = True
        p = {}
        for feature in c.tasklist.features:
            p['feature_' + feature.name] = 1
            setattr(c, 'feature_' + feature.name, 1)

        if has_permission('tasklist', 'update'):
            c.contextual_wrapper_class = 'tt-context-tasklist-update'
            return filled_render('tasklist/show_update.myt', c.tasklist, p)
        else:
            c.contextual_wrapper_class = 'tt-context-tasklist-preferences'
            return filled_render('tasklist/show_preferences.myt', c.tasklist, p)

    @authenticate
    @validate(schema=CreateListForm(), form='show_update')  
    @attrs(action='update', readonly=False)
    @catches_errors
    def update(self, id, *args, **kwargs):
        assert self.form_result['member_level'] >= self.form_result['other_level']
        c.tasklist = safe_get(TaskList, id, check_live=True)

        p = dict(self.form_result)
        
        if "feature_custom_status" not in p and "statuses" in p:
            del p['statuses']
        c.tasklist.set(**p)

        set_features(p)
        self._setup_roles(p, c.tasklist)
        return Response.redirect_to(action='show',id=c.tasklist.id)

    @authenticate
    @attrs(action='delete', readonly=False)
    @catches_errors
    def destroy(self, id, *args, **kwargs):
        c.tasklist = safe_get(TaskList, id, check_live=True)
        c.tasklist.live = False
        return Response.redirect_to(action='index')

#note the reverse order
def compareDates(a, b):
    delta = b.updated - a.updated
    return delta.days * 86400 + delta.seconds
