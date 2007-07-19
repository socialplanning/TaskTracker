
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

"""
Setup your Routes options here
"""
import sys, os
from routes import Mapper

def is_safe_method(environ, match_dict):

    action = match_dict['action']
    
    if action.startswith("show") or action.startswith("index"):
        return True
    
    return environ['REQUEST_METHOD'] == 'POST'
    
def make_map():
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    map = Mapper(directory=os.path.join(root_path, 'controllers'))
    
    # This route handles displaying the error page and graphics used in the 404/500
    # error pages. It should likely stay at the top to ensure that the error page is
    # displayed properly.
    map.connect('error/:action/:id', controller='error')
    
    # Define your routes. The more specific and detailed routes should be defined first,
    # so they may take precedent over the more generic routes. For more information, refer
    # to the routes manual @ http://routes.groovie.org/docs/

    map.connect('modify-contents', 'modify-contents',
                controller='tasklist', action='batch_form')
    map.connect('manage-tasklists', 'manage',
                controller='tasklist', action='show_widget_project_tasklists')
    map.connect('home', '', controller='tasklist', action='index')

    map.connect(':controller/:action/:id', conditions=dict(function=is_safe_method))
    map.connect('home', '', controller='tasklist', action='index')

    map.connect('*url', controller='template', action='view')

    return map
