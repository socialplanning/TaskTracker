
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

class TestTaskController(TestController):
    def test_index(self):
        lists = list(TaskList.select())

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist'))
        for l in lists:
            res.mustcontain(l.title)
        res = res.click(lists[0].title)
        res.mustcontain(lists[0].title)
        task = lists[0].tasks[0]

        assert task.status == 'not done'
        res2 = app.post('/task/change_field/%s' % task.id, params={'field':'status', 'status':'done'})
        assert task.status == "done"
        res2 = app.post('/task/change_field/%s' % task.id, params={'field':'status', 'status':'__no_such_status__'})
        assert task.status == "done"
     
    def test_show_create(self):
        task_listID = TaskList.select()[0].id

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist', action='show',
                id=task_listID
                ))

        form = res.forms['add_task_form']

        form['title'] = 'The new task title'
        form['text'] = 'The new task body'
        res = form.submit()

        # the response should consist of the new task's table row
        res.mustcontain('<tr status="not done"')        
        res.mustcontain("The new task title")
        res.mustcontain("The new task body")

        # the task should now show up on the tasklist view page
        res = app.get(url_for(
                controller='tasklist', action='show',
                id=task_listID
                ))
        res.mustcontain("The new task title")
        res.mustcontain("The new task body")

    def _getElementsByTagName(self, body, tagname):
        elements = []
        start = -1
        while 1:
            start = body.find('<' + tagname, start + 1)
            if start == -1:
                break
            end = body.find('>', start)
            elements.append(body[start:end+1])

        return elements

    def test_subtask(self):
        """ Test that subtasks show up on the page for the task they come from. """
        tl = self.create_tasklist('testing subtasks')
        top_level_task = Task(title='top level', task_listID = tl.id, text = '')
        sub_task = Task(title='second level', task_listID = tl.id, text = '', parentID = top_level_task.id)

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist', action='show', id=tl.id))

        res.mustcontain ('top level')
        res.mustcontain ('second level')

        res = app.get(url_for(
                controller='task', action='show', id=top_level_task.id))

        res.mustcontain ('top level')
        res.mustcontain ('second level')

        sub_task.destroySelf()
        top_level_task.destroySelf()
        tl.destroySelf()

# actually, this role is never used.

#     def test_auth_role(self):
#         tl = self.create_tasklist('testing the auth role')

#         #set security such that only task owner can change status and update
#         found = False
#         for perm in tl.permissions:
#             if perm.action.action == "task_change_status" or perm.action.action == "task_update":
#                 found = True
#                 perm.min_level = Role.getLevel("TaskOwner")
#         assert found

#         #add a task assigned to 'auth'
#         task1 = Task(title='Fleem', text='x', owner='auth', task_listID=tl.id)
#         #add a task not assigned to 'auth'
#         task2 = Task(title='Fleem', text='x', owner='admin', task_listID=tl.id)

#         app = self.getApp('auth')

#         res = app.get(url_for(
#                 controller='tasklist', action='show', id=tl.id))

#         res.mustcontain('testing the auth role')

#         spanTags = self._getElementsByTagName(res.body, 'span')

#         found = 0
#         for span in spanTags:
#             for field in 'status deadline priority owner'.split():
#                 if '%s-label_%d' % (field, task1.id) in span:
#                 #the label for task1 must be clickable
#                     assert 'onclick="viewChangeableField(%d, &quot;%s&quot;)"' % (task1.id, field) in span
#                     found += 1
#                 elif '%s-label_%d' % (field, task2.id) in span:
#                 #the label for task2 must not be clickable
#                     assert 'onclick="viewChangeableField(%d, \'%s\')"' % (task1.id, field) not in span
#                     found += 1

#         assert found == 8

#         selectTags = self._getElementsByTagName(res.body, 'select')
#         found = 0
#         for select in selectTags:
#             #there is no select for task2, because we can't edit it.
#             assert 'status_%d' % task2.id not in select 
#             assert 'priority_%d' % task2.id not in select

#             #but there is one for task1
#             if 'status_%d' % task1.id in select or 'priority_%d' % task1.id in select:
#               found += 1

#         assert found == 2

