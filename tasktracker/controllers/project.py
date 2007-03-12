
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

class StatusListValidator(formencode.FancyValidator):
    def _to_python(self, value, state):
        if not (',' in value and 'done,' in value):
            raise formencode.Invalid(
                CreateProjectForm.atLeastOneStatus,
                value, state)
        return value

class CreateProjectForm(formencode.Schema):  
    allow_extra_fields = True  
    filter_extra_fields = True  
    atLeastOneStatus = 'You need at least one status.  Consider using "done" and "not done".'
    statuses = StatusListValidator(not_empty=True, messages={'empty': atLeastOneStatus})

class ProjectController(BaseController):

    @attrs(action='initialize')
    @validate(schema=CreateProjectForm(), form='show_initialize')
    @catches_errors
    def initialize(self, id, *args, **kwargs):
        c.project = Project.get(id)

        if c.project.initialized:
            print "initialized."
            return redirect_to(controller='tasklist', action='index')

        try:
            c.project.create_list_permission = int(request.params['create_list_permission']) 
        except KeyError:
            raise MissingArgumentError('create_list_permission : %s' % request.params)

        statuses = request.params['statuses'][:-1].split(",")

        for status in statuses:
            Status(name=status, projectID=id)

        c.project.initialized = True
        return redirect_to(controller='tasklist', action='index')

    @attrs(action='initialize')
    @catches_errors
    def show_initialize(self, id, *args, **kwargs):
        c.project = Project.get(id) 
        if c.project.initialized:
            return redirect_to(controller='tasklist', action='index')
        c.adminLevel = Role.getLevel('ProjectAdmin')
        c.memberLevel = Role.getLevel('ProjectMember')
        c.anonymousLevel = Role.getLevel('Anonymous')
        return render_response('zpt', 'project/show_initialize')

    @attrs(action='show_uninitialized')
    def show_not_permitted(self, id):
        return render_text('This project\'s security settings do not allow you to perform that operation.')

    @attrs(action='show_uninitialized')
    def show_uninitialized(self, id):
        return render_text ('This project has not yet set up their task lists.  Talk to a project administrator.')

    @attrs(action='lock', readonly=True)
    def lock(self):
        c.project.readonly = True
        return redirect_to(controller='tasklist', action='index')

    @attrs(action='lock', readonly=True)
    def unlock(self):
        c.project.readonly = False
        return redirect_to(controller='tasklist', action='index')

    
