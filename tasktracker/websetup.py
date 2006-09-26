# THIS FILE IS BROKEN

from paste.deploy import loadapp, appconfig, CONFIG

from tasktracker.models import soClasses, Task, TaskList

import os
import sys

here_dir = os.path.dirname(__file__)
conf_dir = os.path.dirname(here_dir)

sys.path.insert(0, conf_dir)

import pkg_resources

pkg_resources.working_set.add_entry(conf_dir)

from tasktracker.models import *

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup tasktracker here.
    """

    dummy, sect = section.split(':')

    conf = appconfig('config:%s#%s' % (filename, sect), relative_to=conf_dir)
    CONFIG.push_process_config({'app_conf': conf.local_conf,
                                'global_conf': conf.global_conf})
    for table in soClasses[::-1]:
        table.dropTable(ifExists=True)

    for table in soClasses:
        table.createTable(ifNotExists=True)

    Role(title="Anonymous", level=100)
    Role(title="Authenticated", level=60)
    Role(title="ProjectMember", level=50)
    Role(title="TaskOwner", level=40)
    Role(title="ListOwner", level=30)
    Role(title="ProjectAdmin", level=20)
    Role(title="Deity", level=0)


    Permission(action="tasklist_view", min_level=Role.getLevel('Anonymous'))
    Permission(action="task_view", min_level=Role.getLevel('Anonymous'))
    Permission(action="task_create", min_level=Role.getLevel('Authenticated'))
    Permission(action="task_update", min_level=Role.getLevel('Authenticated'))
    Permission(action="task_change_status", min_level=Role.getLevel('Anonymous'))
    Permission(action="task_claim", min_level=Role.getLevel('Authenticated'))
    Permission(action="task_own", min_level=Role.getLevel('Authenticated'))
    Permission(action="task_assign", min_level=Role.getLevel('ProjectMember'))
