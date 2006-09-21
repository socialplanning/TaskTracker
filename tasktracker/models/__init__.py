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

def _index(index):
    if index is None:
        index = 0
    else:
        index += 1
    return index

def _task_sort_index(task_listID, status='uncompleted', skip=None):
    """
    Returns an index which is guaranteed to be greater than all live  indexes in 
    the same list with the same status.

    """
    return _index(Task.select(
            AND(Task.q.task_listID==task_listID, 
                Task.q.status==status, 
                Task.q.id != skip,
                Task.q.live == True
                )).max('sort_index'))


class Task(SQLObject):
    class sqlmeta:
        defaultOrder = 'sort_index'

    def _create(self, id, **kwargs):
        kwargs['sort_index'] = _task_sort_index(kwargs['task_listID']) or 0
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
        new_index = _task_sort_index(self.task_listID, status=self.status, skip=self.id)
        self.sort_index = new_index


class Comment(SQLObject):
    class sqlmeta:
        defaultOrder = 'date'

    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol()
    text = StringCol()
    task = ForeignKey("Task")

def _task_list_sort_index():
    return _index(TaskList.selectBy(live=True).max('sort_index'))

class TaskList(SQLObject):
    class sqlmeta:
        defaultOrder = 'sort_index'

    created = DateTimeCol(default=datetime.datetime.now)
    title = StringCol()
    live = BoolCol(default=True)
    text = StringCol()
    sort_index = IntCol(default=_task_list_sort_index)
    tasks = MultipleJoin("Task")
