from tasktracker.tests import *
from tasktracker.models import *

class TestTaskController(TestController):
    def test_index(self):
        lists = list(TaskList.select())

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='tasklist'))
        for l in lists:
            res.mustcontain(l.title)
        res = res.click(lists[0].title)
        res.mustcontain(lists[0].title)
        task = lists[0].tasks[0]
        assert task.status == 'not done'
        res2 = app.get('/task/change_status/%s?status=%s' % (task.id, 'done'))
        assert task.status == "done"
     
    def test_show_create(self):
        task_listID = TaskList.select()[0].id

        app = self.getApp('admin')

        res = app.get(url_for(
                controller='task', action='show_create', 
                task_listID=task_listID
                ))

        form = res.forms[0]

        form['title'] = 'The new task title'
        form['text'] = 'The new task body'
        form['deadline'] = '10/10/2029'
        res = form.submit()

        #Creating a new task should redirect you to the list of tasks.

        location = res.header_dict['location']
        assert location.startswith('/tasklist/view/')

        id = int(location[location.rindex('/') + 1:])

        assert id == task_listID

        res = res.follow()

        res.mustcontain('The new task title')
    

    def create_tasklist(self, title):
        app = self.getApp('admin')
        res = app.get(url_for(
                controller='tasklist', action='show_create'))

        form = res.forms[0]
        
        form.fields['title'][0].value = title
        form.fields['mode'][0].value = 'simple'
        policy = form.fields['policy'][0]
        policy.value = policy.options[1][0] #medium
        
        res = form.submit()
        res = res.follow()
        
        path = res.req.path_info
        new_task_list_id = int(path[path.rindex('/') + 1:])

        task_list = TaskList.get(new_task_list_id)
        return task_list

    def test_index(self):
        list = self.create_tasklist('testing the "auth" role')

        #add a task assigned to 'auth'
        t = Task(title='Fleem', text='x', owner='auth', task_listID=list.id)

        app = self.getApp('auth')

        res = app.get(url_for(
                controller='tasklist', action='view', id=list.id))
        

        res.mustcontain('testing the &quot;auth&quot; role')

        t.destroySelf()
        list.destroySelf()
