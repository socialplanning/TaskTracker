
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
        self.setup_fixtures()
        TestCase.__init__(self, *args)

    def _get_authenticator(self, res):
        authenticator = None
        for form in res.forms.values():
            if form.get('authenticator', None):
                authenticator = form['authenticator'].value
                break
        assert authenticator
        return authenticator

    def setup_fixtures(self):
        conn = hub.getConnection()
        for table in [Watcher, TaskListPermission, OutgoingEmail,
                      Task.versions.versionClass, TaskList.versions.versionClass, Task, TaskList]:
            delquery = conn.sqlrepr(Delete(table.q, where=None))
            conn.query(delquery)
    
        app = self.getApp('admin')
        app.post(url_for(controller='project', action='initialize'))

        self.task_list = self.create_tasklist('The list')

        Task(title="Task 1", text="This is a task",
             task_list=self.task_list)
        Task(title="Task 2", text="Another task",
             task_list=self.task_list)
        task_list_complete = self.create_tasklist('Complete list')
        Task(title="Task A", text="more",
             task_list=task_list_complete,
             status='done')
        Task(title="Task B", text="yet more text",
             task_list=task_list_complete,
             status='done')


    def setup_database(self):
        nonFixedClasses = [Task, TaskList, TaskListPermission, Project, TaskListRole, Comment, Status, User]

        #for table in nonFixedClasses[::-1]:
        #    table.dropTable(ifExists=True)
        #for table in nonFixedClasses:
        #    table.createTable(ifNotExists=True)
        
        for username in ['admin', 'member', 'auth', 'anon']:
            User(username=username, password='nopassword'.encode("base64"))

        self.project = Project(title='theproject')

    def getApp(self, username):
        encoded = 'Basic ' + (username + ':nopassword').encode('base64')        
        return paste.fixture.TestApp(self.wsgiapp, extra_environ={'HTTP_AUTHORIZATION': encoded})
        
    def create_tasklist(self, title, member_level=4, other_level=4):
        app = self.getApp('admin')
        res = app.get(url_for(
                controller='tasklist', action='show_create'))

        form = res.forms[0]
        
        form['title'] = title
        class level(object):
            def __init__(self, level):
                self.value = level

        form.fields['member_level'] = [level(member_level)]
        form.fields['other_level'] = [level(other_level)]
        
        res = form.submit()
        res = res.follow()
        
        path = res.req.path_info
        new_task_list_id = int(path[path.rindex('/') + 1:])

        task_list = TaskList.get(new_task_list_id)
        return task_list

__all__ = ['url_for', 'TestController']
