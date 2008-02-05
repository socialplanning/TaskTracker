
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
from tasktracker.lib.helpers import filled_render, has_permission, SafeHTML, html2safehtml

import formencode  

from paste import httpexceptions

class CreateListForm(formencode.Schema): 
    pre_validators = [formencode.variabledecode.NestedVariables()]
    allow_extra_fields = True
    title = SafeHTML(not_empty = True)
    text = SafeHTML(not_empty = False)    
    member_level = formencode.validators.Int()
    other_level = formencode.validators.Int(if_missing=None)
    initial_assign = formencode.validators.Int()

def add_feature(name, value = None):
    f = TaskListFeature.selectBy(task_listID=c.tasklist.id, name=name)
    if f.count():
        f[0].value = value
    else:
        TaskListFeature(task_listID=c.tasklist.id, name=name, value=value)

def remove_feature(name, value = None):  
    f = TaskListFeature.selectBy(task_listID=c.tasklist.id, name=name)
    if f.count():
        f[0].destroySelf()


def set_features(p):
    for feature in ['deadlines', 'custom_status']:
        if p.get('feature_%s' % feature, None):
            add_feature(feature)
        else:
            remove_feature(feature)

class TasklistController(BaseController):
    @classmethod
    def _getVisibleTaskLists(cls, username):
        return [t for t in TaskList.selectBy(projectID = c.project.id, live = True)
                if cls._has_permission('tasklist', 'show', {'id':t.id, 'username':username})]

    @attrs(action='open', readonly=True)
    def index(self):
        c.tasklists = self._getVisibleTaskLists(c.username)
        c.contextual_wrapper_class = 'tt-context-tasklist-index'
        return render('tasklist/index.myt')

    @attrs(action='show', readonly=True)
    @catches_errors
    def show(self, id, *args, **kwargs):
        c.tasklist = safe_get(TaskList, id, check_live=True)
        self.preload_permission_cache(c.tasklist)

        c.task_listID = id
        c.tasks = c.tasklist.topLevelTasks()
        c.parentID = 0
        c.depth = 0
        from tasktracker.lib import helpers as h
        c.permalink = h._get_permalink(request.GET)
        c.contextual_wrapper_class = 'tt-context-tasklist-show'
        return render('task/list.myt')

    @attrs(action='create', readonly=True)
    def show_create(self):
        c.managers = []
        c.administrators = c.usermapper.project_member_names("ProjectAdmin")
        if c.username not in c.administrators:
            c.administrators.append(c.username)
        c.contextual_wrapper_class = 'tt-context-tasklist-create'
        c.project_permission_level = request.environ['topp.project_permission_level']
        return render('tasklist/show_create.myt')

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

        anon_level = Role.getLevel('Anonymous')
        auth_level = Role.getLevel('Authenticated')
        member_level = Role.getLevel('ProjectMember')
        manager_level = Role.getLevel('ListOwner')

        actions = ['', 'task_show', 'task_claim', 'task_create', 'task_update']
        
        for i in range(len(actions)):
            action = actions[i]
            if not action: continue
            if i <= p.get('other_level', 0):
                if action != 'task_show':
                    level = auth_level
                else:
                    level = anon_level
            elif i <= p.get('member_level', 0):
                level = member_level
            else:
                level = manager_level

            #task_show and tasklist_show are the same, as is comment
            make_permission(action, tasklist, level)
            if action == 'task_show':
                make_permission('tasklist_show', tasklist, level)
                comment_level = level
                if level == anon_level:
                    comment_level = auth_level
                make_permission('task_comment', tasklist, comment_level)

            #change_status goes with claim
            if action == 'task_claim':
                if level == manager_level:
                    make_permission('task_change_status', tasklist, Role.getLevel('TaskOwner'))
                else:
                    make_permission('task_change_status', tasklist, level)

        list_owner_level = Role.getLevel('ListOwner')
        #only managers can assign and update list
        #and delete tasklists
        make_permission('task_assign', tasklist, list_owner_level)
        make_permission('tasklist_update', tasklist, list_owner_level)
        make_permission('tasklist_delete', tasklist, list_owner_level)
        

        list_owner = Role.selectBy(name='ListOwner')[0].id
        #demote old managers
        for user in tasklist.special_users:
            if user.roleID == list_owner: 
                user.destroySelf()

        administrators = c.usermapper.project_member_names("ProjectAdmin")
        for manager in p['managers'].split(","):
            # ignore submitted managers who aren't project members
            # @@ this currently works silently.. should it error?
            if manager and manager not in administrators and c.usermapper.is_project_member(manager):
                TaskListRole(task_listID=tasklist.id, username=manager,roleID=list_owner)

    @authenticate
    @attrs(action='create', readonly=False)
    @validate(schema=CreateListForm(), form='show_create')  
    def create(self):
        assert self.form_result['member_level'] >= self.form_result['other_level']
        
        p = dict(self.form_result)
        p['username'] = c.username
        p['projectID'] = c.project.id
        dup_tls = TaskList.selectBy(projectID = c.project.id, title = p['title'])
        if dup_tls.count(): pass
        #raise httpexceptions.HTTPInternalServerError("A tasklist with this title already exists.")

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

        if 'text' in p:
            p['text'] = html2safehtml(p['text'])
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
