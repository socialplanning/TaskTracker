
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
import formencode
from formencode.validators import *
from tasktracker.lib.datetimeconverter import *

from dateutil.parser import parse as dateparse

class EditTaskForm(formencode.Schema):  
    pre_validators = [formencode.variabledecode.NestedVariables]
    allow_extra_fields = True
    filter_extra_fields = True
    ignore_key_missing = True
    title = h.SafeHTML(not_empty=True, strip=True, min=1, max=255)
    deadline = formencode.compound.All(DateValidator(),
                                       DateConverter())
    status = h.SafeHTML(not_empty=True)
    priority = formencode.validators.OneOf("High Medium Low None".split())
    owner = formencode.compound.Any(NotEmpty(), Empty())
    parentID = formencode.validators.Int(not_empty = True)
    siblingID = formencode.validators.Int(not_empty = True)
    task_listID = formencode.validators.Int()
    text = h.SafeHTML()
    is_preview = StringBoolean(not_empty = True)
    is_flat = StringBoolean(not_empty = True)
    editable_title = StringBoolean(not_empty = True)
    columnOrder = String()
    depth = Int()

def _assignment_permitted(new_owner):
    return ( h.has_permission(controller='task', action='assign') ) or \
        ( new_owner == c.username and h.has_permission(controller='task', action='claim') )

_actions = dict(status='change_status', owner='claim', priority='update', deadline='update', text='update', title='update')
def _field_permission(param):    
    return _actions[param['field']]


def get_child_tasks_in_display_order(task):
    children = task.liveChildren()
    if not children:
        return [task]
    else:
        return sum(map(get_child_tasks_in_display_order, children), [task])

def get_tasks_in_display_order(tasklist):
    return sum(map(get_child_tasks_in_display_order, tasklist.topLevelTasks()), [])
    
