
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
from pylons.templating import render_response as render_body

from dateutil.parser import parse as dateparse

class EditTaskForm(formencode.Schema):  
    pre_validators = [formencode.variabledecode.NestedVariables]
    allow_extra_fields = True
    filter_extra_fields = True
    ignore_key_missing = True
    title = NotEmpty()
    deadline = formencode.compound.All(DateValidator(),
                                       DateConverter())
    status = String(not_empty = True)
    priority = formencode.validators.OneOf("High Medium Low None".split())
    owner = formencode.compound.Any(NotEmpty(), Empty())
    parentID = formencode.validators.Int(not_empty = True)
    siblingID = formencode.validators.Int(not_empty = True)
    task_listID = formencode.validators.Int()
    text = formencode.validators.String()
    is_preview = StringBoolean(not_empty = True)
    no_second_row = StringBoolean(not_empty = True)
    is_flat = StringBoolean(not_empty = True)
    editable_title = StringBoolean(not_empty = True)
    depth = Int()
    private = NotEmpty()

def _assignment_permitted(new_owner):
    return (h.has_permission(controller='task', action='assign') or new_owner == c.username and h.has_permission(controller='task', action='claim'))

_actions = dict(status='change_status', owner='claim', priority='update', deadline='update', text='update', title='update')
def _field_permission(param):    
    return _actions[param['field']]
    
