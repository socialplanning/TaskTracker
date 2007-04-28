
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

from tasktracker.tests import *
from tasktracker.models import *
import re

class TestTaskController(TestController):

    # @@ what the hell is this testing? -- egj
    def test_index(self):
        lists = list(TaskList.select())
        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist'))
        for l in lists:
            res.mustcontain(l.title)

        res = res.click(lists[0].title)
        res.mustcontain(lists[0].title)

        task = lists[0].tasks[0]
        authenticator = self._get_authenticator(res)

        assert not task.status.done
        res2 = app.post('/task/change_field/%s' % task.id,
                        params={'field':'status', 'status':'true', 'authenticator':authenticator})
        assert task.status.done
        try:
            res2 = app.post('/task/change_field/%s' % task.id,
                            params={'field':'status', 'status':'__no_such_status__', 'authenticator':authenticator})
        except AssertionError:
            pass
        assert task.status.done
     
    def test_create_task(self):
        task_listID = TaskList.select()[0].id
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show', id=task_listID))

        ### create a new task
        form = res.forms['add_task_form']
        form['title'] = 'The new task title'
        form['text'] = 'The new task body'
        res = form.submit()

        ### the response should consist of the new task's table row
        assert re.search('<tr[^>]*status\s*=\s*"not%20done"', res.body)
        res.mustcontain("The new task title")
        res.mustcontain("The new task body")

        ### the task should now show up on the tasklist view page
        res = app.get(url_for(controller='tasklist', action='show', id=task_listID))
        res.mustcontain("The new task title")
        res.mustcontain("The new task body")

    def test_delete_task(self):
        tl = self.create_tasklist('testing deletion')
        top_level_task = Task(title='top level', task_listID = tl.id, text = '')
        sub_task = Task(title='second level', task_listID = tl.id, text = '', parentID = top_level_task.id)
        second_task = Task(title='another task', task_listID = tl.id, text = '')
        app = self.getApp('admin')

        ### we should be able to delete a task by clicking a link
        res = app.get(url_for(controller='task', action='show', id=top_level_task.id))
        res.mustcontain("delete this task")
        # we actually can't just click the link, because there's some magical hidden javascript
        res = app.post(url_for(controller='task', action='destroy', id=top_level_task.id,
                               authenticator=self._get_authenticator(res)))

        ### this should redirect us to the tasklist page
        res = res.follow()

        ### the task should be gone
        assert "top level" not in res.body
        
        ### but all other tasks should remain
        res.mustcontain("another task")
        
        ### but the deleted task's subtasks should not remain!
        assert "second level" not in res.body
        try:
            res = app.get(url_for(controller='task', action='show', id=sub_task.id))
            raise Exception("Request for deleted task should have failed!")
        except AssertionError: pass
        #assert res.status != 200
        #.mustcontain("This task has been deleted.")

        ### the deleted task shouldn't be available anymore either
        try: 
            res = app.get(url_for(controller='task', action='show', id=top_level_task.id))
            raise Exception("Request for deleted task should have failed!")
        except AssertionError: pass
        #assert res.status != 200
        #res.mustcontain("This task has been deleted.")

        for ob in (tl, top_level_task, sub_task, second_task):
            ob.destroySelf()

    def test_subtask(self):
        """ Test that subtasks show up on the page for the task they come from. """
        tl = self.create_tasklist('testing subtasks')
        top_level_task = Task(title='top level', task_listID = tl.id, text = '')
        sub_task = Task(title='second level', task_listID = tl.id, text = '', parentID = top_level_task.id)
        app = self.getApp('admin')

        ### both the top-level and subtask should show up on the tasklist
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        res.mustcontain('top level')
        res.mustcontain('second level')

        ### and on the top-level task's page
        res = app.get(url_for(controller='task', action='show', id=top_level_task.id))
        res.mustcontain('top level')
        res.mustcontain('second level')
        res.mustcontain("1 </span> sub-task")

        sub_task.destroySelf()
        top_level_task.destroySelf()
        tl.destroySelf()

    def test_comments(self):
        tl = TaskList.select()[0]
        #set security such that any logged-in user can comment and show posts
        found = False
        for perm in tl.permissions:
            if perm.action.action == "task_comment" or perm.action.action == "task_show":
                found = True
                perm.min_level = Role.getLevel("Authenticated")
        assert found
        task1 = Task(title='Fleem', text='x', owner='fred', task_listID=tl.id)
        app = self.getApp('auth')

        ### make sure the task shows up
        res = app.get(url_for(controller='task', action='show', id=task1.id))
        res.mustcontain('Fleem')

        ### the comment should be returned in the response after it is submitted
        form = res.forms['add_comment_form']
        form.fields['text'][0].value = "This is a test comment."
        res = form.submit()
        res.mustcontain("This is a test comment.")

        ### and it should show up on the task's detail page, too
        res = app.get(url_for(controller='task', action='show', id=task1.id))
        res.mustcontain("This is a test comment.")

        task1.destroySelf()

    def test_private_tasks(self):
        tl = self.create_tasklist('testing the auth role')
        #hack to force private tasks
        TaskListFeature(task_listID=tl.id, name='private_tasks', value=None)
        nonpriv = Task(title='The non-private one', text='x', private=False, task_listID=tl.id)
        priv = Task(title='The private one', text='x', private=True, task_listID=tl.id)

        ### admins can see everything
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        res.mustcontain('The non-private one')
        res.mustcontain('The private one')

        ### including next/prev navigation to the private task
        res = app.get(url_for(controller='task', action='show', id=nonpriv.id))
        res.mustcontain("The private one")
        res = res.click("The private one")
        res.mustcontain("The private one")

        ### but mere members can't see private tasks
        app = self.getApp('member')
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        res.mustcontain('The non-private one')
        assert 'The private one' not in res.body

        ### not even in next/prev navigation on task/show
        res = app.get(url_for(controller='task', action='show', id=nonpriv.id))
        assert 'The private one' not in res.body

        ### they also can't guess urls
        res = app.get(url_for(controller='task', action='show', id=priv.id))
        location = res.header_dict['location']
        assert location.startswith('/error')

        ### project members can create private tasks
        app = self.getApp('member')
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        form = res.forms['add_task_form']
        form['title'] = 'The new task title'
        form['text'] = 'The new task body'
        form['private'] = '1'
        res = form.submit()

        ### the resulting task should say that it's private
        res.mustcontain("private")

        ### the task owner can see his private tasks
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        res.mustcontain('The non-private one')
        res.mustcontain("The new task title")

        ### though not other people's private tasks!
        assert "The private one" not in res.body

        app = self.getApp('Mowbray')
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        assert "The private one" not in res.body
        assert "The new task title" not in res.body
        res.mustcontain("The non-private one")

        ### and the task owner can access them too
        app = self.getApp('member')
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        res = res.click("The new task title")
        res.mustcontain("The new task title")
        
        ### even through next/prev navigation on task/show
        res = app.get(url_for(controller='task', action='show', id=nonpriv.id))
        res.mustcontain("The new task title")
        res = res.click("The new task title")
        res.mustcontain("The new task title")
        
        nonpriv.destroySelf()
        priv.destroySelf()

    def test_task_update_field(self):
        tl = self.create_tasklist('testing task update', member_level=1, other_level=1)
        task = Task(title='The task', text='x', private=False, task_listID=tl.id)        
        app = self.getApp('admin')
        
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))

        ### when you change a task owner, the response should consist of the new task TR
        res = app.post('/task/change_field/%s' % task.id,
                       params=dict(owner='Mowbray', field='owner', authenticator=self._get_authenticator(res)))
        assert re.search('<tr[^>]*owner\s*=\s*"Mowbray"', res.body)

        ### and the new owner should be displayed on the task page
        res = app.get(url_for(controller='task', action='show', id=task.id))
        res.mustcontain("Mowbray")

        ### there should be a newly-creted version now
        versions = list(task.versions)
        assert len(versions) == 1
        version = versions[0]

        ### and that version should reflect the original task information before the update
        assert version.owner == "" 
        assert version.dateArchived == task.created

        ### changing the status, deadline, and priority should do the same thing
        res = app.post('/task/change_field/%s' % task.id,
                       params=dict(status='true', field='status', authenticator=self._get_authenticator(res)))
        assert re.search('<tr[^>]*status\s*=\s*"done"', res.body)
        res = app.get(url_for(controller='task', action='show', id=task.id))

        res = app.post('/task/change_field/%s' % task.id,
                       params=dict(deadline='11-26-1984', field='deadline', authenticator=self._get_authenticator(res)))
        assert re.search('<tr[^>]*deadline\s*=\s*"1984-11-26"', res.body)
        res = app.get(url_for(controller='task', action='show', id=task.id))

        res = app.post('/task/change_field/%s' % task.id,
                       params=dict(priority='High', field='priority', authenticator=self._get_authenticator(res)))
        assert re.search('<tr[^>]*priority\s*=\s*"High"', res.body)
        res = app.get(url_for(controller='task', action='show', id=task.id))

        ### and each of those actions should have created a new version
        versions = list(task.versions)
        assert len(versions) == 4

        for version in versions:
            version.destroySelf()
        task.destroySelf()

        ### now make sure that a member cannot do this
        app = self.getApp('member')
        task = Task(title='The task', text='x', private=False, task_listID=tl.id)

        ### when he tries to change a field, the controller should throw us an AssertionError
        res = app.get(url_for(controller='task', action='show', id=task.id))
        try:
            res = app.post('/task/change_field/%s' % task.id,
                           params=dict(owner='member', field='owner', authenticator=self._get_authenticator(res)))
            raise Exception("This should have failed.")
        except AssertionError:
            pass

        ### his change should not be reflected in the task detail page
        res = app.get(url_for(controller='task', action='show', id=task.id))
        assert 'newowner' not in res.body

        ### and no new version should be created
        versions = list(task.versions)
        assert len(versions) == 0

        task.destroySelf()
        tl.destroySelf()

    def test_next_prev_task(self):
        tl = self.create_tasklist('testing next/prev tasks')
        name = "ZZZ XXX YYY VVV WWW UUU".split()
        tasks = [Task(title=name[i], task_listID=tl.id, owner='admin') for i in range(6)]
        tasks[3].owner = "Mowbray"
        tasks[4].priority = "High"

        app = self.getApp('admin')
        
        ### with a flat list and no sorting or filtering, prev and next tasks should be sorted by id
        res = app.get(url_for(controller='task', action='show', id=tasks[0].id))

        ### the display for the first task should show the title of the current task and the next one
        res.mustcontain("ZZZ")
        res.mustcontain("XXX")
    
        ### but not the others
        for bad in name[2:]:
            assert bad not in res.body

        ### the display for a task in the middle should show its own name, the one before, and the one after
        res = app.get(url_for(controller='task', action='show', id=tasks[3].id))
        res.mustcontain("WWW")
        res.mustcontain("YYY")
        res.mustcontain("VVV")

        ### but not the others
        for bad in name[:2]:
            assert bad not in res.body
        for bad in name[5:]:
            assert bad not in res.body

        ### the display for the last task should show the title of the previous task and the current one
        res = app.get(url_for(controller='task', action='show', id=tasks[5].id))
        res.mustcontain("WWW")
        res.mustcontain("UUU")

        ### but not the others
        for bad in name[:4]:
            assert bad not in res.body

        ### with a flat list with sorting and filtering, prev and next tasks should be sorted accordingly
        res = app.get(url_for(controller='task', action='show', id=tasks[0].id, owner="admin", sortBy="title"))
        res.mustcontain("ZZZ")
        res.mustcontain("YYY")
        assert "XXX" not in res.body
        for bad in name[3:]:
            assert bad not in res.body

        #since filtering is disabled for next/prev, we want to cancel this test

