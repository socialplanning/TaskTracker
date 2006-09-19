import os

import pylons.config

from tasktracker.config.routing import make_map

def load_environment():
    map = make_map()
    # Setup our paths
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = {'root_path': root_path,
             'controllers': os.path.join(root_path, 'controllers'),
             'templates': [os.path.join(root_path, path) for path in \
                           ('components', 'templates')],
             'static_files': os.path.join(root_path, 'public')
             }
    
    # The following options are passed directly into Myghty, so all configuration options
    # available to the Myghty handler are available for your use here
    myghty = {}
    myghty['log_errors'] = True
    
    # Add your own Myghty config options here, note that all config options will override
    # any Pylons config options
    
    # Return our loaded config object
    return pylons.config.Config(myghty, map, paths)
