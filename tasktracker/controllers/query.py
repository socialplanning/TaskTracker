
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

def _make_path_key(task):
    key = []
    cur = task
    while cur.parentID:
        key.append(cur.parentID)
        cur = cur.parent
    return key

def _sorted_by_parent(list, parent=0):
    #Schwartzian transform
    sort = [(_make_path_key(task), task) for task in list]
    return [x[1] for x in sorted(sort)]


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
        return render_response('task/flat_list.myt', flat=True)

    def _sorted_select(self, query):
        return Task.select(query, orderBy='task_list_id')

    @attrs(action='loggedin')
    def show_my_tasks(self):
        c.list_name = "My tasks"
        results = self._sorted_select(AND(Task.q.owner == c.username, Task.q.live == True))
        return self._render(results)

    @attrs(action='open')
    def show_project_tasks(self):
        c.list_name = "All tasks in a project"
        results = []
        for tl in TaskList.selectBy(projectID = c.project.id):
            results += list(Task.selectBy(task_listID = tl.id, live=True))
        return self._render(results)

    @attrs(action='open')
    def show_tasklist_tasks(self, id):
        c.list_name = "All tasks in a task list"
        results = self._sorted_select(AND(Task.q.task_listID == id, Task.q.live == True))
        return self._render(results)
