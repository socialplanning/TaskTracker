from tasktracker.lib.base import *
from tasktracker.models import *

from tasktracker.lib import helpers as h
import formencode
from formencode.validators import *
from tasktracker.lib.datetimeconverter import *

class CreateTaskForm(formencode.Schema):  
    allow_extra_fields = True  
    title = NotEmpty()
    deadline = formencode.compound.All(DateValidator(earliest_date=datetime.datetime.today),
                                       DateTimeConverter())

class StatusChangeForm(formencode.Schema):
    allow_extra_fields = True
    status = formencode.validators.OneOf([status.name for status in Status.select()])

class TaskController(BaseController):

    def _clean_params(self, params):
        allowed_params = ("title", "text", "status", "deadline", "task_listID", "owner", "private")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean

    @validate(schema=StatusChangeForm(), form='show_update')
    @attrs(action='change_status')
    @catches_errors
    def change_status(self, id):
        c.task = self.getTask(int(id))
        c.task.status = self.form_result['status']
        return render_text('ok')

    @attrs(action='view')
    def auto_complete_for_owner(self, id):
        c.task = self.getTask(int(id))
        partial = request.params['owner']
        users = list(c.users)

        users = filter(lambda u: u.lower().startswith(partial.lower()), users)

        return render_text('<ul class="autocomplete">%s</ul>' % ''.join(['<li>%s</li>' % u for u in users]))

    @attrs(action='update')
    def move(self, id):
        task = self.getTask(int(id))
        if request.params.has_key ('new_parent'):

            new_parent_id = int(request.params['new_parent'])
            assert new_parent_id == 0 or Task.get(new_parent_id).task_listID == task.task_listID
            task.parentID = new_parent_id
            task.moveToTop()
        else:
            new_sibling_id = int(request.params['new_sibling'])
            new_sibling = Task.get(new_sibling_id)
            assert new_sibling.task_listID == task.task_listID
            task.parentID = new_sibling.parentID
            task.moveBelow(new_sibling)

        return render_text('ok')

    @attrs(action='create')
    @catches_errors
    def show_create(self, id):
        c.task_listID = int(request.params['task_listID'])
        if not c.task_listID:
            raise ValueError("Can only create a task within a task list.")

        c.tasklist = TaskList.get(c.task_listID)
        return render_response('zpt', 'task.show_create')

    @attrs(action='create')
    @validate(schema=CreateTaskForm(), form='show_create')  
    def create(self):
        p = self._clean_params(self.form_result)
        if not (c.level <= Role.getLevel('ProjectAdmin') or
                TaskList.get(p['task_listID']).isOwnedBy(c.username)):
            p['private'] = False

        c.task = Task(**p)

        return redirect_to(action='view',controller='tasklist', id=request.params['task_listID'])

    @attrs(action='claim')
    @catches_errors
    def claim(self, id):
        c.task = self.getTask(id)
        c.task.owner = c.username
        return redirect_to(action='view',controller='task', id=id)

    @attrs(action='assign')
    @catches_errors
    def assign(self, id):
        c.task = self.getTask(id)
        c.task.owner = c.username
        return redirect_to(action='view',controller='task', id=id)

    @attrs(action='comment')
    @catches_errors
    def comment(self, id):
        c.task = Task.get(int(id))
        comment = Comment(text=request.params["text"], user=c.username, task=c.task)

        return redirect_to(action='view',id=c.task.id)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id):
        c.task = self.getTask(int(id))
        c.owner = c.task.owner.title
        return render_response('zpt', 'task.show_update')

    @attrs(action='update')
    @validate(schema=CreateTaskForm(), form='show_update')
    def update(self, id):
        c.task = self.getTask(int(id))
        p = self._clean_params(self.form_result)

        if not (h.has_permission(controller='task', action='assign') or p['owner'] == c.username and h.has_permission(controller='task', action='claim')):
            del p['owner']

        if not p['owner']:
            del p['owner']

        c.task.set(**p)

        return redirect_to(action='view', controller='tasklist', id=c.task.task_listID)

    def getTask(self, id):
        try:
            return Task.get(int(id))
        except LookupError:
            raise NoSuchIdError("No such task ID: %s" % id)

    @attrs(action='view')
    @catches_errors
    def view(self, id):
        c.task = self.getTask(int(id))
        c.tasklist = c.task.task_list
        c.depth = c.task.depth() + 1
        return render_response('zpt', 'task.view')

    @attrs(action='update')
    @catches_errors
    def destroy(self, id):
        c.task = self.getTask(int(id))
        c.task.live = False
        return redirect_to(action='view', controller='tasklist', id=c.task.task_listID)

