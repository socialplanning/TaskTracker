from tasktracker.lib.taskparser import TaskParser
from tasktracker.tests import *

import datetime
import os

class TestImport(TestController):

    def test_parse(self):
        expected_tasks = [dict(deadline = datetime.datetime(2006, 9, 21), 
                           title = 'write press release for fleem morx'), 
                          dict(deadline = datetime.datetime(2006, 9, 13),
                               title = 'blah blah blah'),
                          dict(deadline = datetime.datetime(2006, 9, 4),
                               title = 'morx')
                          ]
        datadir = "tasktracker/tests/data"
        files = os.listdir(datadir)
        for file in files:
            path = os.path.join(datadir, file)
            if not os.path.isfile(path):
                continue
            f = open(path, "rb")
            data = f.read()
            f.close()
            tasks = TaskParser.parse(data)
            print tasks
            assert len(tasks) == len(expected_tasks)
            for i in range(len(tasks)):
                assert tasks[i].title == expected_tasks[i].title
                assert tasks[i].deadline.month == expected_tasks[i].deadline.month
                assert tasks[i].deadline.day == expected_tasks[i].deadline.day
                assert tasks[i].deadline.year == expected_tasks[i].deadline.year or expected_tasks[i].deadline.year == 2006