#         ### let's check that filter
#         res = app.get(url_for(controller='task', action='show', id=tasks[4].id, owner="admin", sortBy="title"))
#         res.mustcontain("WWW")
#         res.mustcontain("XXX")
        
#         ### task VVV should be filtered out, so UUU should be there instead
#         res.mustcontain("UUU")
#         assert "VVV" not in res.body
#         assert "ZZZ" not in res.body
#         assert "YYY" not in res.body

        ### if we go to a url which the current task would be filtered from, the filters return to default
        res = app.get(url_for(controller='task', action='show', id=tasks[3].id, owner="admin", sortBy="title", priority="None"))
        res.mustcontain("WWW")
        res.mustcontain("UUU")
        res.mustcontain("VVV")
        
        ### if a task has a child, the child will be the next task
        child = Task(title="child", task_listID=tl.id, owner='admin', parentID=tasks[0].id)
        res = app.get(url_for(controller='task', action='show', id=tasks[0].id, sortBy="title"))
        res.mustcontain("ZZZ")
        res.mustcontain("YYY")
        res.mustcontain("child</a> &gt;&gt;") # "child" will be in the response elsewhere too, so be more specific

        ### if a task has a parent, the parent will be the previous task
        res = app.get(url_for(controller='task', action='show', id=child.id, sortBy="title"))
        res.mustcontain("child")
        res.mustcontain('&lt;&lt; previous task: <a href = "/task/show/%d" base_href = "/task/show/%d" title = "" id = "title_%d" class = "uses_permalink big"> ZZZ' % (tasks[0].id, tasks[0].id, tasks[0].id))

        for task in tasks:
            task.destroySelf()
        child.destroySelf()
        tl.destroySelf()

    def can_claim_tasks(self):
        pass


#    def _getElementsByTagName(self, body, tagname):
#        """ This is a total hack and should not be used """
#        elements = []
#        start = -1
#        while 1:
#            start = body.find('<' + tagname, start + 1)
#            if start == -1:
#                break
#            end = body.find('>', start)
#            elements.append(body[start:end+1])
#
#        return elements

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
# actually, this role is never used.
