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
    class sqlmeta:
        defaultOrder = '-level'

    name = StringCol()
    description = StringCol()
    level = IntCol()

    levels = {}

    @classmethod
    def getLevel(cls, name):
        if not Role.levels.has_key(name):
            Role.levels[name] = Role.selectBy(name=name)[0].level
        return Role.levels[name]

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
    _cacheValue = False
    username = StringCol(length=100)
    task_list = ForeignKey('TaskList')
    sire = StringCol(length=100)

    index = DatabaseIndex('username', 'task_list', unique=True)

class SecurityPolicyAction(SQLObject):
    simple_security_policy = ForeignKey("SimpleSecurityPolicy")
    action = ForeignKey("Action")
    min_level = IntCol()                        

class SimpleSecurityPolicy(SQLObject):
    name = StringCol()
    actions = MultipleJoin('SecurityPolicyAction')

class Action(SQLObject):
    action = StringCol()
    question = StringCol()
    roles = RelatedJoin('Role')

class TaskListPermission(SQLObject):
    _cacheValue = False
    action = ForeignKey("Action")
    task_list = ForeignKey("TaskList")
    min_level = IntCol()
    
    def _create(self, id, **kwargs):
        if 'min_level' in kwargs:
            # make sure value is sane
            if kwargs['min_level'] > \
                    Action.get(kwargs['action'].id).roles[0].level:
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
    owner = StringCol(default="")

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
    _cacheValue = False
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

    security_policy = ForeignKey("SimpleSecurityPolicy", default=0)

    def set(self, init=False, **kwargs):
        if init:
            SQLObject.set(self, **kwargs)
            return

        conn = hub.getConnection()
        trans = conn.transaction()

        params = self._clean_params(kwargs)
        SQLObject.set(self, **params)
        self._setup_actions(kwargs)

        trans.commit()

    def _clean_params(self, kwargs):

        params = {}
        allowed_params = ("title", "text", "projectID")
        for param in allowed_params:
            if kwargs.has_key(param):
                params[param] = kwargs[param]

        return params

    def _setup_actions(self, kwargs):

        for permission in self.permissions:
            permission.destroySelf()

        if kwargs.get('mode') == 'simple':
            ss = SimpleSecurityPolicy.get(int(kwargs['policy']))
            actions = SecurityPolicyAction.selectBy(simple_security_policy=ss)
            for action in actions:
                p = TaskListPermission(task_listID=self.id,
                                       min_level=action.min_level, action=action.action)
        else:
            for action in Action.select():
                value = kwargs.get('action_%s' % action.action, None)
                if value:
                    role = Role.get(value)
                else:
                    role = action.roles[-1]
                p = TaskListPermission(task_listID=self.id, min_level=role.level, action=action)


    def rescuePermissions(self):
        print "Rescuing permissions.  This is very, very bad."
        for action in Action.select():
            TaskListPermission(task_listID=self.id, min_level=action.roles[0].level, action=action)

    def _create(self, id, **kwargs):
        username = kwargs.pop('username')
        params = self._clean_params(kwargs)

        conn = hub.getConnection()
        trans = conn.transaction()

        SQLObject._create(self, id, init=True, **params)

        self._setup_actions(kwargs)

        TaskListOwner(username=username, sire=username, task_listID = self.id)

        trans.commit()



    @classmethod
    def getVisibleTaskLists(cls, level):
        return TaskList.select(
            AND(TaskList.q.live==True, 
                TaskListPermission.q.task_listID == TaskList.q.id, 
                TaskListPermission.q.actionID == Action.q.id, 
                Action.q.action == 'tasklist_view',
                TaskListPermission.q.min_level >= level))
    


    def isOwnedBy(self, username):
        return TaskListOwner.selectBy(username = username, task_listID = self.id).count()

    def uncompletedTasks(self):
        return [x for x in self.tasks if x.status == 'uncompleted']

    def completedTasks(self):
        return [x for x in self.tasks if x.status == 'completed']

soClasses = [
    Role,
    Project,
    Action,
    SimpleSecurityPolicy,
    SecurityPolicyAction,
    TaskListPermission,
    Task,
    TaskList,
    TaskListOwner,
    Comment,
    ]
