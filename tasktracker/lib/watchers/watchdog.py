from tasktracker.models import *

from pylons import c
from routes.util import url_for
from tasktracker.events import fire

class Snapshot(object):
    pass

class Watchdog:
    @classmethod
    def snapshotSQLObject(cls, obj):
        out = Snapshot()
        columns = obj.__class__.sqlmeta.columns
        for column in columns.keys():
            setattr(out,column,getattr(obj, column))

        return out

    @classmethod
    def sendMail(cls, username, message):
        to = c.usermapper(username).email_address #START HERE TO FIXME
        mail = OutgoingEmail(envelope_to_address = to, envelope_from_address = 'test@example.com', message=message)
        return mail

    def before(self, params):
        pass
    def after(self, params):
        pass

class TaskWatchdog(Watchdog):
    def before(self, params):
        self.task = Task.get(int(params['id'])) 
        self.pre_task = self.snapshotSQLObject(self.task)

    def after(self, params):
        pass
        #notify("task modified", pre = self.pre_task, post = self.task)

class TaskMoveWatchdog(TaskWatchdog):
    pass #we don't actually want to watch moves yet

class TaskCreateWatchdog(Watchdog):
    def after(self, params):
        self.task = Task.get(int(params['id'])) 
        fire("Task Created", task = self.task)

class TaskCommentWatchdog(TaskWatchdog):
    pass

class TaskUpdateWatchdog(TaskWatchdog):
    
    def after(self, params):
        self.task = Task.get(int(params['id'])) 
        fire("Task Updated", pre_task = self.pre_task, task = self.task)

