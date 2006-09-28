from tasktracker.tests import *
from tasktracker.models import *

class TestTaskListController(TestController):
        
    def test_show_create(self):

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist', action='show_create'))

        form = res.forms[0]

        form['title'] = 'The new tl title'
        form['text'] = 'The new tl body'
        res = form.submit()

        location = res.header_dict['location']
        assert location.startswith('/tasklist/view/')

        id = int(location[location.rindex('/') + 1:])

        assert id

        res = res.follow()

        res.mustcontain('The new tl title')

        assert TaskList.get(id).text == 'The new tl body'
        
        #clean up: destroy new list
        TaskList.delete(id)

    def test_admin_only_list(self):
        #create a new list that only admins can touch
        task_list = TaskList(title="admin list 1", text="The list", projectID=self.project.id, username='member')

        #log in as a member
        app = self.getApp('member')        

        #make sure it doesn't show up on the index

        res = app.get(url_for(
                controller='tasklist', action='index'))

        assert 'admin list 1' not in res

        #make sure we can't view it.
        res = app.get(url_for(
                controller='tasklist', action='view', id=task_list.id))

        assert 'not_permitted' in res.header_dict['location']

        task_list.destroySelf()

    def test_member_viewable_list(self):
        #create a new list that members can view
        task_list = TaskList(title="member list 1", text="The list", projectID=self.project.id, username='member', action_tasklist_view=Role.selectBy(name='ProjectMember')[0].id)

        #log in as a member
        app = self.getApp('member')        

        res = app.get(url_for(
                controller='tasklist', action='index'))

        assert 'member list 1' in res

        res = res.click('member list 1')

        assert 'member list 1' in res

        #but members cannot create tasks.

        res = res.click('Add a new task')

        assert 'not_permitted' in res.header_dict['location']        

        task_list.destroySelf()