class TaskController(BaseController):

    @attrs(action='open', readonly=True)
    def index(self, *args, **kwargs):
        return Response.redirect_to(url_for('home'))

    @authenticate
    @validate(schema=EditTaskForm(), form='show_update')
    @attrs(action=_field_permission, readonly=False)
    @catches_errors
    def change_field(self, id, *args, **kwargs):

        field = request.params['field']
        task = safe_get(Task, id, check_live=True)
        newfield = self.form_result[field]

        #special case for deadline -- converts a datetime to a date.
        old = getattr(task, field)
        if field == 'deadline' and old and isinstance(old, datetime.datetime):
            old = old.date()

        #special case for status if only two statuses are present.
        elif field == 'status':
            if not task.task_list.hasFeature('custom_status'):
                assert newfield in ('true', 'false'), ("Bad status %s on task %s" % (newfield, id))
                if newfield == 'true':
                    newfield = task.task_list.getDoneStatus()
                else:
                    newfield = task.task_list.getNotDoneStatus()
            else:
                newfield = task.task_list.getStatusByName(newfield)
                assert newfield, ("Nonexistent status on task %d" % id)

        #special case for owner

        elif field == "owner":
            if not _assignment_permitted(newfield):
                raise httpexceptions.HTTPForbidden
            if newfield == "--": newfield = None

        # find out if the old taskrow wants us to render its replacement a particular way
        is_preview = self.form_result.get('is_preview', None)
        is_flat = self.form_result.get('is_flat', None)
        editable_title = self.form_result.get('editable_title', None)
        depth = self.form_result.get('depth', 0)
        columnOrder = self.form_result.get('columnOrder', None)
        if isinstance(newfield, basestring):
            newfield = h.html2safehtml(newfield)        
        if not old == newfield:
            setattr(task, field, newfield)

        c.task = task
        c.depth = depth

        if columnOrder:
            c.permalink = columnOrder

        return render('task/task_item_row.myt', fragment=True, atask=c.task,
                               is_preview=is_preview, is_flat=is_flat, 
                               editable_title=editable_title)

    @attrs(action='open', readonly=True)  # @@ no - this should not be open. - egj
    def auto_complete_for(self, id):
        partial = request.params[id]
        # @@ let's make this readable... - egj
        users = filter(lambda u: u.lower().startswith(partial.lower()), c.usermapper.project_member_names())
        return render_text('<ul class="autocomplete">%s</ul>' % ''.join(['<li>%s</li>' % u for u in users]))

    def _move_under_parent(self, id, parentID):
        task = safe_get(Task, id, check_live=True)
        assert parentID == 0 or Task.get(parentID).task_listID == task.task_listID, ("Line 135")
        assert parentID != task.id, ("Time paradox!")
        task.parentID = parentID

        task.moveToTop()

    def _move_below_sibling(self, id, siblingID):
        task = safe_get(Task, id, check_live=True)

        if siblingID == 0:
            task.parentID = 0
            task.moveToTop()
            return

        new_sibling = Task.get(siblingID)
        assert new_sibling.task_listID == task.task_listID, ("Mismatched tasklists for tasks %d and %d" % (new_sibling.id, task.id))
        task.parentID = new_sibling.parentID
        task.moveBelow(new_sibling)

    @jsonify
    @attrs(action='update', readonly=False)
    def move(self, id):        
        if request.params.has_key('new_parent'):
            new_parent_id = int(request.params['new_parent'])
            self._move_under_parent(id, new_parent_id)
        else:
            new_sibling_id = int(request.params['new_sibling'])
            self._move_below_sibling(id, new_sibling_id)
        
        task = safe_get(Task, id, check_live=True)
        tasks = get_tasks_in_display_order(task.task_list)
        return [dict(id = t.id, depth = t.depth(), has_children = int(bool(len(t.children)))) for t in tasks]
        #return render_text('ok')

    @attrs(action='create', readonly=False)
    @catches_errors
    def show_create(self, id, *args, **kwargs):
        c.task_listID = int(request.params['task_listID'])
        if not c.task_listID:
            raise ValueError("Can only create a task within a task list.")

        c.tasklist = safe_get(TaskList, c.task_listID)
        assert c.tasklist.project == c.project, ("Bad projects!")
        if 'parentID' in request.params:
            c.parentID = request.params['parentID']
        else:
            c.parentID = 0
        c.contextual_wrapper_class = 'tt-context-task-create'
        return render('task/show_create.myt')

    @authenticate
    @attrs(action='create', readonly=False)
    @validate(schema=EditTaskForm(), form='show_create')
    def create(self, *args, **kwargs):
        return self._create_task(**self.form_result)

    @authenticate
    @attrs(action='create', readonly=False)
    def create_ajax(self, id):
        try:
            params = EditTaskForm().to_python(request.params)
            return self._create_task(**params)
        except formencode.api.Invalid, invalid:
            return render_text(invalid.msg, code=500)
    

    def _create_task(self, **p):
        p['creator'] = c.username
        if not p.has_key('task_listID'):
            p['task_listID'] = c.tasklist.id
        if not p.has_key('parentID'):
            p['parentID'] = 0
        siblingID = p['siblingID']
        del p['siblingID']

        assert TaskList.get(p['task_listID']).project == c.project
        c.task = Task(**p)
        
        # some ugly error checking
        assert TaskList.get(p['task_listID']).id == int(p['task_listID'])
        assert int(p['parentID']) == 0 or Task.get(p['parentID']).task_listID == int(p['task_listID'])
        c.depth = 0
        if siblingID > 0:
            self._move_below_sibling(c.task.id, siblingID)
        return render('task/task_list_item.myt', atask=c.task, fragment=True)

    # @@ The next two methods are no longer used, but cannot be removed because
    # security depends upon them.  

    @attrs(action='claim', readonly=False)
    @catches_errors
    def claim(self, id, *args, **kwargs):
        return render("dummy")

    # @@ This is no longer used.
    @attrs(action='assign', readonly=False)
    @catches_errors
    def assign(self, id, *args, **kwargs):
        return render("dummy")

    @attrs(action='comment', readonly=False)
    @catches_errors
    def comment(self, id, *args, **kwargs):
        comment = request.params["text"].strip()
        if not len(comment):
            return Response('')
        c.task = safe_get(Task, id, check_live=True)
        c.comment = Comment(text=h.html2safehtml(comment), user=c.username, task=c.task)
        return Response(c.comment.text)

    @attrs(action='update', readonly=True)
    @catches_errors
    def show_update(self, id, *args, **kwargs):
        c.oldtask = safe_get(Task, id, check_live=True)
        c.owner = c.oldtask.owner
        c.contextual_wrapper_class = 'tt-context-task-update'
        return render('task/show_update.myt')

    # @@ is this ever used?
    @authenticate
    @attrs(action='update', readonly=False)
    @validate(schema=EditTaskForm(), form='show_update')
    def update(self, id):
        c.task = safe_get(Task, id, check_live=True)
        p = self.form_result
        new_parent_id = int(p['parentID'])
        assert new_parent_id == 0 or Task.get(new_parent_id).task_listID == c.task.task_listID
        assert new_parent_id != c.task.id
        p['task_listID'] = c.task.task_listID

        if not _assignment_permitted(p['owner']):
            del p['owner']

        if not p['owner']:
            del p['owner']

        c.task.set(**p)

        return Response.redirect_to(action='show', controller='tasklist', id=c.task.task_listID)

    @attrs(action='update', readonly=False)
    def revertToDate(self, id):
        c.task = safe_get(Task, id, check_live=True)
        date = dateparse(request.params['date'])
        c.task.revertToDate(date)
        return self.show(id)

    @attrs(action='show', readonly=True)
    @catches_errors
    def show(self, id, *args, **kwargs):
        version = request.params.get('version', None)
        if version:
            c.version = version
            c.task = Task.versions.versionClass.get(version)
        else:
            c.task = safe_get(Task, int(id), check_live=True)

        c.parentID = int(id)
        c.tasklist = c.task.task_list
        c.task_listID = c.tasklist.id        
        c.depth = c.task.depth()
        c.permalink = h._get_permalink(request.GET)
        c.prev, c.next = c.task.adjacentTasks(options=h.permalink_to_sql(c.permalink),
                                                                user=c.username, level=c.level)
        #if the task shown would not be shown under the current
        #filters, alter the permalink to remove the filters.
        if not h.is_task_allowed(c.task, c.permalink):
            c.permalink = h._get_permalink_without_filters(request.GET)
        
        c.contextual_wrapper_class = 'tt-context-task-show'
        return render('task/show.myt')

    @authenticate
    @attrs(action='update', readonly=False)
    @catches_errors
    def destroy(self, id, *args, **kwargs):
        c.task = safe_get(Task, id, check_live=True)
        c.task.live = False
        return Response.redirect_to(action='show', controller='tasklist', id=c.task.task_listID)

    @attrs(action='open', readonly=False, restrict_remote_addr=True)
    @catches_errors
    def show_authenticate(self, id, *args, **kwargs):
        return render('task/authenticate.myt')
