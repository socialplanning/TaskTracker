
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

from sqlobject import *
from sqlobject.inheritance import InheritableSQLObject
from sqlobject.sqlbuilder import *
from sqlobject.events import *
from pylons.database import PackageHub
from pylons import c
from tasktracker.lib.memoize import memoize

hub = PackageHub("tasktracker", pool_connections=False)
__connection__ = hub

# Don't forget to update soClasses, below

import datetime

def create_version(klass, obj):
    """Stores the old version of an item before it's updated."""
    args = {}
    columns = klass.sqlmeta.columns
    for column in columns.keys():
        if column not in ["updated", "id", "origID"]:
            args[column] = getattr(obj, column)

    obj.updated = datetime.datetime.now()
    args['updated'] = obj.updated
    args['updated_by'] = c.username
    args['origID'] = obj.id

    return klass(**args)

class OutgoingEmail(SQLObject):
    envelope_from_address = StringCol()
    envelope_to_address = StringCol()
    message = StringCol()
    created = DateTimeCol(default=datetime.datetime.now)

class Notification(SQLObject):
    class sqlmeta:
        defaultOrder = 'created'

    username = StringCol()
    task = ForeignKey("Task")
    task_list = ForeignKey("TaskList")
    created = DateTimeCol(default=datetime.datetime.now)
    notified = BoolCol(default=False)
    importance = IntCol()
    oldVersion = ForeignKey("Version")
    triggering_watcher = ForeignKey("Watcher")
    handled = BoolCol(default=False)
    
    def targetType(self):
        if self.taskID:
            return "task"
        else:
            return "task_list"

class Versionable(InheritableSQLObject):
    doneConstruction = BoolCol(default=False)

class Version(InheritableSQLObject):
    """Represents an old version of an item."""

    updated = DateTimeCol()
    updated_by = StringCol()
    orig = ForeignKey("Versionable")

    def nextVersion(self):
        version = Version.select(AND(Version.q.origID == self.orig.id, Version.q.updated > self.updated), limit=1, orderBy=Version.q.updated)
        if version.count():
            return version[0]
        else:
            return self.orig

    def getChangedFields(self):
        next = self.nextVersion()
        columns = self.__class__.sqlmeta.columns
        fields = []
        for column in columns:
            if column not in ["updated", "id", "origID"]:
                if getattr(self, column) != getattr(next, column):
                    fields.append(column.title())

        return fields        

class TaskVersion(Version):

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


class TaskListVersion(Version):

    title = StringCol()
    live = BoolCol()
    text = StringCol()
    sort_index = IntCol()
    initial_assign = IntCol()

class Watcher(SQLObject):
    username = StringCol()
    task = ForeignKey("Task")
    task_list = ForeignKey("TaskList")
    interest_level = IntCol()

    def target(self):
        if self.taskID:
            return self.task
        else:
            return self.task_list

class Status(SQLObject):
    name = StringCol()
    task_list = ForeignKey("TaskList")

    @classmethod
    def lookup(cls, name, task_list_id):
        return Status.selectBy(name=name, task_listID=task_list_id)

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

    @classmethod
    def getByName(cls, name):
        return Role.selectBy(name=name)[0]

class Project(SQLObject):
    title = StringCol()
    task_lists = MultipleJoin("TaskList")

    @classmethod
    def getProject(cls, title):
        projects = list(Project.selectBy(title=title))
        if not projects:
            return Project(title=title)
        else:
            return projects[0]

class TaskListRole(SQLObject):
    _cacheValue = False
    username = StringCol(length=100)
    task_list = ForeignKey('TaskList')
    role = ForeignKey("Role")

    index = DatabaseIndex(task_list, username, role, unique=True)

class Action(SQLObject):
    action = StringCol(unique=True, length=100)
    roles = RelatedJoin('Role')

class TaskListPermission(SQLObject):
    _cacheValue = False
    action = ForeignKey("Action")
    task_list = ForeignKey("TaskList")
    min_level = IntCol()
    
    def _create(self, id, **kwargs):
        if 'min_level' in kwargs:
            # make sure value is sane
            if kwargs['min_level'] > kwargs['action'].roles[0].level:
                raise ValueError("Invalid permission settings.  Trying to create a permission with level %d for action %s, which has roles %s." % (kwargs['min_level'], kwargs['action'].action, [(r.name, r.level) for r in kwargs['action'].roles]))
        super(TaskListPermission, self)._create(id, **kwargs)


