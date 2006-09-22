from tasktracker.tests import *
from tasktracker.models import *

class TestTaskController(TestController):
    def test_index(self):
        lists = list(TaskList.select())
        res = self.app.get(url_for(
                controller='tasklist'))
        for l in lists:
            res.mustcontain(l.title)
        res = res.click(lists[0].title)
        res.mustcontain(lists[0].title)
        task = lists[0].tasks[0]
        assert task.status == 'uncompleted'
        res2 = self.app.get('/task/complete_task/%s' % task.id)
        assert task.status == 'completed'
        
