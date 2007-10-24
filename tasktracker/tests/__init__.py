
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
import re
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
        # FIXME: Sometimes, for some reason, this attribute isn't set,
        # which causes url_for to fail
        request_config().environ = {
            'SCRIPT_NAME': '',
            'HTTP_HOST': 'localhost',
            }
        self.setup_database()
        self.setup_fixtures()
        TestCase.__init__(self, *args)

    def _get_authenticator(self, app):
        res = app.get(url_for(controller='task', action='show_authenticate', id=0))

        key_re = re.compile('key = (\w+)')
        result = key_re.search(res.body)
        authenticator = result.groups(1)[0]
        return authenticator

    def setup_fixtures(self):
        conn = hub.getConnection()
        for table in [TaskListPermission,
                      Task.versions.versionClass, TaskList.versions.versionClass, Task, TaskList]:
            delquery = conn.sqlrepr(Delete(table.q, where=None))
            conn.query(delquery)
    
        app = self.getApp('admin')
        app.post(url_for(controller='project', action='initialize'), extra_environ={"HTTP_X_OPENPLANS_TASKTRACKER_INITIALIZE" : 'True'})

        self.task_list = self.create_tasklist('The list')
        
        self.create_task(task_list=self.task_list, title="Task 1",
                         text="This is a task")
        self.create_task(task_list=self.task_list, title="Task 2",
                         text="Another task")
        task_list_complete = self.create_tasklist('Complete list')
        self.create_task(task_list=task_list_complete, title="Task A",
                         text="more", status='true')
        self.create_task(task_list=task_list_complete, title="Task B",
                         text="yet more text", status='true')


    def setup_database(self):
        nonFixedClasses = [Task, TaskList, TaskListPermission, Project, TaskListRole, Comment, Status, User]

        #for table in nonFixedClasses[::-1]:
        #    table.dropTable(ifExists=True)
        #for table in nonFixedClasses:
        #    table.createTable(ifNotExists=True)
        
        for username in ['admin', 'member', 'auth', 'anon']:
            User(username=username, password='nopassword'.encode("base64"))

        self.project = Project(title='theproject')

    def getApp(self, username, project_permission_level='open_policy', project='theproject'):
        encoded = 'Basic ' + (username + ':nopassword').encode('base64')        
        return paste.fixture.TestApp(self.wsgiapp, extra_environ={'HTTP_AUTHORIZATION': encoded,
'openplans_ttpolicy' : project_permission_level, "HTTP_X_OPENPLANS_PROJECT" : project})

    def create_task(self, task_list = None, task_listID = None, title="", text="", **kwargs):
        if task_list:
            task_listID = task_list.id
        assert task_listID
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show', id=task_listID))
        form = res.forms['add_task_form']
        form['title'] = title
        form['text'] = text
        if kwargs.get('parentID', None):
            form['parentID'] = kwargs['parentID']
            del kwargs['parentID']
        res = form.submit()
        try:
            task_id = re.search('<tr[^>]*id\s*=\s*"task_(\d+)"', res.body).group(1)
        except AttributeError:
            print "failed to create task", title, text
            print res.body
            return

        task = Task.get(task_id)
        for field, value in kwargs.items():
            self.task_set(task, field, value)
        return task

    def task_set(self, task, field, value, app=None):
        if not app:
            app = self.getApp('admin')
        res = app.post('/task/change_field/%s' % task.id,
                       params={'field':field, field:value, 'authenticator':self._get_authenticator(app)})

    def comment(self, taskID, text, user):
        app = self.getApp(user)
        res = app.post('/task/comment/%s' % taskID,
                       params={'text':text, 'authenticator':self._get_authenticator(app)})
        
        
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
