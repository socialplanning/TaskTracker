from tasktracker.lib.base import *
from tasktracker.models import *


class ViewController(BaseController):

    def clean_params(self, params):
        allowed_params = ("title", "text")
        clean = {}
        for param in allowed_params:
            if params.has_key(param):
                clean[param] = params[param]
        return clean

    def index(self):
        c.tasks = Task.selectBy(live=True)
        return render_response('zpt', 'index')

    def show_create(self):
        return render_response('zpt', 'show_create')

    def create(self):
        c.task = Task()
        c.task.set(**self.clean_params(request.params))

        return redirect_to(action='view',id=c.task.id)

    def comment(self,id):
        c.task = Task.get(int(id))
        comment = Comment(text=request.params["text"], user=request.params["user"], task=c.task)

        return redirect_to(action='view',id=c.task.id)

    def show_update(self, id):
        c.task = Task.get(int(id))
        return render_response('zpt', 'show_update')

    def update(self, id):
        c.task = Task.get(int(id))
        c.task.set(**self.clean_params(request.params))

        return redirect_to(action='view',id=c.task.id)

    def view(self, id):
        try:
            c.task = Task.get(int(id))
            return render_response('zpt', 'view')
        except LookupError:
            c.error = "No such task"
            return render_response('zpt', 'error')            

    def destroy(self, id):
        try:
            c.task = Task.get(int(id))
            c.task.live = False
            c.flash = "Deleted."
            return self.index()
        except LookupError:
            c.error = "No such task"
            return render_response('zpt', 'error')
        
