from tasktracker.models import *

from pylons import c
from routes.util import url_for

class Watchdog:
    @classmethod
    def snapshotSQLObject(cls, obj):
        out = {}
        columns = obj.__class__.sqlmeta.columns
        for column in columns.keys():
            out[column] = getattr(obj, column)

        return out

    @classmethod
    def sendMail(cls, username, message):
        to = c.usermapper(username).email_address
        OutgoingEmail(envelope_to_address = to, envelope_from_address = 'test@example.com', message=message)


    def before(self, params):
        pass
    def after(self, params):
        pass

class TaskWatchdog(Watchdog):
    def before(self, params):
        task = Task.get(int(params['id'])) 
        self.pre_task = self.snapshotSQLObject(task)


class TaskMoveWatchdog(Watchdog):
    pass #we don't actually want to watch moves yet


class TaskCreateWatchdog(Watchdog):
    def after(self, params):
        message = """
Subject: %s: Task created in list %s

A new task was created in the task list %s that you were watching. 

Creator: %s
Title: %s
%s

        """ % (c.project, c.task.task_list.title, c.task.task_list.title, c.task.creator, c.task.title, c.task.text)

        for watcher in c.task.task_list.watchers:
            self.sendMail(watcher.username, message)

class TaskCommentWatchdog(Watchdog):
    def after(self, params):

        message = """
Subject: %s: New comment on %s

%s commented on the task entitled '%s':
%s

To reply, go to %s
        """ % (c.project, c.task.title, c.comment.user, c.task.title, c.comment.text, url_for(action="view", controller="task", id=c.task.id, qualified=True))

        for watcher in c.task.watchers:
            self.sendMail(watcher.username, message)

        for watcher in c.task.task_list.watchers:
            self.sendMail(watcher.username, message)

class TaskUpdateWatchdog(TaskWatchdog):
    def after(self, params):
        message = """
Subject: %s: Task %s changed

The task named %s has been altered. 

To view the changes, go to %s
        """ % (c.project, c.task.title, c.task.title, url_for(action="view", controller="task", id=c.task.id, qualified=True))

        for watcher in c.task.watchers:
            self.sendMail(watcher.username, message)

        for watcher in c.task.task_list.watchers:
            self.sendMail(watcher.username, message)