#         task1.destroySelf()
#         task2.destroySelf()
#         tl.destroySelf()

    def test_comments(self):
        tl = TaskList.select()[0]

        #set security such that any logged-in user can comment and show posts
        found = False
        for perm in tl.permissions:
            if perm.action.action == "task_comment" or perm.action.action == "task_show":
                found = True
                perm.min_level = Role.getLevel("Authenticated")
        assert found

        #add a task assigned to 'fred'
        task1 = Task(title='Fleem', text='x', owner='fred', task_listID=tl.id)

        #show the task
        app = self.getApp('auth')

        res = app.get(url_for(
                controller='task', action='show', id=task1.id))

        res.mustcontain('Fleem')
        
        #fill in the form
        form = res.forms['add_comment_form']

        form.fields['text'][0].value = "This is a test comment."

        res = form.submit()
        res = res.follow()

        res.mustcontain("This is a test comment.")

        task1.destroySelf()

    def test_private_tasks(self):
        tl = self.create_tasklist('testing the auth role')
        #hack to force private tasks
        TaskListFeature(task_listID=tl.id, name='private_tasks', value=None)

        nonpriv = Task(title='The non-private one', text='x', private=False, task_listID=tl.id)
        priv = Task(title='The private one', text='x', private=True, task_listID=tl.id)

        #admins can see everything
        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist', action='show', id=tl.id))

        res.mustcontain('The non-private one')
        res.mustcontain('The private one')

        #but mere members can't see private tasks
        app = self.getApp('member')

        res = app.get(url_for(
                controller='tasklist', action='show', id=tl.id))

        res.mustcontain('The non-private one')
        assert 'The private one' not in res.body

        #they also can't guess urls
        res = app.get(url_for(
                controller='task', action='show', id=priv.id))

        location = res.header_dict['location']
        assert location.startswith('/error')

        # but task owners can see their private tasks
        app = self.getApp('member')
        priv.owner = "member"

        res = app.get(url_for(
                controller='tasklist', action='show', id=tl.id))

        res.mustcontain('The non-private one')
        res.mustcontain('The private one')

        
        nonpriv.destroySelf()
        priv.destroySelf()
    
    def test_task_update(self):
        tl = self.create_tasklist('testing task update')

        task = Task(title='The task', text='x', private=False, task_listID=tl.id)
        
        app = self.getApp('admin')

        res = app.get(url_for(
                controller='task', action='show_update', id=task.id))

        form = res.forms[0]
        form.fields['title'][0].value = "The updated task."

        res = form.submit()

        res = app.get(url_for(
                controller='task', action='show', id=task.id))
        
        res.mustcontain("The updated task")

        #find the old version
        versions = task.versions
        assert len(versions) == 1
        version = versions[0]

        assert version.title == "The task"
        assert version.text == "x"
        assert version.updated == task.created

        version.destroySelf()
        task.destroySelf()
        tl.destroySelf()
        
#     def test_task_watch(self):
#         """Tests adding self as a watcher for a task"""
#         tl = self.create_tasklist('testing task watching')

#         task = Task(title='The task', text='x', private=False, task_listID=tl.id)
        
#         app = self.getApp('admin')

#         res = app.get(url_for(controller='task', action='show', id=task.id))
        
#         task_path = '/task/show/%s' % task.id

#         res = res.click("Watch this task")
#         res.mustcontain("Just the highlights")
#         res = res.forms[0].submit()
#         assert res.header_dict['location'].startswith(task_path)
#         res = res.follow()

#         res.mustcontain("Edit your watch settings")

#         #delete watcher

#         res = app.get(url_for(controller='task', action='show', id=task.id))
#         res = res.click("Edit your watch settings")
#         res = res.click("Stop watching")
#         assert Watcher.selectBy(username='admin').count() == 0

    def test_task_update_field(self):
        tl = self.create_tasklist('testing task update')

        task = Task(title='The task', text='x', private=False, task_listID=tl.id)
        
        app = self.getApp('admin')

        res = app.get(url_for(
                controller='task', action='assign', id=task.id, owner='newowner'))

        res = app.get(url_for(
                controller='task', action='show', id=task.id))
        
        res.mustcontain("newowner")

        #find the old version
        versions = task.versions
        assert len(versions) == 1
        version = versions[0]

        assert version.owner == "" 
        assert version.updated == task.created

        version.destroySelf()
        task.destroySelf()
        tl.destroySelf()
