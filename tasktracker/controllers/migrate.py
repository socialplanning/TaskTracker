
# Copyright (C) 2006 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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

from cabochonclient import datetime_to_string
from tasktracker.lib.base import *
from tasktracker.models import *

import tasktracker.lib.helpers as h

class MigrateController(BaseController):
    @attrs(action='migrate', readonly=True, restrict_remote_addr=True)
    def show_initialize_twirlip(self):
        return Response('<form action="%s" method="post"><input type="submit" name="submit" value="migrate"></form>' % h.url_for(action='initialize_twirlip'))
        

    @attrs(action='migrate', readonly=True, restrict_remote_addr=True)
    def initialize_twirlip(self, *args, **kwargs):
        for task in Task.select():
            g.queues['create'].send_message(dict(
                    url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
                    context = h.url_for(controller='tasklist', action='show', id=task.task_listID, qualified=True),
                    categories=['projects/' + task.task_list.project.title, 'tasktracker'],
                    title = task.long_title,
                    user = task.owner,
                    event_class = [],        
                    date = datetime_to_string(datetime.datetime.now()),
                    no_autowatches = 1
                    ))


        return Response("successfully migrated everything to cabochon")
