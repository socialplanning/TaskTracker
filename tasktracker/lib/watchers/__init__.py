from tasktracker.models import *

from pylons import c

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
