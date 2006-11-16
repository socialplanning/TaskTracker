
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


class ViewController(BaseController):

    def clean_params(self, params):
        allowed_params = ("title", "text", "status")
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
        c.task = Task(**self.clean_params(request.params))

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

        return redirect_to(action='index')

    def getTask(self, id):
        try:
            return Task.get(int(id))
        except LookupError:
            raise NoSuchIdError("No such task ID: %s" % id)

    @catches_errors
    def view(self, id, *args, **kwargs):
        c.task = self.getTask(int(id))
        return render_response('zpt', 'view')

    @catches_errors
    def destroy(self, id, *args, **kwargs):
            c.task = Task.get(int(id))
            c.task.live = False
            c.flash = "Deleted."
            return self.index()
        
