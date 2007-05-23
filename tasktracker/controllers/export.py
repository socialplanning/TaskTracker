# See http://microformats.org/wiki/xoxo for format of export

from tasktracker.lib.base import *

class ExportController(BaseController):

    @authenticate
    @attrs(action='tasklist_show', readonly=True)
    @catches_errors
    def index(self, id):
        # FIXME: is it actually okay to export old lists?  Probably not...
        c.task_list = safe_get(TaskList, id, check_live=True)
        c.tasks = [
            task for task in c.task_list.visibleTasks()
            if c.parent is None]
        return render_response('export.myt')

