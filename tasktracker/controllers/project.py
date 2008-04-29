
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
import simplejson
import formencode  

class ProjectController(BaseController):

    @attrs(action='open', readonly=True)
    def index(self, *args, **kwargs):
        return Response.redirect_to(url_for('home'))

    @attrs(action='initialize', readonly=True, restrict_remote_addr=True)
    def initialize(self, *args, **kwargs):
        c.project.initialized = True
        c.project.readonly = False
        return Response("successfully initialized project")

    @attrs(action='initialize', readonly=True, restrict_remote_addr=True)
    def uninitialize(self, *args, **kwargs):
        c.project.initialized = False
        c.project.readonly = True
        return Response("successfully uninitialized project")

    @attrs(action='destroy', readonly=True, restrict_remote_addr=True)
    def destroy(self, *args, **kwargs):
        import logging
        log = logging.getLogger('tasktracker')
        log.info('project %s destroy called' % c.project.title)
        c.project.destroySelf()
        return simplejson.dumps({"status" : "accepted"})
    delete = destroy
    
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
        return render_text("This project's security settings do not allow you to perform that operation.") # @@ ugly - egj

    @attrs(action='show_uninitialized')
    def show_uninitialized(self, id):
        return Response("""<html><body><div class="oc-genericError"><div class="oc-statusMessage">Sorry! TaskTracker is currently unavailable.</div></div></body></html>""")
