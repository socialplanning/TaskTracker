
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

class QueryController(BaseController):

    def _render(self, results):
        c.results = results
        c.depth = 0
        c.flat = True
        return render_response('zpt', 'task.flat_list')

    @attrs(action='loggedin')
    def my_tasks(self):
        c.list_name = "My tasks"
        results = Task.selectBy(owner=c.username, live=True)
        return self._render(results)

    @attrs(action='open')
    def project_tasks(self):
        c.list_name = "All tasks in a project"
        results = Task.select(TaskList.q.projectID == Project.q.id & 
                              Project.q.title == c.project & 
                              Task.q.task_listID == TaskList.q.id & 
                              Task.q.live == True)
        return self._render(results)

    @attrs(action='open')
    def tasklist_tasks(self, id):
        c.list_name = "All tasks in a task list"
        results = Task.select(Task.q.task_listID == id & 
                              Task.q.live == True)
        return self._render(results)
