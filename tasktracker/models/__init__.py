
# Copyright (C) 2006-2007 The Open Planning Project

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
from sqlobject.versioning import Versioning
from sqlobject.sqlbuilder import *
from sqlobject.events import *
from pylons.database import PackageHub
from pylons import c, g
from tasktracker.lib.memoize import memoize

hub = PackageHub("tasktracker", pool_connections=False)
__connection__ = hub

# Don't forget to update soClasses, below

import datetime

import os

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
    triggering_watcher = ForeignKey("Watcher")
    handled = BoolCol(default=False)
    
    def targetType(self):
        if self.taskID:
            return "task"
        else:
            return "task_list"

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
    class sqlmeta:
        defaultOrder = 'id'

    name = StringCol(length=255)
    task_list = ForeignKey("TaskList")

    @classmethod
    def lookup(cls, name, task_list_id):
        return Status.selectBy(name=name, task_listID=task_list_id)

class Role(SQLObject):
    class sqlmeta:
        defaultOrder = '-level'

    name = StringCol(length=255)
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
    title = StringCol(length=255)
    task_lists = MultipleJoin("TaskList")
    initialized = BoolCol(default=False)
    readonly = BoolCol(default=False)
    
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
    index = max([t.sort_index for t in Task.selectBy(live=True)] + [0])
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
    creator = StringCol(length=255, default="")
    deadline = DateTimeCol(default=None)
    live = BoolCol(default=True)    
    owner = StringCol(length=255, default="")
    parent = ForeignKey("Task")
    priority = StringCol(length=255, default="None")
    private = BoolCol(default=False)
    sort_index = IntCol()
    status = StringCol(length=255)
    task_list = ForeignKey("TaskList")
    text = StringCol(length=255, default="")
    title = StringCol()
    versions = Versioning(extraCols=dict(updatedBy = StringCol(length=255, default=lambda : c.username)))
    watchers = MultipleJoin("Watcher")

    def get_updated(self):
        if self.versions.count():
            return self.versions[-1].dateArchived
        else:
            return self.created

    updated = property(get_updated)

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

        kwargs['sort_index'] = _task_sort_index()
        kwargs.setdefault('parentID', 0)
        kwargs['live'] = True

        if task_list.initial_assign == 0 and not kwargs.get('owner', None):
            kwargs['owner'] = c.username

        super(Task, self)._create(id, **kwargs)

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

    def liveDescendents(self):
        descendents = []
        children = self.liveChildren()
        for child in children:
            descendents.append(child)
            descendents += child.liveDescendents()
        return descendents

    def uncompletedChildren(self):
        import tasktracker.lib.helpers as h

        return [c for c in self.children if c.status != 'done' and c.live and h.has_permission('task', 'show', id=c.id)]

    def uncompletedDescendents(self):
        descendents = []
        children = self.uncompletedChildren()
        for child in children:
            descendents.append(child)
            descendents += child.uncompletedDescendents()
        return descendents
        
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

    def path(self, attr=None):
        if not attr: attr = "sort_index"
        path = []
        task = self
        while task.parentID:
            path.append(getattr(task, attr))
            task = task.parent
        path.append(getattr(task, attr))
        path.reverse()
        return path

    def adjacentTasks(self, options=None, user=None, level=100):
        query = AND(Task.q.task_listID == c.task_listID, Task.q.live==1)

        sortOrder = None
        if options: 
            sql, orderBy, sortOrder = options
        if not sortOrder:
            sortOrder = "ASC"

        if not orderBy:
            orderBy = "sort_index"

        if level >= Role.getLevel("ListOwner"):
            #filtering needed
            query = AND(query, OR(Task.q.private == 0, Task.q.owner == user))
        
        attr = getattr(c.task, orderBy)
        next_predicate = (getattr(Task.q, orderBy) > attr, "ASC")
        prev_predicate = (getattr(Task.q, orderBy) < attr, "DESC")
        if sortOrder == "DESC":
            next_predicate, prev_predicate = prev_predicate, next_predicate
        
        tasks = []
        for predicate, sortOrder in [prev_predicate, next_predicate]:
            is_prev = bool(id(predicate) == id(prev_predicate[0]))

            adj_task_query = "%s order by %s %s, sort_index %s" % (sqlrepr(AND(query, predicate, Task.q.parentID == c.task.parentID), 'mysql'), orderBy, sortOrder, sortOrder)
            if "SQLOp" in adj_task_query:
                import pdb;pdb.set_trace()

            adj = list(Task.select(adj_task_query).orderBy(None).limit(1))
            if adj:
                adj = adj[0]
            else:
                if c.task.parentID and is_prev: #parent can only be prev, not next
                    adj = c.task.parent
                else:
                    adj_task_query = "%s order by %s %s, sort_index %s" % (sqlrepr(AND(query, predicate, Task.q.parentID == 0), 'mysql'), orderBy, sortOrder, sortOrder)
                    #adj_task_query = "%s AND task.parent_id = 0 AND %s order by %s %s, sort_index %s" % (query, predicate, orderBy, sortOrder, sortOrder)
                    adj = list(Task.select(adj_task_query).orderBy(None).limit(1))
                    if adj:
                        adj = adj[0]
                    else:
                        adj = None

            if not adj and is_prev:
                tasks.append(None)
                continue

            def search_children(child, recursive=True):
                if not child:
                    return child
                while 1:
                    child_task_query = "%s order by %s %s, sort_index %s" % (sqlrepr(AND(query, Task.q.parentID == child.id), 'mysql'), orderBy, sortOrder, sortOrder)
                    new_child = list(Task.select(child_task_query).orderBy(None).limit(1))
                    if not new_child:
                        break
                    child = new_child[0]
                    if not recursive:
                        break
                return child

            if is_prev:
                if adj.id == self.parentID:
                    child = adj
                else:
                    child = search_children(adj)
                    
            else:
                #check if next is child of this task
                child = search_children(c.task, recursive=False)
                if child == c.task:
                    #next is (maybe child of) some sib of this task
                    child = search_children(adj)
            tasks.append(child)

        return tasks


    # @@ it's looking more and more like this doesn't remotely belong in the model. - egj
    def adjacentTasksFiltered(self, options=None, user=None, level=100):
        """Unused.  It's too expensive. See adjacentTasks, above for current implementation."""
        query = """task.task_list_id=%s AND task.live=1""" % (c.task_listID)
        sql = sortOrder = None
        if options: 
            sql, orderBy, sortOrder = options
        if sql:
            query = "%s %s" % (query, sql)
        if not orderBy:
            orderBy = "sort_index"

        if level >= Role.getLevel("ListOwner"):
            #filtering needed
            query += " AND (task.private = 0 OR task.owner = '%s')" % user

        conn = hub.getConnection()
        trans = conn.transaction()
        tasks = Task.select(query)
        trans.commit()

        tasks = list(tasks)
        root_tasks = None

        delete_permalink = False
        if self not in tasks:
            all_tasks = Task.select( """task.task_list_id=%s AND task.live=1""" % (c.task_listID) )
            tasks = all_tasks
            root_tasks = [task for task in all_tasks if task.parentID == 0]
            delete_permalink = True

        if not root_tasks:
            root_tasks = Task.select( """task.task_list_id=%s AND task.live=1 AND task.parent_id = 0""" % (c.task_listID) )
            
        sorted_tasks = sortedTasks(tasks, root_tasks, orderBy, sortOrder)

        next = prev = None
        index = sorted_tasks.index(self)
        if index > 0:
            prev = sorted_tasks[index - 1]
        if index < len(sorted_tasks) - 1:
            next = sorted_tasks[index + 1]

        return (prev, next, delete_permalink)

    def actions(self):
        return sorted(self.comments + list(self.versions), key=_by_date, reverse=True)

    def revertToDate(self, date):
        versions_in_future = []
        TaskVersion = Task.versions.versionClass
        last_good_version = TaskVersion.select(AND(TaskVersion.q.masterID==self.id, TaskVersion.q.dateArchived < date)).orderBy('dateArchived')[-1]

        #do the reversion
        last_good_version.restore()
        
        #now we need to make sure the task is consistent
        if self.live:
            if self.parentID and not self.parent.live:
                self.parentID = 0

        for version in reversed(list(self.versions)):
            if version.dateArchived < date:
                break
            #archive the data
            versions_in_future.append(version)

        if not version:
            return #nothing changed since date

        comments_in_future = []
        for comment in reversed(list(self.comments)):
            if comment.date < date:
                break
            comments_in_future.append(comment)
            
        #store and delete all future versions (including the one we just created)

        histdir = os.path.join(g.obsolete_future_history_dir, 'task', str(self.id))
        if not os.path.exists(histdir):
            os.makedirs(histdir)

        now = datetime.datetime.now().isoformat()
        histfile = os.path.join(histdir, now)
        f = open(histfile, "w")

        for version in versions_in_future:
            print >>f, "TaskVersion(%s)" % ", ".join (['%s = %s' % (k, repr(v)) for k,v in version.sqlmeta.asDict().items()])
            version.destroySelf()

        for comment in comments_in_future:
            print >>f, "Comment(%s)" % ", ".join (['%s = %s' % (k, repr(v)) for k,v in comment.sqlmeta.asDict().items()])
            comment.destroySelf()

        f.close()

