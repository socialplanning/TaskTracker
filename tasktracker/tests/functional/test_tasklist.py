
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

class TestTaskListController(TestController):
        
    def test_show_create(self):

        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))

        form = res.forms[0]

        form['title'] = 'The new tl title'
        form['text'] = 'The new tl body'
        res = form.submit()

        location = res.header_dict['location']
        assert location.startswith('/tasklist/show/')

        id = int(location[location.rindex('/') + 1:])

        assert id
        res = res.follow()

        res.mustcontain('The new tl title')

        tl = TaskList.get(id)
        assert tl.text == 'The new tl body'
        
        tl.destroySelf()

    def test_update_screen_preserves_features(self):

        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))

        form = res.forms[0]

        form['title'] = 'The new tl title'
        form['feature_deadlines'] = 1
        res = form.submit()
        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]

        res = app.get(url_for(controller='tasklist', action='show_update', id = the_id))
        assert res.form['feature_deadlines'].checked
        assert not res.form['feature_custom_statuses'].checked 
        assert not res.form['feature_private_tasks'].checked
        
        #clean up: destroy new list
        TaskList.get(the_id).destroySelf

    def test_custom_status(self):

        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))

        form = res.forms[0]

        form['title'] = 'The new tl title'
        form['feature_custom_statuses'] = 1

        form['statuses'] = 'morx,fleem'
        res = form.submit()
        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]

        tl = TaskList.get(the_id)
        assert [s.name for s in tl.statuses] == ['morx', 'fleem', 'done']
        
        #clean up: destroy new list
        tl.destroySelf()

    def test_list_manager(self):
        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))

        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['managers'] = 'admin,member'

        res = form.submit()
        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]
        res = res.follow()
        res = res.click("view list preferences")
        res.mustcontain('<span>member</span>')

        app = self.getApp('member')

        res = app.get(url_for(controller='tasklist', action='show_update', id=the_id))
        res.mustcontain('Managers:')
        form = res.forms[0]
        form['managers'] = 'admin'
        res = form.submit()
        res = res.follow()

        res = app.get(url_for(controller='tasklist', action='show_update', id=the_id))
        assert res.header_dict['location'].startswith('/error/')

    def test_list_update_permission(self):
        tl = self.create_tasklist('fleem')

        #create a task
        task = Task(title='morx', task_listID=tl.id)

        app = self.getApp('anon')

        res = app.get(url_for(controller='task', action='show', id=task.id))
        found = False
        for form in res.forms.values():
            if form.action.startswith ('/task/change_field'):
                found = True

        assert found

    def test_privacy(self):
        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))

        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['feature_private_tasks'] = 1

        res = form.submit()
        res = res.follow()
        form = res.forms[0]

        assert form.fields.has_key('private')

        res = app.get(url_for(controller='tasklist', action='show_create'))
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['feature_private_tasks'] = 0

        res = form.submit()
        res = res.follow()
        form = res.forms[0]

        assert not form.fields.has_key('private')


    def test_tasklist_watch(self):
        """Tests adding self as a watcher for a task list"""
        tl = self.create_tasklist(title="list")

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist', action='show', id=tl.id))
        
        res = res.click("watch this list")
        res.mustcontain("Just the highlights")
        res = res.forms[0].submit()

        assert res.header_dict['location'].startswith('/tasklist/show/%s' % tl.id)
        res = res.follow()
        res.mustcontain("edit watch settings")
        tl.destroySelf()
