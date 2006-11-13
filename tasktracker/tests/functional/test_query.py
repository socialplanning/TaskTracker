
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
        tl = self.create_tasklist('testing task watching', security_level=0)

        my_task = Task(title='My task', text='x', private=False, task_listID=tl.id, owner='admin')
        her_task = Task(title='Her task', text='x', private=False, task_listID=tl.id, owner='maria')
        
        app = self.getApp('admin')

        res = app.get(url_for(controller='query', action='my_tasks'))
        res.mustcontain('My task')
        assert 'Her task' not in res

        for x in [my_task, her_task, tl]:
            x.destroySelf()

