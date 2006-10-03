from tasktracker.lib.base import *
from tasktracker.models import *

import formencode  
from formencode.validators import *
import datetime

class CreateTaskForm(formencode.Schema):  
    allow_extra_fields = True  
    title = NotEmpty()
    deadline = formencode.compound.All(DateValidator(earliest_date=datetime.date.today), 
                                       DateConverter())

class TaskController(BaseController):

    def _clean_params(self, params):
        allowed_params = ("title", "text", "status", "deadline", "task_listID")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean

    @attrs(action='change_status')
    @catches_errors
    def change_status(self, id):
        c.task = self.getTask(int(id))
        c.task.status = request.params['status']

        return render_text('ok')

    @attrs(action='update')
    def move(self, id):
        task = self.getTask(int(id))
        new_parent_id = int(request.params['new_parent'])
        assert new_parent_id == 0 or Task.get(new_parent_id).task_listID == task.task_listID
        task.parentID = new_parent_id

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
        c.task = Task(**self._clean_params(self.form_result))

        return redirect_to(action='view',controller='tasklist', id=request.params['task_listID'])

    @attrs(action='comment')
    @catches_errors
    def comment(self, id):
        c.task = Task.get(int(id))
        comment = Comment(text=request.params["text"], user=request.params["user"], task=c.task)

        return redirect_to(action='view',id=c.task.id)

    @attrs(action='update')
    @catches_errors
    def show_update(self, id):
        c.task = self.getTask(int(id))
        return render_response('zpt', 'task.show_update')

    @attrs(action='update')
    @catches_errors
    def update(self, id):
        c.task = self.getTask(int(id))
        c.task.set(**self._clean_params(request.params))

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
        return render_response('zpt', 'task.view')

    @attrs(action='create')
    @catches_errors
    def destroy(self, id):
        c.task = self.getTask(int(id))
        c.task.live = False
        c.flash = "Deleted."
        return redirect_to(action='view', controller='tasklist', id=c.task.task_listID)
