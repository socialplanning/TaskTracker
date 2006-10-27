
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

from tasktracker.lib.base import c
from tasktracker.lib.base import render_response as render_body

def render_response(templateEngine, page, *args):
    
    body = render_body(templateEngine, page, *args)
    if body.status_code == 200 and not page.split(".")[-1].startswith("_"):
        #don't apply the layout to partials
        c.body_content = ''.join(body.content)
       
        body = render_body(templateEngine, "layout")

    return body