def _task_sort_index():
    index = max([t.sort_index for t in Task.selectBy(live=True, doneConstruction=True)] + [0])
    if index is None:
        return 0
    else:
        return index + 1

class Task(Versionable):
    class sqlmeta:
        defaultOrder = 'sort_index'

    version_class = TaskVersion
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
    text = StringCol(default="")
    title = StringCol()
    updated = DateTimeCol(default=datetime.datetime.now)
    updated_by = StringCol()
    versions = MultipleJoin("Version", joinColumn="orig_id", orderBy='updated')
    watchers = MultipleJoin("Watcher")

    def getWatcher(self, username):
        return Watcher.selectBy(username=username, taskID=self.id)[0]

    def isWatchedBy(self, username):
        return Watcher.selectBy(username=username, task=self.id).count() > 0

    def _create(self, id, **kwargs):
        if 'task_list' in kwargs:
            kwargs['task_listID'] = kwargs.pop('task_list').id          

        task_list = TaskList.get(kwargs['task_listID'])

        if kwargs.get('private'):
            assert 'private_tasks' in [f.name for f in task_list.features]

        if not kwargs.get('status', None):
            kwargs['status'] = task_list.statuses[0].name
        assert kwargs['status']

        kwargs['updated_by'] = c.username
        kwargs['sort_index'] = _task_sort_index()
        kwargs.setdefault('parentID', 0)
        kwargs['live'] = True

        if task_list.initial_assign == 0 and not kwargs.get('owner', None):
            kwargs['owner'] = c.username

        super(Task, self)._create(id, **kwargs)
        self.doneConstruction = True

    def set(self, **kwargs):
        kwargs['updated_by'] = c.username
        kwargs['updated'] = datetime.datetime.now()

        super(Task, self).set(**kwargs)

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
        import tasktracker.lib.helpers as h

        return [c for c in self.children if c.live and h.has_permission('task', 'show', id=c.id)]

    def uncompletedChildren(self):
        import tasktracker.lib.helpers as h

        return [c for c in self.children if c.status != 'done' and c.live and h.has_permission('task', 'show', id=c.id)]

    def isOwnedBy(self, username):
        return self.owner == username            

    def changeStatus(self, newStatus):
        self.status = newStatus
        return self.status

    @memoize
    def depth(self):
        depth = 0
        p_id = int(self.parentID)
        while p_id:
            depth += 1
            p_id = int(Task.get(p_id).parentID)
        return depth

    @memoize
    def path(self):
        path = []
        task = self
        while task.parentID:
            path.append(task.sort_index)
            task = task.parent
        path.append(task.sort_index)
        path.reverse()
        return path

    @memoize
    def previousTask(self):
        conn = hub.getConnection()
        trans = conn.transaction()
        tasks = [t[1] for t in sorted([(task.path(), task) for task in Task.selectBy(task_listID=c.task_listID)])]
        trans.commit()

        prev = None
        for task in tasks:
            if task == self:
                return prev
            prev = task
        return prev

    @memoize
    def nextTask(self):

        conn = hub.getConnection()
        trans = conn.transaction()
        tasks = [t[1] for t in reversed(sorted([(task.path(), task) for task in Task.selectBy(task_listID=c.task_listID)]))]
        trans.commit()
        
        next = None
        for task in tasks:
            if task == self:
                return next
            next = task
        return next

    def actions(self):
        return sorted(self.comments + self.versions, key=_by_date)

def _by_date(obj):
    if hasattr(obj, 'date'):
        return obj.date
    else:
        return obj.updated

class Comment(SQLObject):
    class sqlmeta:
        defaultOrder = 'date'

    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol()
    text = StringCol()
    task = ForeignKey("Task")

def _task_list_sort_index():
    index = max([tl.sort_index for tl in TaskList.selectBy(doneConstruction=True)] + [0])
    if index is None:
        return 0
    else:
        return index + 1

class User(SQLObject):
    username = StringCol()
    password = StringCol()

class TaskListFeature(SQLObject):
    name = StringCol()
    task_list = ForeignKey("TaskList")
    value = StringCol()

