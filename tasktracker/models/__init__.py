
# Copyright (C) 2006 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 
# 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301
# USA

## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from sqlobject.sqlbuilder import *
from pylons.database import PackageHub
from pylons import c

hub = PackageHub("tasktracker")
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass

# Don't forget to update soClasses, below

import datetime

def create_version(klass, obj):
    args = {}
    columns = klass.sqlmeta.columns
    for column in columns.keys():
        if column not in ["version", "id", "origID"]:
            args[column] = getattr(obj, column)

    args['version'] = obj.updated
    args['orig'] = obj.id

    return klass(**args)

class OutgoingEmail(SQLObject):
    envelope_from_address = StringCol()
    envelope_to_address = StringCol()
    message = StringCol()
    created = DateTimeCol(default=datetime.datetime.now)

class Notification(SQLObject):
    username = StringCol()
    task = ForeignKey("Task")
    task_list = ForeignKey("TaskList")
    created = DateTimeCol(default=datetime.datetime.now)
    notified = BoolCol(default=False)
    importance = IntCol()
    regardingTaskVersion = ForeignKey("TaskVersion")
    regardingTaskListVersion = ForeignKey("TaskListVersion")

class TaskVersion(SQLObject):

    orig = ForeignKey("Task")

    version = DateTimeCol(default=datetime.datetime.now)

    deadline = DateTimeCol()
    live = BoolCol(default=True)    
    owner = StringCol()
    priority = StringCol(default="None")
    private = BoolCol()
    sort_index = IntCol()
    status = StringCol()
    task_list = ForeignKey("TaskList")
    text = StringCol()
    title = StringCol()
    updated = DateTimeCol()
    updated_by = StringCol()

class TaskListVersion(SQLObject):
    orig = ForeignKey("TaskList")

    version = DateTimeCol(default=datetime.datetime.now)

    updated = DateTimeCol()
    updated_by = StringCol()
    title = StringCol()
    live = BoolCol()
    text = StringCol()
    sort_index = IntCol()

class Watcher(SQLObject):
    username = StringCol()
    task = ForeignKey("Task")
    task_list = ForeignKey("TaskList")
    interest_level = IntCol()

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
    action = StringCol(unique=True)
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



    children = MultipleJoin("Task", joinColumn='parent_id', orderBy='sort_index')
    comments = MultipleJoin("Comment")
    created = DateTimeCol(default=datetime.datetime.now)
    creator = StringCol(default="")
    deadline = DateTimeCol(default=None)
    live = BoolCol(default=True)    
    owner = StringCol(default="")
    parent = ForeignKey("Task")
    priority = StringCol(default="None")
    private = BoolCol(default=False)
    sort_index = IntCol()
    status = StringCol()
    task_list = ForeignKey("TaskList")
    text = StringCol()
    title = StringCol()
    updated = DateTimeCol(default=datetime.datetime.now)
    updated_by = StringCol()
    versions = MultipleJoin("TaskVersion", joinColumn="orig_id")
    watchers = MultipleJoin("Watcher")

    def isWatchedBy(self, username):
        return Watcher.selectBy(username=username, task=self.id).count() > 0

    def _create(self, id, **kwargs):
        if 'task_list' in kwargs:
            kwargs['task_listID'] = kwargs.pop('task_list').id

        if not kwargs.has_key('status'):
            project = TaskList.get(kwargs['task_listID']).project
            assert len(project.statuses)
            kwargs['status'] = project.statuses[0].name

        kwargs['updated_by'] = c.username
        kwargs['sort_index'] = _task_sort_index()
        kwargs.setdefault('parentID', 0)
        kwargs['live'] = True
        SQLObject._create(self, id, **kwargs)

    def set(self, **kwargs):
        kwargs['updated_by'] = c.username
        kwargs['updated'] = datetime.datetime.now()
        if getattr(self, 'id', None):
            create_version(TaskVersion, self)
        SQLObject.set(self, **kwargs)

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
        return [c for c in self.children if c.live and has_permission('task', 'show', id=c.id)]

    def isOwnedBy(self, username):
        return self.owner == username            

    def changeStatus(self, newStatus):
        self.status = newStatus
        return self.status

    def depth(self):
        depth = 0
        p_id = int(self.parentID)
        while p_id:
            depth += 1
            p_id = int(Task.get(p_id).parentID)
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

class User(SQLObject):
    username = StringCol()
    password = StringCol()

class TaskList(SQLObject):
    _cacheValue = False
    class sqlmeta:
        defaultOrder = 'sort_index'

    live = BoolCol(default=True)
    owners = MultipleJoin("TaskListOwner")
    permissions = MultipleJoin("TaskListPermission")
    project = ForeignKey("Project")
    security_policy = ForeignKey("SimpleSecurityPolicy", default=0)
    sort_index = IntCol(default=_task_list_sort_index)
    tasks = MultipleJoin("Task")
    text = StringCol()
    title = StringCol()
    updated = DateTimeCol(default=datetime.datetime.now)
    updated_by = StringCol()
    versions = MultipleJoin("TaskVersion", joinColumn="orig_id")
    watchers = MultipleJoin("Watcher")
    created = DateTimeCol(default=datetime.datetime.now)

    def isWatchedBy(self, username):
        return Watcher.selectBy(username=username, task_list=self.id).count() > 0

    def topLevelTasks(self):
        from tasktracker.lib.helpers import has_permission
        return [c for c in Task.selectBy(parentID=0, live=True, task_listID=self.id) if has_permission('task', 'show', id=c.id)]

    def uncompletedTasks(self):
        from tasktracker.lib.helpers import has_permission
        return [c for c in Task.select(AND(Task.q.status != 'done', Task.q.task_listID == self.id, Task.q.live == True)) if has_permission('task', 'show', id=c.id)]
    
    def completedTasks(self):
        return list(Task.selectBy(status='done', task_listID=self.id, live=True))

    def set(self, **kwargs):
        kwargs['updated_by'] = c.username
        kwargs['updated'] = datetime.datetime.now()
        if getattr(self, 'id', None):
            create_version(TaskListVersion, self)
        else:
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
        params['updated_by'] = c.username
        conn = hub.getConnection()
        trans = conn.transaction()

        SQLObject._create(self, id, **params)

        self._setup_actions(kwargs)

        TaskListOwner(username=username, sire=username, task_listID = self.id)

        trans.commit()

    def isOwnedBy(self, username):
        return TaskListOwner.selectBy(username = username, task_listID = self.id).count()

soClasses = [
    Action,
    Comment,
    Notification,
    OutgoingEmail,
    Project,
    Role,
    SecurityPolicyAction,
    SimpleSecurityPolicy,
    Status,
    Task,
    TaskList,
    TaskListOwner,
    TaskListPermission,
    TaskListVersion,
    TaskVersion,
    User,
    Watcher,
    ]
