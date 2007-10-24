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

class TestHistoryController(TestController):
    def test_history(self):
        #let's create a task and do some things to it.

        tl = TaskList.select()[0]
        task = self.create_task(title='initial title', task_listID = tl.id, text = '')

        #the first series of changes

        self.task_set(task, 'title', 'changed title')
        self.task_set(task, 'text', 'changed text')

        self.comment(taskID = task.id, text='the first comment', user='first user')

        import time
        time.sleep(2)
        import datetime
        in_between_time  = datetime.datetime.now()
        time.sleep(2)

        #second series

        self.task_set(task, 'title', 'changed title again')
        self.task_set(task, 'text', 'changed text again')
        
        self.comment(taskID = task.id, text='the second comment', user='second user')

        assert len(list(task.comments)) == 2
        assert len(list(task.versions)) == 4

        #do revert
        app = self.getApp('admin')

        fdate = in_between_time.strftime("%Y-%m-%dT%H:%M:%S")

        res = app.post(url_for(
                controller='task', action='revertToDate', id=task.id, date=fdate))

        #check results of revert
        assert len(list(task.comments)) == 1
        assert len(list(task.versions)) == 2

        assert task.title == 'changed title'
        assert task.versions[0].title == 'initial title'
