import os, sys
from unittest import TestCase

here_dir = os.path.dirname(__file__)
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)

import pkg_resources

pkg_resources.working_set.add_entry(conf_dir)

pkg_resources.require('Paste')
pkg_resources.require('PasteScript')

from paste.deploy import loadapp, appconfig, CONFIG
import paste.fixture

from tasktracker.config.routing import *
from routes import request_config, url_for

from tasktracker.models import soClasses, Task, TaskList

class TestController(TestCase):
    def __init__(self, *args):
        self.conf = appconfig('config:development.ini#test', relative_to=conf_dir)
        CONFIG.push_process_config({'app_conf': self.conf.local_conf,
                                    'global_conf': self.conf.global_conf})
        wsgiapp = loadapp('config:development.ini#test', relative_to=conf_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
        self.setup_database()
        TestCase.__init__(self, *args)

    def setup_database(self):
        for table in soClasses[::-1]:
            table.dropTable(ifExists=True)
        for table in soClasses:
            table.createTable(ifNotExists=True)
        task_list = TaskList(title="List 1", text="The list")
        Task(title="Task 1", text="This is a task",
             sort_index=1, task_list=task_list)
        Task(title="Task 2", text="Another task",
             sort_index=2, task_list=task_list)
        task_list_complete = TaskList(title="Complete list", text="Another list")
        Task(title="Task A", text="more",
             sort_index=1, task_list=task_list_complete,
             status='completed')
        Task(title="Task B", text="yet more text",
             sort_index=2, task_list=task_list_complete,
             status='completed')
        
        

__all__ = ['url_for', 'TestController']
