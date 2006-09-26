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

class Role(SQLObject):
    title = StringCol()
    level = IntCol()

    levels = {}

    @classmethod
    def getLevel(cls, title):
        if not Role.levels.has_key(title):
            Role.levels[title] = Role.selectBy(title=title)[0].level
        return Role.levels[title]

class Project(SQLObject):
    title = StringCol()
    create_list_permission = IntCol(default=0)
    initialized = BoolCol(default=False)
    task_lists = MultipleJoin("TaskList")

    @classmethod
    def getProject(cls, title):
        projects = list(Project.selectBy(title=title))
        if not projects:
            return Project(title=title)
        else:
            return projects[0]

class TaskListOwner(SQLObject):
    username = StringCol(length=100)
    task_list = ForeignKey('TaskList')
    sire = StringCol(length=100)

    index = DatabaseIndex('username', 'task_list', unique=True)

class Permission(SQLObject):
    action = StringCol()
    min_level = IntCol()

class TaskListPermission(SQLObject):
    permission = ForeignKey("Permission")
    task_list = ForeignKey("TaskList")
    min_level = IntCol()

    def _create(self, id, **kwargs):
        if 'min_level' in kwargs:
            if kwargs['min_level'] > \
                    Permission.get(kwargs['permission_ID']).min_level:
                raise ValueError("Invalid permission settings.")
        SQLObject._create(self, id, **kwargs)

class Task(SQLObject):
    class sqlmeta:
        defaultOrder = 'sort_index'

    def _create(self, id, **kwargs):
        if 'task_list' in kwargs:
            kwargs['task_listID'] = kwargs.pop('task_list').id
        kwargs['sort_index'] = self._next_sort_index(kwargs['task_listID'])
        SQLObject._create(self, id, **kwargs)

    created = DateTimeCol(default=datetime.datetime.now)
    deadline = DateTimeCol(default=None)
    title = StringCol()
    text = StringCol()
    live = BoolCol(default=True)    
    status = EnumCol(default='uncompleted', enumValues=('completed', 'uncompleted'))    
    sort_index = IntCol()
    comments = MultipleJoin("Comment")
    task_list = ForeignKey("TaskList")
    private = BoolCol(default=False)
    owner = StringCol()

    def isOwnedBy(self, username):
        return self.owner == username            

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
    permissions = MultipleJoin("TaskListPermission")
    project = ForeignKey("Project")
    owners = MultipleJoin("TaskListOwner")

    def isOwnedBy(self, username):
        return TaskListOwner.selectBy(username = username, task_listID = self.id).count()

    def uncompletedTasks(self):
        return [x for x in self.tasks if x.status == 'uncompleted']

    def completedTasks(self):
        return [x for x in self.tasks if x.status == 'completed']

soClasses = [
    Role,
    Project,
    Permission,
    TaskListPermission,
    Task,
    TaskList,
    TaskListOwner,
    Comment,
    ]
