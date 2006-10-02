## NOTE
##   If you plan on using SQLObject, the following should be un-commented and provides
##   a starting point for setting up your schema

from sqlobject import *
from pylons.database import PackageHub
hub = PackageHub("tasktracker")
__connection__ = hub

# You should then import your SQLObject classes
# from myclass import MyDataClass

# Don't forget to update soClasses, below

import datetime

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
            Role.levels[name] = Role.selectBy(name=name)[0].level
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
        defaultOrder = 'left_node'

    created = DateTimeCol(default=datetime.datetime.now)
    deadline = DateTimeCol(default=None)
    title = StringCol()
    text = StringCol()
    live = BoolCol(default=True)    
    status = StringCol()

    comments = MultipleJoin("Comment")
    task_list = ForeignKey("TaskList")
    private = BoolCol(default=False)
    owner = StringCol(default="")

    left_node = IntCol(default=-1)
    right_node = IntCol(default=-1)
    moving = BoolCol(default=False)

    def _create(self, id, **kwargs):
#        if 'task_list' in kwargs:
#            kwargs['task_listID'] = kwargs.pop('task_list').id

        if not kwargs.has_key('status'):
            project = TaskList.get(kwargs['task_listID']).project
            assert len(project.statuses)
            kwargs['status'] = project.statuses[0].name

        right = Task.selectBy(task_listID = kwargs['task_listID']).max('right_node')
        if not right:
            right = 1

        kwargs['left_node'] = right + 1
        kwargs['right_node'] = right + 2

        SQLObject._create(self, id, **kwargs)

    def depth(self):
        return len(Task.select(Task.q.left_node < self.left_node and Task.q.right_node > self.node.right_node))

    def reparent(self, new_parent):
        """Places this node as the last of the parent's childern"""

        conn = hub.getConnection()
        trans = conn.transaction()

        update_right = conn.sqlrepr(Update(Task.q, {right: Task.q.right + 2}, where=Task.q.right > new_parent.right))

        update_left = conn.sqlrepr(Update(Task.q, {left:Task.q.left + 2}, where=Task.q.left > new_parent.right))

        conn.query(update_left)
        conn.query(update_right)

        self.left_node = new_parent.right_node
        self.right_node = new_parent.right_node + 1
        new_parent.right_node += 2

        trans.commit()
        conn.cache.clear()

    def childTasks(self):
        return ((self.right - self.left) - 1) / 2

    def insertBefore(self, sibling):
        """Places this node before another node."""

        #Everything after the old location, but before the new location needs to be shifted.
        #Everything after the new location, but before the old location needs to be shifted.
        
        #shift forward:  [before old][old][middle][new][after new]
        #shift back :    [before new][new][middle][old][after new]
        
        conn = hub.getConnection()
        trans = conn.transaction()

        subtree_insert_shift = 1 + self.right - self.left
        subtree_internal_shift = sibling.left - self.left 

        update_self = conn.sqlrepr(Update(Task.q, {
                    left: Task.q.left + subtree_internal_shift,
                    right: Task.q.right + subtree_internal_shift,
                    moving: True
                    }, where=AND(Task.q.left >= self.left, Task.q.right <= self.right)))
        

        if self.left > sibling.left:
            update_middle_left = conn.sqlrepr(Update(Task.q, {
                        left: Task.q.left + subtree_insert_shift
                        }, where=AND(Task.q.left >= sibling.left, 
                                     Task.q.left < self.left, 
                                     Task.q.moving == False)))

            update_middle_right = conn.sqlrepr(Update(Task.q, {
                        right: Task.q.right + subtree_insert_shift
                        }, where=AND(Task.q.right > sibling.right, 
                                     Task.q.right < self.left, 
                                     Task.q.moving == False)))        
        else:
            update_middle_left = conn.sqlrepr(Update(Task.q, {
                        left: Task.q.left - subtree_insert_shift
                        }, where=AND(Task.q.left >= self.left, 
                                     Task.q.left < sibling.left, 
                                     Task.q.moving == False)))

            update_middle_right = conn.sqlrepr(Update(Task.q, {
                        right: Task.q.right - subtree_insert_shift
                        }, where=AND(Task.q.right > sibling.right, 
                                     Task.q.right < self.left, 
                                     Task.q.moving == False)))
         
       
        update_restore = conn.sqlrepr(Update(Task.q, {
                        moving: False
                        }))       

        conn.query(update_self)
        conn.query(update_middle_left)
        conn.query(update_middle_right)
        conn.query(update_restore)

        trans.commit()
        conn.cache.clear()   

    def isOwnedBy(self, username):
        return self.owner == username            

    def changeStatus(self, newStatus):
        self.status = newStatus
        return self.status

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
    ]
