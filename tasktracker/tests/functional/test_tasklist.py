
# Copyright (C) 2006-2007 The Open Planning Project

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
        
    def test_create_list(self):
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show_create'))
        
        ### fill in some values and create a tasklist
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['text'] = 'The new tl body'
        res = form.submit()

        ### the response should redirect us to a tasklist/show
        location = res.header_dict['location']
        assert location.startswith('/tasklist/show/')

        ### the response redirect should contain a proper integer id for the new tasklist
        id = int(location[location.rindex('/') + 1:])
        assert id

        ### the new tasklist view should contain the tasklist title
        res = res.follow()
        res.mustcontain('The new tl title')

        ### and the tasklist itself should have been created with the correct id and values
        tl = TaskList.get(id)
        assert tl.text == 'The new tl body'

        tl.destroySelf()

    def test_different_projects(self):
        ### @@ this test needs to tell us about itself

        app = self.getApp('admin')

        res = app.get(url_for(controller='tasklist', action='show_create'))
        
        ### fill in some values and create a tasklist
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['text'] = 'The new tl body'
        res = form.submit()

        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]

        res = app.get(url_for(controller='tasklist'))
        res.mustcontain("The new tl title")
        res = app.get(url_for(controller='tasklist', action='show', id=the_id))
        res.mustcontain("The new tl title")

        res = app.post(url_for(controller='project', action='initialize'),
                       extra_environ={"HTTP_X_OPENPLANS_PROJECT":"differentproj"})

        res = app.get(url_for(controller='tasklist'), extra_environ={"HTTP_X_OPENPLANS_PROJECT":"differentproj"})
        assert "The new tl title" not in res.body
        
        res = app.get(url_for(controller='tasklist', action='show', id=the_id),
                      extra_environ={"HTTP_X_OPENPLANS_PROJECT":"differentproj"}, status=404)

    def test_delete_list(self):
        tl = self.create_tasklist('testing tasklist deletion')
        app = self.getApp("admin")

        ### we can get the tasklist
        res = app.get(url_for(controller='tasklist', action='show'))
        res.mustcontain("testing tasklist deletion")

        ### admins are given an option to delete the tasklist
        res.mustcontain("delete this list")

        ### but non-list-managers are given no such option
        app = self.getApp("member")
        res = app.get(url_for(controller='tasklist', action='show'))
        res.mustcontain("testing tasklist deletion")
        assert "delete this list" not in res.body
        
        ### they can't even do it directly
        res = app.post(url_for(controller='tasklist', action='destroy', id=tl.id, authenticator=self._get_authenticator(res)))
        res = res.follow()
        res.mustcontain("Not permitted")
        res = app.get(url_for(controller='tasklist'))        
        res.mustcontain("testing tasklist deletion")

        ### but, really, admins can
        app = self.getApp("admin")
        res = app.get(url_for(controller='tasklist', action='show'))
        res.mustcontain("delete this list")
        res = app.post(url_for(controller='tasklist', action='destroy', id=tl.id, authenticator=self._get_authenticator(res)))

        ### it will redirect to the list of tasklists page, and the tasklist will be gone
        res = res.follow()
        assert "testing tasklist deletion" not in res.body

        tl.destroySelf()

    def test_update_screen_preserves_features(self):
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show_create'))

        ### create a new tasklist with deadlines installed
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['feature_deadlines'] = 1
        res = form.submit()

        ### view the tasklist update-prefs screen
        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]
        res = app.get(url_for(controller='tasklist', action='show_update', id = the_id))

        ### it should display the proper preferences based on the creation
        assert res.form['feature_deadlines'].checked
        assert not res.form.fields.has_key('feature_custom_status')
        assert not res.form['feature_private_tasks'].checked
        
        TaskList.get(the_id).destroySelf

    def test_custom_status(self):
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show_create'))

        ### create a new tasklist with custom statuses
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['feature_custom_status'] = 1
        form['statuses'] = 'morx,fleem'
        res = form.submit()

        ### the tasklist should have stored the proper custom statuses
        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]
        tl = TaskList.get(the_id)
        assert set([s.name for s in tl.statuses]) == set(['morx', 'fleem', 'done'])

        ### and they should all be somewhere on the tasklist view page
        res = app.get(url_for(controller="tasklist", action="show", id=the_id))
        res.mustcontain("morx")
        res.mustcontain("fleem")
        res.mustcontain("done")

        ### when we view the update preferences page the statuses should be there
        res = app.get(url_for(controller="tasklist", action="show_update"))
        res.mustcontain("morx")
        res.mustcontain("fleem")
        res.mustcontain("done")

        ### we can add new statuses to the list of custom statuses
        form = res.forms[0]
        form['statuses'] = 'geoffrey'
        res = form.submit()
        
        ### they should all be in the tasklist and on the view page
        assert set([s.name for s in tl.statuses]) == set(['morx', 'fleem', 'done', 'geoffrey'])
        res = app.get(url_for(controller="tasklist", action="show", id=the_id))
        res.mustcontain("morx")
        res.mustcontain("fleem")
        res.mustcontain("done")
        res.mustcontain("geoffrey")

        tl.destroySelf()        

    def test_list_manager(self):
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist', action='show_create'))

        ### create a new tasklist with an additional manager
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['managers'] = 'admin,member'
        res = form.submit()

        ### the tasklist preferences page should show the additional manager
        loc = res.header_dict['location']
        the_id = loc.split("/")[-1]
        res = res.follow()
        res = res.click("view list preferences", index=0)
        res.mustcontain('<span>member</span>')
        
        ### delete the additional manager from the list
        res = app.get(url_for(controller='tasklist', action='show_update', id=the_id))
        form = res.forms[0]
        form['managers'] = 'admin'
        res = form.submit()
        res = res.follow()

        ### the former additional manager should no longer have manager privileges
        app = self.getApp('member')
        res = app.get(url_for(controller='tasklist', action='show_update', id=the_id))
        assert res.header_dict['location'].startswith('/error/')

        tl = TaskList.get(the_id)
        tl.destroySelf()

    ## @@ what is this testing??
    def test_list_update_permission(self):
        tl = self.create_tasklist('fleem')
        task = Task(title='morx', task_listID=tl.id)

        app = self.getApp('anon')
        res = app.get(url_for(controller='task', action='show', id=task.id))
        res.mustcontain('<option value="Medium">Medium</option>')

        task.destroySelf()
        tl.destroySelf()

    def test_privacy(self):
        app = self.getApp('admin')

        ### create a new tasklist with private tasks installed
        res = app.get(url_for(controller='tasklist', action='show_create'))
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['feature_private_tasks'] = 1
        res = form.submit()

        ### there should now be an option to make tasks private
        res = res.follow()
        form = res.forms[0]
        assert form.fields.has_key('private')
        res.mustcontain("make this task private")

        ### uninstall private tasks
        res = app.get(url_for(controller='tasklist', action='show_create'))
        form = res.forms[0]
        form['title'] = 'The new tl title'
        form['feature_private_tasks'] = 0
        res = form.submit()

        ### the privacy option should now be gone
        res = res.follow()
        form = res.forms[0]
        assert not form.fields.has_key('private')

    def test_readonly(self):

        def try_create_tasklist(title, member_level=4, other_level=4):
            res = app.get(url_for(controller='tasklist', action='show_create'))

            form = res.forms[0]
            
            form['title'] = title
            class level(object):
                def __init__(self, level):
                    self.value = level
                    
            form.fields['member_level'] = [level(member_level)]
            form.fields['other_level'] = [level(other_level)]
                    
            res = form.submit()
            return res

        ### set a readonly lock on the project 
        app = self.getApp('admin')
        res = app.post(url_for(controller='project', action='lock'))

        ### creating a new tasklist should no longer be possible
        res = try_create_tasklist('test locking')
        res = app.get(url_for(controller='tasklist'))
        assert 'test locking' not in res

        ### unlock the project and create a new tasklist successfully
        res = app.post(url_for(controller='project', action='unlock'))
        res = try_create_tasklist('test locking')
        res = app.get(url_for(controller='tasklist'))
        assert 'test locking' in res

    def test_initialized(self):
        app = self.getApp('admin')

        ### uninitialize the project
        res = app.post(url_for(controller='project', action='uninitialize'))
        res.mustcontain("successfully uninitialized project")
        
        ### no mere member should be able to do anything
        app = self.getApp('member')
        res = app.get(url_for(controller='tasklist'))
        res = res.follow()
        res.mustcontain("has not installed a task tracker.")

        ### not even initialize the project
        from tasktracker.lib.base import NotInitializedException
        try:
            res = app.post(url_for(controller='project', action='initialize'))
            raise AssertionError("error: unauthorized user's attempt to initialize project did not raise NotInitializedException")
        except NotInitializedException:
            pass

        ### an admin can't do anything either
        app = self.getApp('admin')
        res = app.get(url_for(controller='tasklist'))
        res = res.follow()
        res.mustcontain("has not installed a task tracker.")

        ### but an admin can initialize the project
        res = app.post(url_for(controller='project', action='initialize'))
        res.mustcontain("successfully initialized project")
        
        ### and then can do things as normal
        res = app.get(url_for(controller='tasklist'))
        res.mustcontain("Glossary")

    def test_task_create(self):
        """Tests creating a new task"""
        tl = self.create_tasklist('testing task creation')        
        app = self.getApp('admin')

        ### create a new task
        res = app.get(url_for(controller='tasklist', action='show', id=tl.id))
        form = res.forms[0]
        form['title'] = "The new task"
        form['text'] = "The description text"
        res = form.submit()

        ### the response will contain information about the task
        res.mustcontain("The new task")
        res.mustcontain("The description text")
        
        tl.destroySelf()