def sortedTasks(allowed_tasks, this_level, sort_by, sort_order):
    def _cmp(x, y):
        try:
            return cmp(x,y)
        except TypeError:
            # @@ this isn't even remotely general, but in our current db setup the only way to get here is comparing a datetime with None.
            if x[0] is None:
                return 1
            elif y[0] is None:
                return -1
            else:
                return 0

    reverse = False
    if sort_order == "DESC":
        reverse = True
    s = []

    # we can't just pass reverse=True to sorted because we need
    # a totally reversed list not just a reverse-sorted list.
    tuples = sorted([(getattr(k, sort_by), k) for k in this_level], cmp=_cmp)
    if reverse:
        tuples.reverse()
    for k in tuples:
        if k[1] in allowed_tasks:
            s.append(k[1])
        s.extend(sortedTasks(allowed_tasks, k[1].children, sort_by, sort_order))
    return s

def _by_date(obj):
    if hasattr(obj, 'date'):
        return obj.date
    else:
        return obj.dateArchived

class Comment(SQLObject):
    class sqlmeta:
        defaultOrder = 'date'

    date = DateTimeCol(default=datetime.datetime.now)
    user = StringCol(length=255)
    text = StringCol(length=255)
    task = ForeignKey("Task")

def _task_list_sort_index():
    index = max([tl.sort_index for tl in TaskList.select()] + [0])
    if index is None:
        return 0
    else:
        return index + 1

