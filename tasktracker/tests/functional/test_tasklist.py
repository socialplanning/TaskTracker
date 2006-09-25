from tasktracker.tests import *
from tasktracker.models import *

class TestTaskListController(TestController):
        
    def test_show_create(self):
        res = self.app.get(url_for(
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