class TaskController(BaseController):
    
    def _clean_params(self, params):
        allowed_params = ("title", "text", "status", "deadline", "task_listID", "parentID", "siblingID", "owner", "private", "priority")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean
    
    @authenticate
    @validate(schema=EditTaskForm(), form='show_update')
    @attrs(action=_field_permission, watchdog=TaskUpdateWatchdog)
    @catches_errors
    def change_field(self, id, *args, **kwargs):
        field = request.params['field']
        task = self._getTask(int(id))
        newfield = self.form_result[field]

        #special case for deadline -- converts a datetime to a date.
        old = getattr(task, field)
        if field == 'deadline' and old and isinstance(old, datetime.datetime):
            old = old.date()

        #special case for status if only two statuses are present.
        elif field == 'status':
            if not task.task_list.hasFeature('custom_status'):
                assert newfield in ('true', 'false')
                if newfield == 'true':
                    newfield = 'done'
                else:
                    newfield = 'not done'
            else:
                assert newfield in [s.name for s in task.task_list.statuses]

        #special case for owner

        elif field == "owner":
            assert _assignment_permitted(newfield)
            assert newfield in [u['username'] for u in c.usermapper.project_members()]

        # find out if the old taskrow wants us to render its replacement a particular way
        is_preview = self.form_result.get('is_preview', None)
        no_second_row = self.form_result.get('no_second_row', None)
        is_flat = self.form_result.get('is_flat', None)
        editable_title = self.form_result.get('editable_title', None)
        depth = self.form_result.get('depth', 0)
        if not old == newfield:
            setattr(task, field, newfield)

        c.task = task
        c.depth = depth

        return render_response('task/task_item.myt', fragment=True, atask=c.task,
                               no_second_row=no_second_row, is_preview=is_preview, is_flat=is_flat, editable_title=editable_title)

    @attrs(action='open')
    def auto_complete_for(self, id):
        partial = request.params[id]
        users = map (lambda u: u['username'], c.usermapper.project_members())
        users = filter(lambda u: u.lower().startswith(partial.lower()), users)
        return render_text('<ul class="autocomplete">%s</ul>' % ''.join(['<li>%s</li>' % u for u in users]))

    def _move_under_parent(self, id, parentID):
        task = self._getTask(int(id))
        assert parentID == 0 or Task.get(parentID).task_listID == task.task_listID
        assert parentID != task.id
        task.parentID = parentID
        if parentID > 0:
            parent = Task.get(parentID)
            if parent.private:
                task.private = True
        task.moveToTop()

    def _move_below_sibling(self, id, siblingID):
        task = self._getTask(int(id))
        new_sibling = Task.get(siblingID)
        assert new_sibling.task_listID == task.task_listID
        task.parentID = new_sibling.parentID
        if new_sibling.parentID > 0:
            parent = Task.get(new_sibling.parentID)
            if parent.private:
                task.private = True
        task.moveBelow(new_sibling)

    @attrs(action='update', watchdog=TaskMoveWatchdog)
    def move(self, id):        
        if request.params.has_key('new_parent'):
            new_parent_id = int(request.params['new_parent'])
            self._move_under_parent(id, new_parent_id)
        else:
            new_sibling_id = int(request.params['new_sibling'])
            self._move_below_sibling(id, new_sibling_id)
        return render_text('ok')

    @attrs(action='create')
    @catches_errors
    def show_create(self, id, *args, **kwargs):
        c.task_listID = int(request.params['task_listID'])
        if not c.task_listID:
            raise ValueError("Can only create a task within a task list.")

        c.tasklist = TaskList.get(c.task_listID)
        if 'parentID' in request.params:
            c.parentID = request.params['parentID']
        else:
            c.parentID = 0
        return render_response('task/show_create.myt')

    @authenticate
    @attrs(action='create', watchdog=TaskCreateWatchdog)
    @validate(schema=EditTaskForm(), form='show_create')
    def create(self, *args, **kwargs):
        p = self._clean_params(self.form_result)
        return self._create_task(url_from=request.params.get('url_from', None), **p)

    def _create_task(self, url_from = None, **p):
        if not (c.level <= Role.getLevel('ProjectAdmin') or
                TaskList.get(p['task_listID']).isOwnedBy(c.username)):
            p['private'] = False
        p['creator'] = c.username
        if not p.has_key('task_listID'):
            p['task_listID'] = c.tasklist.id
        if p.has_key('text'):
            p['text'] = p['text'].replace('\n', "<br>")  #TODO there must be a better way to do this
        if not p.has_key('parentID'):
            p['parentID'] = 0
        siblingID = p['siblingID']
        del p['siblingID']
        c.task = Task(**p)
        # some ugly error checking
        assert TaskList.get(p['task_listID']).id == int(p['task_listID'])
        assert int(p['parentID']) == 0 or Task.get(p['parentID']).task_listID == int(p['task_listID'])
        c.depth = 0
        if siblingID > 0:
            self._move_below_sibling(c.task.id, siblingID)
        return render_response('task/task_list_item.myt', atask=c.task, fragment=True)

    @attrs(action='claim')
    @catches_errors
    def claim(self, id, *args, **kwargs):
        c.task = self._getTask(id)
        c.task.owner = c.username
        return Response.redirect_to(action='show',controller='task', id=id)
        
    @attrs(action='assign')
    @catches_errors
    def assign(self, id, *args, **kwargs):
        c.task = self._getTask(id)
        c.task.owner = request.params["owner"]
        return Response.redirect_to(action='show',controller='task', id=id)

    @attrs(action='comment', watchdog=TaskCommentWatchdog)
    @catches_errors
    def comment(self, id, *args, **kwargs):
        comment = request.params["text"].strip()
        if not len(comment):
            return Response('')
        c.task = Task.get(int(id))
        c.comment = Comment(text=comment.replace('\n', "<br>"), user=c.username, task=c.task)
        return Response(c.comment.text)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id, *args, **kwargs):
        c.oldtask = self._getTask(int(id))        
        c.owner = c.oldtask.owner
        return render_response('task/show_update.myt')

    @authenticate
    @attrs(action='update', watchdog=TaskUpdateWatchdog)
    @validate(schema=EditTaskForm(), form='show_update')
    def update(self, id):

        c.task = self._getTask(int(id))
        p = self._clean_params(self.form_result)
        new_parent_id = int(p['parentID'])
        assert new_parent_id == 0 or Task.get(new_parent_id).task_listID == c.task.task_listID
        assert new_parent_id != c.task.id
        p['task_listID'] = c.task.task_listID

        if not _assignment_permitted(p['owner']):
            del p['owner']

        if not p['owner']:
            del p['owner']

        if c.task.tasklist.isListOwner(c.username):
            if not 'private' in p.keys():
                p['private'] = False
        else:
            p['private'] = c.task.private

        if p.has_key('text'):
            p['text'] = p['text'].replace('\n', "<br>")

        if not (c.level <= Role.getLevel('ProjectAdmin') or
                c.task.task_list.isOwnedBy(c.username) or
                c.task.owner == c.username):
            del p['private']

        c.task.set(**p)

        return Response.redirect_to(action='show', controller='tasklist', id=c.task.task_listID)

    @authenticate
    @attrs(action='private')
    def update_private(self, id):
        c.task = self._getTask(int(id))
        c.task.private = request.params['private'] == 'true'
        return render_response('task/_private.myt', fragment=True)

    def _getTask(self, id):
        try:
            return Task.get(int(id))
        except LookupError:
            raise NoSuchIdError("No such task ID: %s" % id)

    @attrs(action='private')
    def revertToDate(self, id):
        c.task = self._getTask(int(id))
        date = dateparse(request.params['date'])
        c.task.revertToDate(date)
        return self.show(id)

    @attrs(action='show')
    @catches_errors
    def show(self, id, *args, **kwargs):
        version = request.params.get('version', None)
        if version:
            c.version = version
            c.task = Task.versions.versionClass.get(version)
        else:
            c.task = self._getTask(int(id))
        c.parentID = int(id)
        c.tasklist = c.task.task_list
        c.task_listID = c.tasklist.id        
        c.depth = c.task.depth()
        c.url_from = url_for(controller='task', action='show', id=id)
        c.previewTextLength = 0
        return render_response('task/show.myt')

    @authenticate
    @attrs(action='update')
    @catches_errors
    def destroy(self, id, *args, **kwargs):
        c.task = self._getTask(int(id))
        c.task.live = False
        return Response.redirect_to(action='show', controller='tasklist', id=c.task.task_listID)

    @authenticate
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
    def show_create_tasks(self, id, *args, **kwargs):
        c.tasklist = TaskList.get(int(id))
        c.task_listID = id
        return render_response('task/show_create_tasks.myt')
