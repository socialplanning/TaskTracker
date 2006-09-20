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

def _task_sort_index(task_listID):
    return _index(Task.selectBy(task_listID=task_listID).max('sort_index'))


class Task(SQLObject):
    class sqlmeta:
        defaultOrderBy = 'sort_index'

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

class Comment(SQLObject):
    class sqlmeta:
        defaultOrderBy = 'date'

    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol()
    text = StringCol()
    task = ForeignKey("Task")

def _task_list_sort_index():
    return _index(TaskList.select().max('sort_index'))

class TaskList(SQLObject):
    class sqlmeta:
        defaultOrderBy = 'sort_index'

    created = DateTimeCol(default=datetime.datetime.now)
    title = StringCol()
    live = BoolCol(default=True)
    text = StringCol()
    sort_index = IntCol(default=_task_list_sort_index)
    tasks = MultipleJoin("Task")
