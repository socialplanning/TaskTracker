
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

class NamedList(list):
    pass

def _sorted_by_parent(list, parent=0):
    #first, we want the direct children of the passed-in list
    #then we want to replace each by a list consisting of them and their descendents
    out = []
    children = []
    for x in list:
        if x.parentID == parent:
            #TODO: wait, isn't this just a BFS?  
            #
            out.append(x)
            children += _sorted_by_parent(list, x.id)
    
    return out + children

class QueryController(BaseController):

    def _render(self, results):
        lists = []
        task_list_id = 0
        parent_id = -1

        results = _sorted_by_parent(results)

        for result in results:
            if result.task_listID != task_list_id or result.parentID != parent_id: 
                task_list_id = result.task_listID
                parent_id = result.parentID
                l = NamedList()
                lists.append (l)

                parents = []
                cur = result
                while cur.parentID:
                    parents.insert(0, cur.parent.title)
                    cur = cur.parent
                    
                if parents:
                    parent_path = "- %s" % " - ".join(parents)
                else:
                    parent_path = ''

                l.path = "%s - %s %s" % (result.task_list.project.title, result.task_list.title, parent_path)


            lists[-1].append(result)

        c.results = lists
        c.depth = 0
        c.flat = True
        return render_response('zpt', 'task.flat_list')

    def _sorted_select(self, query):
        return Task.select(query, orderBy='task_list_id')

    @attrs(action='loggedin')
    def my_tasks(self):
        c.list_name = "My tasks"
        results = self._sorted_select(AND(Task.q.owner == c.username, Task.q.live == True))
        return self._render(results)

    @attrs(action='open')
    def project_tasks(self):
        c.list_name = "All tasks in a project"
        results = self._sorted_select(AND(TaskList.q.projectID == c.project.id,
                              Task.q.task_listID == TaskList.q.id,
                              Task.q.live == True))
        return self._render(results)

    @attrs(action='open')
    def tasklist_tasks(self, id):
        c.list_name = "All tasks in a task list"
        results = self._sorted_select(AND(Task.q.task_listID == id, Task.q.live == True))
        return self._render(results)
