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

def setRoles(action, roles):
    for role in roles:
        action.addRole(role)

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

    anon = Role(name="Anonymous",
                description="Anyone at all", level=100)
    auth = Role(name="Authenticated",
                description="Any logged-in OpenPlans user", level=60)
    to = Role(name="TaskOwner",
              description="The person who owns the task", level=50)
    pm = Role(name="ProjectMember",
              description="Any project member", level=40)
    lo = Role(name="ListOwner",
              description="Any person who owns the list", level=30)
    pa = Role(name="ProjectAdmin",
              description="Any project administrator", level=20)

    everyone = [anon, auth, pm, to, lo, pa]
    everyone_but_anon = [anon, auth, pm, to, lo, pa]
    everyone_but_to = [auth, pm, lo, pa]
    members_but_not_to = [pm, lo, pa]
    members = [pm, to, lo, pa]

    setRoles(Action(action="tasklist_view", 
                    question="Who can view the task list?"),
             everyone)
    setRoles(Action(action="tasklist_update",
                    question="Who can update the task list?"),
             members_but_not_to)

    setRoles(Action(action="task_create",
                    question="Who can create tasks in the list?"),
             everyone_but_anon)
    setRoles(Action(action="task_view",
                    question="Who can view public tasks in the list?"),
             everyone)
    setRoles(Action(action="task_update",
                    question="Who can edit public tasks in the list?"),
             everyone_but_anon)
    setRoles(Action(action="task_comment",
                    question="Who can comment on public tasks in the list?"),
             everyone)
    setRoles(Action(action="task_change_status",
                    question="Who can change the status of public tasks in the list?"),
             everyone)
    setRoles(Action(action="task_claim",
                    question="Who can claim public tasks in the list?"),
             everyone_but_anon)

#    setRoles(Action(action="task_own"), everyone_but_to)
    setRoles(Action(action="task_assign",
                    question="Who can assign public tasks in the list?"),
             members)
