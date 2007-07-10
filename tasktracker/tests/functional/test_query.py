
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

class TestTaskController(TestController):
    def test_my_tasks(self):
        tl = self.create_tasklist('testing task query')
        my_task = self.create_task(title='Admin task', text='x', task_listID=tl.id, owner='admin')
        her_task = self.create_task(title='Her task', text='x', task_listID=tl.id, owner='maria')

        ### admin's task should show up here and maria's should not
        app = self.getApp('admin')
        res = app.get(url_for(controller='query', action='show_my_tasks'))
        res.mustcontain('theproject - testing task query')
        res.mustcontain('Admin task')
        assert 'Her task' not in res

        ### maria's task should show up here and admin's should not
        app = self.getApp('maria')
        res = app.get(url_for(controller='query', action='show_my_tasks'))
        res.mustcontain('theproject - testing task query')
        res.mustcontain('Her task')
        assert 'Admin task' not in res

        for x in [my_task, her_task, tl]:
            x.destroySelf()

    def test_project_tasks(self):
        tl = self.create_tasklist('testing task query')
        task = self.create_task(title='A task', text='x', task_listID=tl.id)
        app = self.getApp('admin')

        res = app.get(url_for(controller='query', action='show_project_tasks'))
        res.mustcontain('A task')

        for x in [task, tl]:
            x.destroySelf()

    def test_tasklist_tasks(self):
        tl = self.create_tasklist('testing task query')

        assert tl.id != self.task_list.id # @@ ?

        task = self.create_task(title='A task', text='x', task_listID=tl.id)
        task2 = self.create_task(title='Not here', text='x', task_listID=self.task_list.id)

        app = self.getApp('admin')

        res = app.get(url_for(controller='query', action='show_tasklist_tasks', id=tl.id))
        res.mustcontain('A task')
        assert 'Not here' not in res

        for x in [task, task2, tl]:
            x.destroySelf()
