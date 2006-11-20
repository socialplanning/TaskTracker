
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

class TemplateController(BaseController):
    @attrs(action='open')
    def view(self, url):
        """
        This is the last place which is tried during a request to try to find a 
        file to serve. It could be used for example to display a template::
        
            def show(self, url):
                return render_response(url)
        
        Or, if you're using Myghty and would like to catch the component not
        found error which will occur when the template doesn't exist; you
        can use the following version which will provide a 404 if the template
        doesn't exist::
        
            import myghty.exception
            
            def show(self, url):
                try:
                    return render_response('/'+url)
                except myghty.exception.ComponentNotFound:
                    return Response(code=404)
        
        The default is just to abort the request with a 404 File not found
        status message.
        """
        abort(404)
