from tasktracker.tests import *

class TestExportController(TestController):
    def test_index(self):
        # FIXME: what username should I use?
        app = self.getApp('maria')
        list_id = self.make_list(app)
        response = app.get(url_for(controller='export', id=list_id))
        # Test response...
        print response
        assert 0

    def make_list(self, app):
        res = app.get(url_for(controller='tasklist', action='show_create'))
        form = res.forms[0]
        form['title'] = 'export list'
        form['text'] = 'export body'
        res = form.submit()
        location = res.header('location')
        id = int(location.split('/')[-1])
        return id
