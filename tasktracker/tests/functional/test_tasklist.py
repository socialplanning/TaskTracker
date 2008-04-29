
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
                       extra_environ={"HTTP_X_OPENPLANS_PROJECT":"differentproj", "HTTP_X_OPENPLANS_TASKTRACKER_INITIALIZE" : 'True'})

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
        res = app.post(url_for(controller='tasklist', action='destroy', id=tl.id, authenticator=self._get_authenticator(app)), status=403)

        res = app.get(url_for(controller='tasklist'))        
        res.mustcontain("testing tasklist deletion")

        ### but, really, admins can
        app = self.getApp("admin")
        res = app.get(url_for(controller='tasklist', action='show'))
        res.mustcontain("delete this list")
        res = app.post(url_for(controller='tasklist', action='destroy', id=tl.id, authenticator=self._get_authenticator(app)))

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
        form['member_level'] = '0'
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
        res = app.get(url_for(controller='tasklist', action='show_update', id=the_id), status=403)

        tl = TaskList.get(the_id)
        tl.destroySelf()


    def test_readonly(self):

        def try_create_tasklist(title, member_level=4, other_level=4, status=303):
            res = app.get(url_for(controller='tasklist', action='show_create'))

            form = res.forms[0]
            
            form['title'] = title
            class level(object):
                def __init__(self, level):
                    self.value = level
                    
            form.fields['member_level'] = [level(member_level)]
            form.fields['other_level'] = [level(other_level)]
                    
            res = form.submit(status=status)
            return res

        ### set a readonly lock on the project 
        app = self.getApp('admin')
        res = app.post(url_for(controller='project', action='lock'))

        ### creating a new tasklist should no longer be possible
        res = try_create_tasklist('test locking', status=403)
        res = app.get(url_for(controller='tasklist'))
        assert 'test locking' not in res

        ### unlock the project and create a new tasklist successfully
        res = app.post(url_for(controller='project', action='unlock'))
        res = try_create_tasklist('test locking')
        res = app.get(url_for(controller='tasklist'))
        assert 'test locking' in res

    def test_initialized(self):
        tt_unavailable_msg = 'TaskTracker is currently unavailable'
        app = self.getApp('admin')

        ### uninitialize the project
        res = app.post(url_for(controller='project', action='uninitialize'), extra_environ={"HTTP_X_OPENPLANS_TASKTRACKER_INITIALIZE" : 'True'})
        res.mustcontain("successfully uninitialized project")
        
        ### no mere member should be able to do anything
        app = self.getApp('member')
        res = app.get(url_for(controller='tasklist'))
        res = res.follow()
        res.mustcontain(tt_unavailable_msg)

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
        res.mustcontain(tt_unavailable_msg)

        ### but an admin can initialize the project (via opencore)
        res = app.post(url_for(controller='project', action='initialize'), extra_environ={"HTTP_X_OPENPLANS_TASKTRACKER_INITIALIZE" : 'True'})
        res.mustcontain("successfully initialized project")
        
        ### and then can do things as normal
        res = app.get(url_for(controller='tasklist'))
        res.mustcontain("Within a task list")

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

    def test_tasklist_security(self):
        """
        Tests all possible security settings for actions
        pertaining to tasklists based on a security matrix.
        Actions not covered in these tests have not yet
        been added to the security matrix.

        Actions covered in these tests:
        view tasklist index (or access any TaskTracker page)
        tasklist_create

        Actions that are NOT covered in these tests:
        tasklist_show
        tasklist_update
        tasklist_delete
        """

        f = open("tasktracker/tests/data/tasklists_security.csv")
        users = ['admin', 'member', 'auth', 'anon']
        line_no = 0
        for line in f:
            line_no += 1
            fields = line.strip('\n').split(',')
            project_level = fields[0]
            fields = fields[1:]
            for user in users:
                view_index, create_list = fields[:2]
                fields = fields[2:]
                
                app = self.getApp(user, project_permission_level = project_level)

                # test viewing
                status = view_index == "Y" and 200 or user == "anon" and 401 or 403
                try:
                    res = app.get(url_for(controller='tasklist', action='index'), status=status)
                except:
                    print "Error on line %d: user %s, security %s, view_index expected %s" % (line_no, user, project_level, view_index)
                    raise

                # test tasklist creation
                status = create_list == "Y" and 200 or user == "anon" and 401 or 403
                try:
                    res = app.get(url_for(controller='tasklist', action='show_create'), status=status)
                    if status == 200:
                        form = res.forms[0]
                        form['title'] = "The new tasklist title"
                        form['member_level'] = 4
                        form['other_level'] = 4
                        res = form.submit(status=303) # annoying special case.. tasklist creation redirects to index
                except:
                    print "Error on line %d: user %s, security %s, create_list expected %s" % (line_no, user, project_level, create_list)
                    raise

            print "Done testing line %d: %s" % (line_no, line)

    def test_task_security(self):
        """
        Tests all possible security settings for actions
        pertaining to tasks based on a security matrix.
        Actions not covered in these tests have not yet
        been added to the security matrix.

        Actions covered in these tests:
        task_view
        task_claim
        task_change_status
        task_create
        task_update

        """

        f = open("tasktracker/tests/data/security.csv")
        security_levels = ['not even see this list', 'view this list', 'and claim tasks', 'and create new tasks', 'and edit any task']
        users = ['admin', 'member', 'auth', 'anon']
        line_no = 0
        for line in f:
            line_no += 1
            fields = line[:-1].split(",")
            project_level, member_level, other_level = fields[0:3]
            member_level = security_levels.index(member_level)
            other_level = security_levels.index(other_level)
            fields = fields[3:]
            for user in users:
                def status_for_action(action):
                    status = 200
                    if not action:
                        status = 403
                        if user == 'anon':
                            status = 401
                    return status
                _, view, claim, create, edit = [status_for_action(x == 'Y') for x in fields[:5]]
                fields = fields[5:]

                app = self.getApp(user, project_permission_level = project_level)
                tl = self.create_tasklist('fleem', member_level, other_level)
                #create a task programmatically (note: bypasses security)
                task = self.create_task(title='morx', task_listID=tl.id)

                #test viewing
                try:
                    res = app.get(url_for(controller='task', action='show', id=task.id), status=view)
                except:
                    print "line: %d, user: %s, action: view, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                #test commenting
                try:
                    comment = view
                    if user == 'anon':
                        comment = 401 #anonymous users cannot comment -- all else is as per grid

                    res = app.post(url_for(controller='task', action='comment', id=task.id, text='comment text'), status=comment)
                except:

                    print "line: %d, user: %s, action: comment, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                authenticator = self._get_authenticator(app)

                #test claim: status
                try:
                    res = app.post('/task/change_field/%s' % task.id,
                                    params={'field':'status', 'status':'true', 'authenticator':authenticator}, status=claim)
                except:
                    print "line: %d, user: %s, action: claim (status), member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                #test claim: claim
                try:
                    user_actual = user
                    if user == 'anon':
                        user_actual = ''
                    res = app.post('/task/change_field/%s' % task.id,
                                    params={'field':'owner', 'owner' : user_actual, 'authenticator':authenticator}, status=claim)
                except:
                    print "line: %d, user: %s, action: claim (claim), member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                #test create
                try:

                    res = app.get(url_for(controller='task', action='show_create', task_listID=tl.id), status=create)
                    if res.status == 200:
                        form = res.forms['add_task_form']
                        form['title'] = 'The new task title'
                        form['text'] = 'The new task body'

                        res = form.submit(status=create)
                except:
                    print "line: %d, user: %s, action: create, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                #test edit
                try:
                    res = app.post('/task/change_field/%s' % task.id,
                                   params=dict(deadline='07-03-1980', field='deadline', authenticator=authenticator), status=edit)

                except:
                    print "line: %d, user: %s, action: edit, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                #test assign (list admins only)
                try:
                    if user == 'admin':
                        assign = status_for_action(True)
                    else:
                        assign = status_for_action(False)

                    res = app.post('/task/change_field/%s' % task.id,
                                    params={'field':'owner', 'owner' : 'Mowbray', 'authenticator':authenticator}, status=assign)
                except:
                    print "line: %d, user: %s, action: assign, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                
                tl.destroySelf()
                task.destroySelf()

    def test_task_owner_security(self):
        """ Tests all possible security settings for task owner actions based
on a security matrix.

        Actions covered in these tests:
        task_view
        task_comment
        task_change_status
        task_edit

        """

        f = open("tasktracker/tests/data/taskowner_security.csv")
        security_levels = ['not even see this list', 'view this list', 'and claim tasks', 'and create new tasks', 'and edit any task']
        users = ['admin', 'member', 'auth']
        line_no = 0
        for line in f:
            line_no += 1
            fields = line[:-1].split(",")
            project_level, member_level, other_level = fields[0:3]
            member_level = security_levels.index(member_level)
            other_level = security_levels.index(other_level)
            fields = fields[3:]
            for user in users:
                def status_for_action(action):
                    status = 200
                    if not action:
                        status = 403
                    return status
                _, view, comment, status, edit = [status_for_action(x == 'Y') for x in fields[:5]]
                fields = fields[5:]

                app = self.getApp(user, project_permission_level = project_level)
                tl = self.create_tasklist('fleem', member_level, other_level)
                #create a task programmatically (assigned to user)
                task = self.create_task(title='morx', task_listID=tl.id, owner=user)

                #test viewing
                try:
                    res = app.get(url_for(controller='task', action='show', id=task.id), status=view)
                except:
                    print "line: %d, user: %s, action: view, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                authenticator = self._get_authenticator(app)

                #test commenting
                try:
                    res = app.post(url_for(controller='task', action='comment', id=task.id, text='comment text'), status=comment)
                except:

                    print "line: %d, user: %s, action: comment, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise

                #test status
                try:
                    res = app.post('/task/change_field/%s' % task.id,
                                    params={'field':'status', 'status':'true', 'authenticator':authenticator}, status=status)
                except:
                    print "line: %d, user: %s, action: status, member_level %s, other_level %s" % (line_no, user, security_levels[member_level], security_levels[other_level])
                    raise
