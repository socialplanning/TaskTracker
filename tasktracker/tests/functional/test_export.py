from tasktracker.tests import *

class TestExportController(TestController):
    def test_index(self):
        # FIXME: what username should I use?
        app = self.getApp('admin')
        list = self.create_tasklist("export_list")
        response = app.get(url_for(controller='export', id=list.id))
        # Test response...
        print response
        assert 0