class User(SQLObject):
    username = StringCol(length=255)
    password = StringCol(length=255)

class TaskListFeature(SQLObject):
    name = StringCol(length=255)
    task_list = ForeignKey("TaskList")
    value = StringCol()

class TaskList(SQLObject):
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
    title = StringCol(length=255)
    versions = Versioning(extraCols=dict(updatedBy = StringCol(length=255, default=lambda : c.username)))
    watchers = MultipleJoin("Watcher")
    created = DateTimeCol(default=datetime.datetime.now)
    features = MultipleJoin("TaskListFeature")
    statuses = MultipleJoin("Status")
    initial_assign = IntCol(default=0)
    other_level =  IntCol(default=1)
    member_level =  IntCol(default=1)

    def get_updated(self):
        if self.versions.count():
            return self.versions[-1].dateArchived
        else:
            return self.created

    updated = property(get_updated)

    def isListOwner(self, username):
        list_owner_role = Role.getByName('ListOwner')
        roles = TaskListRole.selectBy(role=list_owner_role, task_list=self, username=username)
        if roles.count() > 0:
            return True
        else:
            return 'ProjectAdmin' in c.usermapper.project_member_roles(username)

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

    @memoize
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
        conn = hub.getConnection()
        trans = conn.transaction()

        super(TaskList, self)._create(id, **params)

        if kwargs.get('statuses', None):
            statuses = kwargs['statuses'].split(",")
            if 'done' in statuses:
                statuses.remove('done')
            #done must always be at end
            statuses.append('done')            

        else:
            statuses = ['not done', 'done']
        for status in statuses:
            Status(name=status, task_list = self.id)

        trans.commit()

    def isOwnedBy(self, username):
        return TaskListRole.selectBy(username = username, task_listID = self.id, role = Role.getByName('ListOwner')).count()

    def destroySelf(self):
        for permission in self.permissions:
            permission.destroySelf()
        
        for feature in self.features:
            feature.destroySelf()

        super(TaskList, self).destroySelf()

TaskVersion = Task.versions.versionClass
TaskVersion.getChangedFields = memoize(TaskVersion.getChangedFields)

soClasses = [
Action,
Comment,
Notification,
OutgoingEmail,
Project,
Role,
Status,
Task,
TaskList,
TaskListFeature,
TaskListPermission,
TaskListRole,
User,
Watcher,
]
