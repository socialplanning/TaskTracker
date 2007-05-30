# See http://microformats.org/wiki/xoxo for format of export

from tasktracker.lib.base import *
from tasktracker.controllers.tasklist import TasklistController

class ExportController(BaseController):

    @attrs(action_noun="tasklist", action='show', readonly=True)
    @catches_errors
    def index(self, id, *args, **kwargs):
        # FIXME: is it actually okay to export old lists?  Probably not...
        c.task_list = safe_get(TaskList, id, check_live=True)
        c.tasks = c.task_list.topLevelTasks()
        return render_response('export.myt')

    @attrs(action="open", readonly=True)
    @catches_errors
    def show_tasklists(self, *args, **kwargs):
        c.tasklists = TasklistController._getVisibleTaskLists(c.username)
        return render_response('export_tasklists.myt')
