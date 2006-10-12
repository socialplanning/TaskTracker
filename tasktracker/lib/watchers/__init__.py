from tasktracker.models import *

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
    def after(self, params):
        self.task = Task.get(int(params['id'])) 

    def before(self, params):
        task = Task.get(int(params['id'])) 
        self.pre_task = self.snapshotSQLObject(task)


class TaskMoveWatcher(TaskWatcher):
    def after(self, params):
        TaskWatcher.after(self, params)
        print "was: %s" % self.pre_task
        print "is: %s" % self.task
