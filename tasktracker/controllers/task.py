
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

from tasktracker.lib.base import *
from tasktracker.models import *

from tasktracker.lib import helpers as h
from tasktracker.lib.taskparser import *
import formencode
from formencode.validators import *
from tasktracker.lib.datetimeconverter import *

class CreateTaskForm(formencode.Schema):  
    pre_validators = [formencode.variabledecode.NestedVariables]
    allow_extra_fields = True  
    title = NotEmpty()
    deadline = formencode.compound.All(DateValidator(earliest_date=datetime.datetime.today),
                                       DateTimeConverter())

class StatusChangeForm(formencode.Schema):
    allow_extra_fields = True
    status = formencode.validators.OneOf([status.name for status in Status.select()])

class PriorityChangeForm(formencode.Schema):
    allow_extra_fields = True
    priority = formencode.validators.OneOf("High Medium Low None".split())

class DeadlineChangeForm(formencode.Schema):
    allow_extra_fields = True
    deadline = formencode.compound.All(DateValidator(earliest_date=datetime.date.today),
                                       DateConverter())

class TaskController(BaseController):

    def _clean_params(self, params):
        allowed_params = ("title", "text", "status", "deadline", "task_listID", "parentID", "owner", "private", "priority")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean

    @validate(schema=StatusChangeForm(), form='show_update')
    @attrs(action='change_status', watchdog=TaskUpdateWatchdog)
    @catches_errors
    def change_status(self, id):
        c.task = self._getTask(int(id))
        c.task.status = self.form_result['status']
        return render_text("ok")

    @validate(schema=PriorityChangeForm(), form='show_update')
    @attrs(action='update', watchdog=TaskUpdateWatchdog)
    @catches_errors
    def change_priority(self, id):
        c.task = self._getTask(int(id))
        c.task.priority = self.form_result['priority']
        return render_text("ok")

    @validate(schema=DeadlineChangeForm(), form='show_update')
    @attrs(action='update', watchdog=TaskUpdateWatchdog)
    @catches_errors
    def change_deadline(self, id):
        c.task = self._getTask(int(id))
        c.task.deadline = self.form_result['deadline']
        print c.task.deadline
        return render_text("ok")
    
    @attrs(action='show')
    def auto_complete_for_owner(self):
        partial = request.params['owner']
        users = map (lambda u: u['username'], c.usermapper.project_members())
        users = filter(lambda u: u.lower().startswith(partial.lower()), users)
        return render_text('<ul class="autocomplete">%s</ul>' % ''.join(['<li>%s</li>' % u for u in users]))

    @attrs(action='update', watchdog=TaskMoveWatchdog)
    def move(self, id):
        task = self._getTask(int(id))
        if request.params.has_key ('new_parent'):
            new_parent_id = int(request.params['new_parent'])
            assert new_parent_id == 0 or Task.get(new_parent_id).task_listID == task.task_listID
            assert new_parent_id != task.id
            task.parentID = new_parent_id
            if new_parent_id > 0:
                parent = Task.get(new_parent_id)
                if parent.private:
                    task.private = True
            task.moveToTop()
        else:
            new_sibling_id = int(request.params['new_sibling'])
            new_sibling = Task.get(new_sibling_id)
            assert new_sibling.task_listID == task.task_listID
            task.parentID = new_sibling.parentID
            if new_sibling.parentID > 0:
                parent = Task.get(new_sibling.parentID)
                if parent.private:
                    task.private = True
            task.moveBelow(new_sibling)
        return render_text('ok')

    @attrs(action='create')
    @catches_errors
    def show_create(self, id):
        c.task_listID = int(request.params['task_listID'])
        if not c.task_listID:
            raise ValueError("Can only create a task within a task list.")

        c.tasklist = TaskList.get(c.task_listID)
        if 'parentID' in request.params:
            c.parentID = request.params['parentID']
        else:
            c.parentID = 0
        return render_response('zpt', 'task.show_create')

    @attrs(action='create', watchdog=TaskCreateWatchdog)
    @validate(schema=CreateTaskForm(), form='show_create')
    def create(self):
        p = self._clean_params(self.form_result)
        return self._create_task(**p)

    def _create_task(self, **p):
        if not (c.level <= Role.getLevel('ProjectAdmin') or
                TaskList.get(p['task_listID']).isOwnedBy(c.username)):
            p['private'] = False
        
        p['creator'] = c.username
        if p.has_key('text'):
            p['text'] = p['text'].replace('\n', "<br>")
        c.task = Task(**p)

        # some ugly error checking
        assert TaskList.get(p['task_listID']).id == int(p['task_listID'])
        assert int(p['parentID']) == 0 or Task.get(p['parentID']).task_listID == int(p['task_listID'])

        return Response.redirect_to(action='show',controller='tasklist', id=request.params['task_listID'])

    @attrs(action='claim')
    @catches_errors
    def claim(self, id):
        c.task = self._getTask(id)
        c.task.owner = c.username
        return Response.redirect_to(action='show',controller='task', id=id)

    @attrs(action='assign')
    @catches_errors
    def assign(self, id):
        c.task = self._getTask(id)
        c.task.owner = request.params["owner"]
        return Response.redirect_to(action='show',controller='task', id=id)

    @attrs(action='comment', watchdog=TaskCommentWatchdog)
    @catches_errors
    def comment(self, id):
        c.task = Task.get(int(id))
        c.comment = Comment(text=request.params["text"].replace('\n', "<br>"), user=c.username, task=c.task)

        return Response.redirect_to(action='show',id=c.task.id)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id):
        c.oldtask = self._getTask(int(id))        
        c.owner = c.oldtask.owner.title
        return render_response('zpt', 'task.show_update')

    @attrs(action='update', watchdog=TaskUpdateWatchdog)
    @validate(schema=CreateTaskForm(), form='show_update')
    def update(self, id):

        c.task = self._getTask(int(id))
        p = self._clean_params(self.form_result)
        new_parent_id = int(p['parentID'])
        assert new_parent_id == 0 or Task.get(new_parent_id).task_listID == c.task.task_listID
        assert new_parent_id != c.task.id
        p['task_listID'] = c.task.task_listID

        if not (h.has_permission(controller='task', action='assign') or p['owner'] == c.username and h.has_permission(controller='task', action='claim')):
            del p['owner']

        if not p['owner']:
            del p['owner']

        if not 'private' in p.keys():
            p['private'] = False

        if p.has_key('text'):
            p['text'] = p['text'].replace('\n', "<br>")

        if not (c.level <= Role.getLevel('ProjectAdmin') or
                c.task.task_list.isOwnedBy(c.username) or
                c.task.owner == c.username):
            del p['private']

        c.task.set(**p)

        return Response.redirect_to(action='show', controller='tasklist', id=c.task.task_listID)

    def _getTask(self, id):
        try:
            return Task.get(int(id))
        except LookupError:
            raise NoSuchIdError("No such task ID: %s" % id)

    @attrs(action='show')
    @catches_errors
    def show(self, id):
        c.task = self._getTask(int(id))
        c.parentID = int(id)
        c.tasklist = c.task.task_list
        c.task_listID = c.tasklist.id
        c.depth = c.task.depth() + 1
        return render_response('zpt', 'task.show')

    @attrs(action='update')
    @catches_errors
    def destroy(self, id):
        c.task = self._getTask(int(id))
        c.task.live = False
        return Response.redirect_to(action='show', controller='tasklist', id=c.task.task_listID)

    @attrs(action='create')
    def create_tasks(self):
        tasks = request.params['tasks']
        import re
        okay = re.compile("\w")
        for line in tasks.split("\n"):
            if okay.search(line):
                self._create_task(task_listID=request.params['task_listID'], private=False, text='', title=line.strip(), parentID = int(request.params['parentID']))
        return Response.redirect_to(action='show',controller='tasklist', id=request.params['task_listID'])

    @attrs(action='open')
    @catches_errors
    def show_create_tasks(self, id):
        c.tasklist = TaskList.get(int(id))
        c.task_listID = id
        return render_response('zpt', 'task.show_create_tasks')
