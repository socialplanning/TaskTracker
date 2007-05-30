from tasktracker.tests import *
from tasktracker.models import *

class TestExportController(TestController):
    def test_index(self):
        # FIXME: what username should I use?
        app = self.getApp('admin')
        tlist = self.create_tasklist("export_list")
        Task(title="Task A", text="This is Task A",
             task_list=tlist)
        t = Task(title="Task B", text="This is Task B",
             task_list=tlist, statusID='done')
        response = app.get(url_for(controller='export', id=tlist.id))
        # Test response...
        response.mustcontain(
            '<ol class="xoxo">',
            'Task A',
            '<del>Task B',
            )
        response = app.get(url_for(controller='export', id=self.task_list.id))
        response.mustcontain(
            '<ol class="xoxo">',
            'Task 1',
            'Task 2',
            'dtcreated',
            )

    def test_tasklists(self):
        app = self.getApp('admin')
        tlist = self.create_tasklist("export_list")
        t2 = self.create_tasklist("export_2")
        response = app.get(url_for(controller='export', action="show_tasklists"))
        # Test response...
        response.mustcontain(
            '<ul class="xoxo">',
            'export_list',
            'export_2'
            )


