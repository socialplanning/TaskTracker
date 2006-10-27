
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
import paste.script.appinstall

from tasktracker.config.routing import *
from routes import request_config, url_for

from tasktracker.models import *

from threading import *

from pylons import c
from pylons.util import AttribSafeContextObj
d = AttribSafeContextObj()
c._push_object(d)


class TestController(TestCase):
    def __init__(self, *args):
        paste.script.appinstall.SetupCommand('setup-app').run(['development.ini#test'])
        self.conf = appconfig('config:development.ini#test', relative_to=conf_dir)
        CONFIG.push_process_config({'app_conf': self.conf.local_conf,
                                    'global_conf': self.conf.global_conf})
        self.wsgiapp = loadapp('config:development.ini#test', relative_to=conf_dir)
        self.setup_database()
        self.setup_project()
        self.setup_fixtures()
        TestCase.__init__(self, *args)

    def setup_fixtures(self):
    
        task_list = TaskList(title="List 1", text="The list", projectID=self.project.id, username='member')

        Task(title="Task 1", text="This is a task",
             task_list=task_list)
        Task(title="Task 2", text="Another task",
             task_list=task_list)
        task_list_complete = TaskList(title="Complete list", text="Another list", projectID=self.project.id, username='admin')
        Task(title="Task A", text="more",
             task_list=task_list_complete,
             status='done')
        Task(title="Task B", text="yet more text",
             task_list=task_list_complete,
             status='done')

    def setup_database(self):
        nonFixedClasses = [Task, TaskList, TaskListPermission, Project, TaskListOwner, Comment, Status, User]

        for table in nonFixedClasses[::-1]:
            table.dropTable(ifExists=True)
        for table in nonFixedClasses:
            table.createTable(ifNotExists=True)
        
        for username in ['admin', 'member', 'auth']:
            User(username=username, password='nopassword'.encode("base64"))

        self.project = Project(title='theproject')

    def setup_project(self):
        app = self.getApp('admin')

        res = app.get('/')
        location = res.header_dict['location']
        assert location.startswith('/project/show_initialize/')

        res = res.follow()

        res.mustcontain('theproject')
        res.mustcontain('Set up')

        form = res.forms[0]

        form['create_list_permission'] = 50

        form['statuses'] = "not done,done,"

        res = form.submit()


    def getApp(self, username):
        encoded = 'Basic ' + (username + ':nopassword').encode('base64')        
        return paste.fixture.TestApp(self.wsgiapp, extra_environ={'HTTP_AUTHORIZATION': encoded})
        

__all__ = ['url_for', 'TestController']
