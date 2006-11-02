
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

from tasktracker.lib.taskparser import TaskParser
#from tasktracker.tests import *

import datetime
import os

class TestImport:

    def test_parse(self):
        expected_tasks = {'blah blah blah':
                              dict(deadline = datetime.datetime(2006, 9, 13),
                                   title = 'blah blah blah'),
                          'morx':
                              dict(deadline = datetime.datetime(2006, 9, 4),
                                   title = 'morx'),
                          'write press release for fleem morx (bob)':
                              dict(deadline = datetime.datetime(2006, 9, 21), 
                                   title = 'write press release for fleem morx (bob)')
                          }
        datadir = "data"
        files = os.listdir(datadir)
        for file in files:
            path = os.path.join(datadir, file)
            if not os.path.isfile(path):
                continue

            tasks = TaskParser.parse(path)
            assert len(tasks) == len(expected_tasks)
            for task in tasks:
                assert expected_tasks.has_key(task['title'])
                ex_task = expected_tasks[task['title']]
                assert task['title'] == ex_task['title']
                assert task['deadline'].month == ex_task['deadline'].month
                assert task['deadline'].day == ex_task['deadline'].day
                assert task['deadline'].year == ex_task['deadline'].year
