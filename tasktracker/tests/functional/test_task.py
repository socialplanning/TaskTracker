
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
from datetime import timedelta

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
        authenticator = self._get_authenticator(app)

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
     

    def test_anyone_claim(self):
        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))
                    
        form = res.forms[0]
            
        form['title'] = 'anyone_claim'
        class level(object):
            def __init__(self, level):
                self.value = level
                    
        form.fields['member_level'] = [level(3)]
        form.fields['other_level'] = [level(2)]
                    
        res = form.submit()
        location = res.header_dict['location']
        the_id = location.split("/")[-1]  
        task = self.create_task(title='a task to claim', task_listID = the_id, text = '')
        self.task_set(task, 'owner', '')
        #now as auth
        app = self.getApp('auth')
        res = app.get(url_for(controller='tasklist', action='show', id=the_id))
        res.mustcontain('Claim this')


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
        top_level_task = self.create_task(title='top level', task_listID = tl.id, text = '')
        sub_task = self.create_task(title='second level', task_listID = tl.id, text = '', parentID = top_level_task.id)
        second_task = self.create_task(title='another task', task_listID = tl.id, text = '')
        app = self.getApp('admin')

        ### we should be able to delete a task by clicking a link
        res = app.get(url_for(controller='task', action='show', id=top_level_task.id))
        res.mustcontain("delete this task")
        # we actually can't just click the link, because there's some magical hidden javascript
        res = app.post(url_for(controller='task', action='destroy', id=top_level_task.id,
                               authenticator=self._get_authenticator(app)))

        ### this should redirect us to the tasklist page
        res = res.follow()

        ### the task should be gone
        assert "top level" not in res.body
        
        ### but all other tasks should remain
        res.mustcontain("another task")
        
        ### but the deleted task's subtasks should not remain!
        assert "second level" not in res.body
        res = app.get(url_for(controller='task', action='show', id=sub_task.id), status=404)

        ### the deleted task shouldn't be available anymore either
        res = app.get(url_for(controller='task', action='show', id=top_level_task.id), status=404)

        for ob in (tl, top_level_task, sub_task, second_task):
            ob.destroySelf()

    def test_subtask(self):
        """ Test that subtasks show up on the page for the task they come from. """
        tl = self.create_tasklist('testing subtasks')
        top_level_task = self.create_task(title='top level', task_listID = tl.id, text = '')
        sub_task = self.create_task(title='second level', task_listID = tl.id, text = '', parentID = top_level_task.id)
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
        task1 = self.create_task(title='Fleem', text='x', owner='fred', task_listID=tl.id)
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

    def test_next_prev_task(self):
        tl = self.create_tasklist('testing next/prev tasks')
        name = "ZZZ XXX YYY VVV WWW UUU".split()
        tasks = [self.create_task(title=name[i], task_listID=tl.id, owner='admin') for i in range(6)]
        self.task_set(tasks[3], 'owner', 'Mowbray')
        self.task_set(tasks[4], 'priority', 'High')

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
        child = self.create_task(title="child", task_listID=tl.id, owner='admin', parentID=tasks[0].id)
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
