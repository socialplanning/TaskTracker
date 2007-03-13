
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

import formencode  

class ProjectController(BaseController):

    @attrs(action='initialize', readonly=True)
    @catches_errors
    def initialize(self, *args, **kwargs):
        if c.project.initialized:
            return redirect_to(controller='tasklist')

        c.project.initialized = True
        c.project.readonly = False
        return Response("successfully initialized project")

    @attrs(action='initialize', readonly=True)
    @catches_errors
    def uninitialize(self, *args, **kwargs):
        c.project.initialized = False
        c.project.readonly = True
        return Response("successfully uninitialized project")

    @attrs(action='lock', readonly=True)
    def lock(self):
        c.project.readonly = True
        return Response("successfully locked project")

    @attrs(action='lock', readonly=True)
    def unlock(self):
        c.project.readonly = False
        return Response("successfully unlocked project")

    @attrs(action='show_uninitialized')
    def show_not_permitted(self, id):
        return render_text("This project's security settings do not allow you to perform that operation.")

    @attrs(action='show_uninitialized')
    def show_uninitialized(self, id):
        return render_text('This project has not installed a task tracker.  Talk to a project administrator.')
