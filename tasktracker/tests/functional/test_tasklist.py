
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

from tasktracker.tests import *
from tasktracker.models import *

class TestTaskListController(TestController):
        
    def test_show_create(self):

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist', action='show_create'))

        form = res.forms[0]

        form['title'] = 'The new tl title'
        form['text'] = 'The new tl body'
        res = form.submit()

        location = res.header_dict['location']
        assert location.startswith('/tasklist/view/')

        id = int(location[location.rindex('/') + 1:])

        assert id

        res = res.follow()

        res.mustcontain('The new tl title')

        assert TaskList.get(id).text == 'The new tl body'
        
        #clean up: destroy new list
        TaskList.delete(id)

    def test_admin_only_list(self):
        #create a new list that only admins can touch
        task_list = TaskList(title="admin list 1", text="The list", projectID=self.project.id, username='member')

        #log in as a member
        app = self.getApp('member')        

        #make sure it doesn't show up on the index

        res = app.get(url_for(
                controller='tasklist', action='index'))

        assert 'admin list 1' not in res

        #make sure we can't view it.
        res = app.get(url_for(
                controller='tasklist', action='view', id=task_list.id))

        assert 'not_permitted' in res.header_dict['location']

        task_list.destroySelf()

    def test_member_viewable_list(self):
        #create a new list that members can view
        task_list = TaskList(title="member list 1", text="The list", projectID=self.project.id, username='member', action_tasklist_view=Role.selectBy(name='ProjectMember')[0].id)

        #log in as a member
        app = self.getApp('member')        

        res = app.get(url_for(
                controller='tasklist', action='index'))

        assert 'member list 1' in res

        res = res.click('member list 1')

        assert 'member list 1' in res

        #but members cannot create tasks.
        assert 'Add a new task' not in res

        res = app.get(url_for(
                controller='task', action='show_create', task_listID=task_list.id))

        assert 'not_permitted' in res.header_dict['location']        

        task_list.destroySelf()

    def test_simple_security(self):
        #log in as a member
        app = self.getApp('member')

        res = app.get(url_for(
                controller='tasklist', action='show_create'))

        form = res.forms[0]

        #set a security setting in the complex form
        #we want to show that this will be overwritten
        select = form.fields['action_task_change_status'][0]
        select.value = select.options[-1][0] #most secure
        
        form.fields['title'][0].value = 'test simple security'
        form.fields['mode'][0].value = 'simple'
        policy = form.fields['policy'][0]
        policy.value = policy.options[0][0] #open
        
        res = form.submit()
        res = res.follow()
        
        path = res.req.path_info
        new_task_list_id = int(path[path.rindex('/') + 1:])

        task_list = TaskList.get(new_task_list_id)

        for perm in task_list.permissions:
            if perm.action.action == 'task_change_status':
                assert perm.min_level >= Role.getLevel('Anonymous')

        
        task_list.destroySelf()

    def test_watchers(self):
        #log in as a member
        app = self.getApp('member')


    def _set_security(self, p):

        task_list = TaskList(title="member list 1", text="The list", projectID=self.project.id, username='member')

        policy = SimpleSecurityPolicy.selectBy(name='open')
        for action in policy.actions:
            TaskListPermission(task_listID=task_list.id, action = action.id, min_level = action.min_level)


        task_list_view_url = url_for(
                controller='tasklist', action='view', id=task_list.id)

        res = app.get(task_list_view_url)
        
        #add self as watcher
        res = res.click("Watch this")
        
        assert res.header_dict['location'] == task_list_view_url

        res = res.follow()

        res.mustcontain("You are watching this tasklist")

        #we're back at the task list page.  Let's create a new task *via this page*

        form = res.forms[0]

        form['title'] = 'The new tl title'
        form['text'] = 'The new tl body'
        res = form.submit()

        #make sure the email was created

        mails = list(OutgoingEmail.select())

        import re
        found = False
        for mail in mails:
            if re.match('Subject: .*member list 1', mail.message):
                found = True
                break

        assert found
            
