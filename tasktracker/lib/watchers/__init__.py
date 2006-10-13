from tasktracker.models import *

from pylons import c

class Watcher:
    @classmethod
    def snapshotSQLObject(cls, obj):
        out = {}
        columns = obj.__class__.sqlmeta.columns
        for column in columns.keys():
            out[column] = getattr(obj, column)

        return out

    def before(self, params):
        pass
    def after(self, params):
        pass

class TaskWatcher(Watcher):
    def before(self, params):
        task = Task.get(int(params['id'])) 
        self.pre_task = self.snapshotSQLObject(task)


class TaskMoveWatcher(Watcher):
    pass #we don't actually want to watch moves yet


class TaskCreateWatcher(Watcher):
    def after(self, params):
        report = """
A new task was created in the task list %s that you were watching. 

Creator: %s
Title: %s
%s

        """ % (c.task.task_list.title, c.task.creator, c.task.title, c.task.text)

        print report
