
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
    def test_my_tasks(self):
        #fixtures:
        tl = self.create_tasklist('testing task query', security_level=0)

        my_task = Task(title='My task', text='x', private=False, task_listID=tl.id, owner='admin')
        her_task = Task(title='Her task', text='x', private=False, task_listID=tl.id, owner='maria')
        
        app = self.getApp('admin')

        res = app.get(url_for(controller='query', action='my_tasks'))
        res.mustcontain('theproject - testing task query')
        res.mustcontain('My task')
        assert 'Her task' not in res

        for x in [my_task, her_task, tl]:
            x.destroySelf()

    def test_project_tasks(self):
        tl = self.create_tasklist('testing task query', security_level=0)

        task = Task(title='A task', text='x', private=False, task_listID=tl.id)
        
        app = self.getApp('admin')

        res = app.get(url_for(controller='query', action='project_tasks'))
        res.mustcontain('A task')

        for x in [task, tl]:
            x.destroySelf()

    def test_tasklist_tasks(self):
        tl = self.create_tasklist('testing task query', security_level=0)

        assert tl.id != self.task_list.id

        task = Task(title='A task', text='x', private=False, task_listID=tl.id)
        task2 = Task(title='Not here', text='x', private=False, task_listID=self.task_list.id)

        app = self.getApp('admin')

        res = app.get(url_for(controller='query', action='tasklist_tasks', id=tl.id))
        res.mustcontain('A task')
        assert 'Not here' not in res

        for x in [task, task2, tl]:
            x.destroySelf()
