
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
from formencode.validators import *

class WatcherUpdateForm(formencode.Schema):  
    allow_extra_fields = True  
    filter_extra_fields = True  
    interest_level = Int()

class WatcherController(BaseController):

    def _get_watcher_target(self):
        id = int(request.params['targetID'])
        if request.params['type'] == 'task':
            c.type = request.params['type']
            return Task.get(id)
        else:
            c.type = request.params['type']
            return TaskList.get(id)

    def _show_watcher_target(self, watcher):
        if watcher.taskID:
            return Response.redirect_to(action='show', controller='task', id=watcher.taskID)
        else:
            return Response.redirect_to(action='show', controller='tasklist', id=watcher.task_listID)

    def _get_watcher(self):
        if request.params['type'] == "task":
            watcher = Watcher.selectBy(username=c.username, taskID=c.target.id)
        else:
            watcher = Watcher.selectBy(username=c.username, task_listID=c.target.id)
        if watcher.count():
            return watcher[0]
        else:
            return None

    def check_email(self):
        if not c.user_info.get('email', None):
            redirect_to(action='missing_email', controller='watcher')

    @attrs(action='open')
    def missing_email(self):
        return render_response('zpt', 'watcher.missing_email')

    @attrs(action='loggedin')
    def show_create(self, id):
        c.target = self._get_watcher_target()
        return render_response('zpt', 'watcher.show_create')

    @attrs(action='edit')
    def show_update(self, id):
        self.check_email()
        watcher = Watcher.get(int(id))
        c.target = watcher.target()
        c.interest_level = watcher.interest_level
        c.watcher_id = watcher.id
        return render_response('zpt', 'watcher.show_update')
        
    @attrs(action='loggedin')
    def create(self, id):
        self.check_email()
        c.target = self._get_watcher_target()
        if c.target.isWatchedBy(c.username):
            watcher = self._get_watcher()
            return self.update(watcher.id)
        else:
            taskID = task_listID = 0
            if c.type == 'task':
                taskID = c.target.id
            else:
                task_listID = c.target.id
            watcher = Watcher(username=c.username, taskID=taskID, task_listID=task_listID, interest_level=int(request.params['interest_level']))
            return self._show_watcher_target(watcher)

        
    @attrs(action='edit')
    @validate(schema=WatcherUpdateForm(), form='show_update')
    def update(self, id):
        self.check_email()
        watcher = Watcher.get(int(id))
        p = dict(self.form_result)
        p['username'] = c.username
        watcher.set(**p)
        return self._show_watcher_target(watcher)

    @attrs(action='edit')
    def destroy(self, id):
        self.check_email()
        watcher = Watcher.get(int(id))
        c.task_id = watcher.taskID
        watcher.destroySelf()
        return Response.redirect_to(action='show', controller='task', id=c.task_id)

