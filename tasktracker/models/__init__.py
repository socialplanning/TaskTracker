## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from pylons.database import PackageHub
hub = PackageHub("tasktracker")
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass


import datetime

class Task(SQLObject):
    class sqlmeta:
        defaultOrder = 'sort_index'

    def _create(self, id, **kwargs):
        if 'task_list' in kwargs:
            kwargs['task_listID'] = kwargs.pop('task_list').id
        kwargs['sort_index'] = self._next_sort_index(kwargs['task_listID'])
        SQLObject._create(self, id, **kwargs)

    created = DateTimeCol(default=datetime.datetime.now)
    title = StringCol()
    text = StringCol()
    live = BoolCol(default=True)    
    status = EnumCol(default='uncompleted', enumValues=('completed', 'uncompleted'))    
    sort_index = IntCol()
    comments = MultipleJoin("Comment")
    task_list = ForeignKey("TaskList")

    @classmethod
    def oppositeStatus(cls, status):
        if status == 'completed':
            return 'uncompleted'
        else:
            return 'completed'

    def toggleStatus(self):
        self.status = self.oppositeStatus(self.status)
        return self.status

    def moveToBottom(self):
        """ Call this *after* toggleStatus """
        new_index = self._next_sort_index(self.task_listID, status=self.status, skip=self.id)
        self.sort_index = new_index

    @classmethod
    def _next_sort_index(cls, task_listID, status='uncompleted', skip=None):
        """
        Returns an index which is guaranteed to be greater than all live  indexes in 
        the same list with the same status.
        """
        index = cls.select(
            AND(cls.q.task_listID==task_listID, 
                cls.q.status==status, 
                cls.q.id != skip,
                cls.q.live == True
                )).max('sort_index')
        if index is None:
            return 0
        else:
            return index + 1

class Comment(SQLObject):
    class sqlmeta:
        defaultOrder = 'date'

    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol()
    text = StringCol()
    task = ForeignKey("Task")

def _task_list_sort_index():
    index = TaskList.selectBy(live=True).max('sort_index')
    if index is None:
        return 0
    else:
        return index + 1

class TaskList(SQLObject):
    class sqlmeta:
        defaultOrder = 'sort_index'

    created = DateTimeCol(default=datetime.datetime.now)
    title = StringCol()
    live = BoolCol(default=True)
    text = StringCol()
    sort_index = IntCol(default=_task_list_sort_index)
    tasks = MultipleJoin("Task")

    def uncompletedTasks(self):
        return [x for x in self.tasks if x.status == 'uncompleted']

    def completedTasks(self):
        return [x for x in self.tasks if x.status == 'completed']

soClasses = [
    Task,
    TaskList,
    Comment,
    ]