class TaskList(Versionable):
    _cacheValue = False
    class sqlmeta:
        defaultOrder = 'sort_index'

    live = BoolCol(default=True)
    special_users = MultipleJoin("TaskListRole")
    permissions = MultipleJoin("TaskListPermission")
    project = ForeignKey("Project")
    sort_index = IntCol(default=_task_list_sort_index)
    tasks = MultipleJoin("Task")
    text = StringCol()
    title = StringCol()
    updated = DateTimeCol(default=datetime.datetime.now)
    updated_by = StringCol()
    versions = MultipleJoin("Version", joinColumn="orig_id", orderBy='updated')
    watchers = MultipleJoin("Watcher")
    created = DateTimeCol(default=datetime.datetime.now)
    features = MultipleJoin("TaskListFeature")
    statuses = MultipleJoin("Status")
    initial_assign = IntCol(default=0)
    other_level =  IntCol()
    member_level =  IntCol()

    def managers(self):
        return [u.username for u in self.special_users if u.role == Role.getByName('ListOwner')]

    def hasFeature(self, feature_name):
        for feature in self.features:
            if feature.name == feature_name:
                return True
        return False

    def getWatcher(self, username):
        return Watcher.selectBy(username=username, task_listID=self.id)[0]

    def isWatchedBy(self, username):
        return Watcher.selectBy(username=username, task_list=self.id).count() > 0

    def topLevelTasks(self):
        import tasktracker.lib.helpers as h

        return [c for c in Task.selectBy(parentID=0, live=True, task_listID=self.id) if h.has_permission('task', 'show', id=c.id)]

    def uncompletedTasks(self):
        import tasktracker.lib.helpers as h

        return [c for c in Task.select(AND(Task.q.status != 'done', Task.q.task_listID == self.id, Task.q.live == True)) if h.has_permission('task', 'show', id=c.id)]
    
    def completedTasks(self):
        import tasktracker.lib.helpers as h
        
        return [c for c in Task.select(AND(Task.q.status == 'done', Task.q.task_listID == self.id, Task.q.live == True)) if h.has_permission('task', 'show', id=c.id)]

    def visibleTasks(self):
        import tasktracker.lib.helpers as h

        return [c for c in Task.select(AND(Task.q.task_listID == self.id, Task.q.live == True)) if h.has_permission('task', 'show', id=c.id)]

    def set(self, **kwargs):

        started = True
        if not getattr(self, 'id', None):
            started = False
            super(TaskList, self).set(**kwargs)
            
        kwargs['updated_by'] = c.username
        kwargs['updated'] = datetime.datetime.now()
        if not started:
            return

        conn = hub.getConnection()
        trans = conn.transaction()

        params = self._clean_params(kwargs)
        super(TaskList, self).set(**params)

        trans.commit()

    def _clean_params(self, kwargs):

        params = {}
        allowed_params = ("title", "text", "projectID", "initial_assign", "member_level", "other_level")
        for param in allowed_params:
            if kwargs.has_key(param):
                params[param] = kwargs[param]

        return params


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

        super(TaskList, self)._create(id, **params)

        if kwargs.get('statuses', None):
            statuses = kwargs['statuses'].split(",")
            if not 'done' in statuses:
                statuses.append('done')
        else:
            statuses = ['not done', 'done']
        for status in statuses:
            Status(name=status, task_list = self.id)

        self.doneConstruction = True
        trans.commit()

    def isOwnedBy(self, username):
        return TaskListRole.selectBy(username = username, task_listID = self.id, role = Role.getByName('ListOwner')).count()

    def destroySelf(self):
        for permission in self.permissions:
            permission.destroySelf()
        
        for feature in self.features:
            feature.destroySelf()

        super(TaskList, self).destroySelf()


def task_row_update(task, args):
    if len(args) == 1 and args.has_key('updated'):
        return
    create_version(TaskVersion, task)

def task_list_row_update(task, args):
    if len(args) == 1 and args.has_key('updated'):
        return
    create_version(TaskListVersion, task)

listen(task_row_update, Task, RowUpdateSignal)
listen(task_list_row_update, TaskList, RowUpdateSignal)

soClasses = [
Action,
Comment,
Notification,
OutgoingEmail,
Project,
Role,
Status,
Task,
TaskVersion,
TaskList,
TaskListFeature,
TaskListPermission,
TaskListRole,
TaskListVersion,
User,
Version,
Versionable,
Watcher,
]
