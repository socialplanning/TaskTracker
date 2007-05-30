# See http://microformats.org/wiki/xoxo for format of export

from tasktracker.lib.base import *

class ExportController(BaseController):

    @attrs(action_noun="tasklist", action='show', readonly=True)
    @catches_errors
    def index(self, id, *args, **kwargs):
        # FIXME: is it actually okay to export old lists?  Probably not...
        c.task_list = safe_get(TaskList, id, check_live=True)
        c.tasks = [
            task for task in c.task_list.visibleTasks()
            if not c.parent]
        return render_response('export.myt')

