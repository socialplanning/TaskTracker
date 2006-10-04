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

    def _getElementsByTagName(self, body, tagname):
        elements = []
        start = -1
        while 1:
            start = body.find('<' + tagname, start + 1)
            if start == -1:
                break
            end = body.find('>', start)
            elements.append(body[start:end+1])

        return elements


    def test_auth_role(self):
        tl = self.create_tasklist('testing the auth role')


        #set security such that only task owner can change status
        found = False
        for perm in tl.permissions:
            if perm.action.action == "task_change_status":
                found = True
                perm.min_level = Role.getLevel("TaskOwner")
        assert found

        #add a task assigned to 'auth'
        task1 = Task(title='Fleem', text='x', owner='auth', task_listID=tl.id)
        #add a task not assigned to 'auth'
        task2 = Task(title='Fleem', text='x', owner='admin', task_listID=tl.id)

        app = self.getApp('auth')

        res = app.get(url_for(
                controller='tasklist', action='view', id=tl.id))

        res.mustcontain('testing the auth role')

        spanTags = self._getElementsByTagName(res.body, 'span')

        found = False
        for span in spanTags:
            if 'label_%d' % task1.id in span:
                #the label for task1 must be hidden
                assert 'display:none' in span
                found = True
                break


        assert found

        selectTags = self._getElementsByTagName(res.body, 'select')
        found = False
        for select in selectTags:
            #there is no select for task2, because we can't edit it.
            assert 'status_%d' % task2.id not in select 

            #but there is one for task1
            if 'status_%d' % task1.id in select:
              found = True

        assert found

        task1.destroySelf()
        task2.destroySelf()
        tl.destroySelf()
