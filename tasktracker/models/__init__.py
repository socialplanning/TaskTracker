## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from sqlobject.sqlbuilder import *
from pylons.database import PackageHub


hub = PackageHub("tasktracker")
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass

# Don't forget to update soClasses, below

import datetime

class OutgoingEmail(SQLObject):
    envelope_from_address = StringCol()
    envelope_to_address = StringCol()
    message = StringCol()
    created = DateTimeCol(default=datetime.datetime.now)

class Watcher(SQLObject):
    username = StringCol()
    task = ForeignKey("Task")
    task_list = ForeignKey("TaskList")

class Status(SQLObject):
    name = StringCol()
    project = ForeignKey("Project")

    @classmethod
    def lookup(cls, name, project_id):
        return Status.selectBy(name=name, projectID=project_id)

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
            role = Role.selectBy(name=name)
            if not role.count():
                print "Bad role %s" % name
                return 0
            Role.levels[name] = role[0].level
        return Role.levels[name]

class Project(SQLObject):
    title = StringCol()
    create_list_permission = IntCol(default=0)
    initialized = BoolCol(default=False)
    task_lists = MultipleJoin("TaskList")
    statuses = MultipleJoin("Status")

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

    index = DatabaseIndex(task_list, username, unique=True)

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


def _task_sort_index():
    index = Task.selectBy(live=True).max('sort_index')
    if index is None:
        return 0
    else:
        return index + 1

class Task(SQLObject):
    class sqlmeta:
        defaultOrder = 'sort_index'

    created = DateTimeCol(default=datetime.datetime.now)
    creator = StringCol(default="")
    deadline = DateTimeCol(default=None)
    title = StringCol()
    text = StringCol()
    live = BoolCol(default=True)    
    status = StringCol()

    comments = MultipleJoin("Comment")
    task_list = ForeignKey("TaskList")
    private = BoolCol(default=False)
    owner = StringCol(default="")
    watchers = MultipleJoin("Watcher")
    sort_index = IntCol()

    parent = ForeignKey("Task")
    children = MultipleJoin("Task", joinColumn='parent_id', orderBy='sort_index')

    def isWatchedBy(self, username):
        return Watcher.selectBy(username=username, task=self.id).count() > 0

    def _create(self, id, **kwargs):
        if 'task_list' in kwargs:
            kwargs['task_listID'] = kwargs.pop('task_list').id

        if not kwargs.has_key('status'):
            project = TaskList.get(kwargs['task_listID']).project
            assert len(project.statuses)
            kwargs['status'] = project.statuses[0].name

        kwargs['sort_index'] = _task_sort_index()
        kwargs.setdefault('parentID', 0)
        kwargs['live'] = True
        SQLObject._create(self, id, **kwargs)


    def _set_live(self, value):
        if getattr(self, 'id', None):
            for task in self.children:
                task.live = value
        self._SO_set_live(value)

    def moveToTop(self):
        #top-level case
        if self.parentID == 0:
            tasks = self.task_list.topLevelTasks()
        else:
            tasks = self.parent.children

        i = 1
        for task in tasks:
            if task == self:
                task.sort_index = 0
            else:
                task.sort_index = i
                i += 1

    def moveBelow(self, new_sibling):
        if self.parentID == 0:
            tasks = self.task_list.topLevelTasks()
        else:
            tasks = self.parent.children

        new_index = new_sibling.sort_index
        i = 1
        for task in tasks:
            if task == self:
                task.sort_index = new_index + 1
            elif task.sort_index > new_index:
                task.sort_index += 1

    def liveChildren(self):
        from tasktracker.lib.helpers import has_permission
        return [c for c in self.children if c.live and has_permission('task', 'view', id=c.id)]

    def isOwnedBy(self, username):
        return self.owner == username            

    def changeStatus(self, newStatus):
        self.status = newStatus
        return self.status

    def depth(self):
        depth = 0
        p_id = self.parentID
        while p_id:
            depth += 1
            p_id = Task.get(p_id).parentID
        return depth

class Comment(SQLObject):
    class sqlmeta:
        defaultOrder = 'date'

    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol()
    text = StringCol()
    task = ForeignKey("Task")

def _task_list_sort_index():
    index = TaskList.select().max('sort_index')
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
    watchers = MultipleJoin("Watcher")
    security_policy = ForeignKey("SimpleSecurityPolicy", default=0)

    def isWatchedBy(self, username):
        return Watcher.selectBy(username=username, task_list=self.id).count() > 0

    def topLevelTasks(self):
        from tasktracker.lib.helpers import has_permission
        return [c for c in Task.selectBy(parentID=0, live=True, task_listID=self.id) if has_permission('task', 'view', id=c.id)]

    def uncompletedTasks(self):
        return list(Task.select(AND(Task.q.status != 'done', Task.q.task_listID == self.id)))
    
    def completedTasks(self):
        return list(Task.select(AND(Task.q.status == 'done', Task.q.task_listID == self.id)))

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

    def isOwnedBy(self, username):
        return TaskListOwner.selectBy(username = username, task_listID = self.id).count()

soClasses = [
    Status,
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
    Watcher,
    OutgoingEmail
    ]
