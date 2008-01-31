
# Copyright (C) 2006-2007 The Open Planning Project

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

from paste.deploy import loadapp, appconfig, CONFIG

from tasktracker.models import soClasses, Task, TaskList
from tasktracker.config.environment import load_environment


import os
import sys

here_dir = os.path.dirname(__file__)
conf_dir = os.path.dirname(here_dir)

sys.path.insert(0, conf_dir)

import pkg_resources

pkg_resources.working_set.add_entry(conf_dir)

from tasktracker.models import *

def setRoles(action, roles):
    """Sets the allowed roles for an action"""
    for role in roles:
        if not role in action.roles:
            action.addRole(role)

def setSecurity(policy, actions):
    """SSets up a security policy's actions"""
    for action_name, role in actions.items():
        action_obj = Action.selectBy(action=action_name)[0]
        SecurityPolicyAction(simple_security_policyID = policy.id, action=action_obj, min_level = role.level)

def setup_config(command, filename, section, vars):
    """
    Set up the task tracker's fixtures
    """

    dummy, sect = section.split(':')

    conf = appconfig('config:%s#%s' % (filename, sect), relative_to=conf_dir)
    load_environment(conf.global_conf, conf.local_conf, setup_config=True)
    
    CONFIG.push_process_config({'app_conf': conf.local_conf,
                                'global_conf': conf.global_conf})
    
    #you'll need these when you need to zap tables
    # DONT EVER UNCOMMENT THIS CODE.
    # for table in soClasses[::-1]:
    #    table.dropTable(ifExists=True)
    for table in soClasses:
        table.createTable(ifNotExists=True)

    def makeUser(usename, password="topp"):
        """Makes a user."""
        return User(username=usename, password=password.encode("base64"))

    for user in """admin auth anon magicbronson rmarianski jhammel cabraham ltucker novalis
                 rob whit ian smk jarasi cholmes bryan vanessa""".split():
        makeUser(user)


    def makeRole(**kwargs):
        """Makes a role if it doesn't already exist."""
        role = Role.selectBy(name = kwargs['name'])
        if role.count():
            role = role[0]
            role.set(**kwargs)
            return role
        else:
            return Role(**kwargs)

    def makeAction(**kwargs):
        """Makes an action if it doesn't already exist."""
        action = Action.selectBy(action = kwargs['action'])
        if action.count():
            action = action[0]
            action.set(**kwargs)
            return action
        else:
            return Action(**kwargs)
            

    anon = makeRole(name="Anonymous",
                    description="Anyone at all", level=100)
    auth = makeRole(name="Authenticated",
                    description="Any logged-in OpenPlans user", level=60)
    pm = makeRole(name="ProjectMember",
                  description="Any project member", level=50)
    taskowner = makeRole(name="TaskOwner",
                    description="The person who owns the task", level=40)
    manager = makeRole(name="ListOwner",
                       description="Any person who owns the list", level=30)
    pa = makeRole(name="ProjectAdmin",
                  description="Any project administrator", level=20)
    
    all = [manager, pm, auth, anon]
    members = [manager, pm, auth]

    setRoles(makeAction(action="tasklist_create"), [pa, pm])
    setRoles(makeAction(action="tasklist_delete"), [pa, manager])

    setRoles(makeAction(action="task_show"), all)
    setRoles(makeAction(action="tasklist_show"), all)

    setRoles(makeAction(action="tasklist_update"), [manager, pa])

    setRoles(makeAction(action="task_create"), all)
    setRoles(makeAction(action="task_update"), all)
    setRoles(makeAction(action="task_claim"), members)

    setRoles(makeAction(action="task_change_status"), all)
    setRoles(makeAction(action="task_assign"), members)

    setRoles(makeAction(action="task_comment"), members)




