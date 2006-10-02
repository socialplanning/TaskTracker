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
        res2 = app.get('/task/change_status/%s?new_status=%s' % (task.id, 'done'))
        assert task.status == done
     
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
        res = form.submit()

        #Creating a new task should redirect you to the list of tasks.

        location = res.header_dict['location']
        assert location.startswith('/tasklist/view/')

        id = int(location[location.rindex('/') + 1:])

        assert id == task_listID

        res = res.follow()

        res.mustcontain('The new task title')
    

