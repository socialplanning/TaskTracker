
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

# visit /migrate/migrate this with the old DB structure.  Save
# the generated SQL. Set up the new structure.  Run the SQL.

from tasktracker.lib.base import *
from tasktracker.models import *

class MigrateController(BaseController):

    @attrs(action=open)
    def migrate(self):
        migration = []
        last_task_list_id = TaskList.select().max('id')

        for task in reversed(list(Task.select(orderBy='id'))):
            new_id = task.id + last_task_list_id
            migration.append("UPDATE task set id=%d where id=%d" % (new_id, task.id))
            migration.append("UPDATE task set parent_id=%d where parent_id=%d" % (new_id, task.id))
            migration.append("INSERT INTO versionable (id, child_name) values (%d, 'Task')" % new_id)
            for comment in task.comments:
                migration.append("UPDATE comment set task_id=%d where task_id=%d" % (new_id, task.id))
        for tasklist in TaskList.select():
            migration.append("INSERT INTO versionable (id, child_name) values (%d, 'TaskList')" % tasklist.id)

        migration.append("alter table task add column child_name text")
        migration.append("alter table task_list add column child_name text")

        return render_text(";<br>".join(migration + [""]))
