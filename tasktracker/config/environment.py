
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

import os

from pylons import config

from tasktracker.config.routing import make_map
import tasktracker.lib.app_globals as app_globals

import pkg_resources

def load_environment(global_conf, app_conf, setup_config=False):
    map = make_map()
    # Setup our paths
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    template_paths = []

#    Myghty doesn't actually support this even though it appears to.

#    if 'template_package' in app_conf:
#        alt_tmpl = pkg_resources.Requirement.parse(app_conf['template_package'])
#        alt_path = pkg_resources.resource_filename(alt_tmpl, 'tasktracker')
#        template_paths.append(os.path.join(alt_path, 'templates'))

    template_paths += [os.path.join(root_path, path) for path in 
                      ('components', 'templates')]

    paths = {'root': root_path,
             'controllers': os.path.join(root_path, 'controllers'),
             'templates': template_paths,
             'static_files': os.path.join(root_path, 'public')
             }
    
    # The following options are passed directly into Myghty, so all configuration options
    # available to the Myghty handler are available for your use here
    myghty = {}
    myghty['log_errors'] = True

    # Add your own Myghty config options here, note that all config options will override
    # any Pylons config options
    
    # Return our loaded config object
    config.init_app(global_conf, app_conf, package='tasktracker',
                    template_engine='pylonsmyghty', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals(setup_config=setup_config)
    import tasktracker.lib.helpers    
    config['pylons.h'] = tasktracker.lib.helpers


    #return pylons.config.Config(myghty, map, paths)
