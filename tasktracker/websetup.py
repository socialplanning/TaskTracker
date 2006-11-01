
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
        if not role in action.roles:
            action.addRole(role)

def setSecurity(policy, actions):
    for action_name, role in actions.items():
        action_obj = Action.selectBy(action=action_name)[0]
        SecurityPolicyAction(simple_security_policyID = policy.id, action=action_obj, min_level = role.level)

def setup_config(command, filename, section, vars):
    """
    Place any commands to setup tasktracker here.
    """

    dummy, sect = section.split(':')

    conf = appconfig('config:%s#%s' % (filename, sect), relative_to=conf_dir)
    CONFIG.push_process_config({'app_conf': conf.local_conf,
                                'global_conf': conf.global_conf})
    
    #you'll need these when you need to zap tables
    #for table in soClasses[::-1]:
    #    table.dropTable(ifExists=True)
    for table in soClasses:
        table.createTable(ifNotExists=True)

    def make_user(usename, password="topp"):
        return User(username=usename, password=password.encode("base64"))

    for user in """admin magicbronson rmarianski jhammel cabraham ltucker novais
                 rob whit ian smk jarasi cholmes bryan vanessa""".split():
        make_user(user)


    def makeRole(**kwargs):
        role = Role.selectBy(name = kwargs['name'])
        if role.count():
            role = role[0]
            role.set(**kwargs)
            return role
        else:
            return Role(**kwargs)

    def makeAction(**kwargs):
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
    to = makeRole(name="TaskOwner",
                  description="The person who owns the task", level=40)
    lo = makeRole(name="ListOwner",
                  description="Any person who owns the list", level=30)
    pa = makeRole(name="ProjectAdmin",
                  description="Any project administrator", level=20)

    everyone = [anon, auth, pm, to, lo, pa]
    everyone_but_anon = [anon, auth, pm, to, lo, pa]
    everyone_but_to = [auth, pm, lo, pa]
    members_but_not_to = [pm, lo, pa]
    members = [pm, to, lo, pa]

    setRoles(makeAction(action="tasklist_show", 
                    question="Who can view the task list?"),
             everyone)
    setRoles(makeAction(action="tasklist_update",
                    question="Who can update the task list?"),
             members_but_not_to)

    setRoles(makeAction(action="task_create",
                    question="Who can create tasks in the list?"),
             everyone_but_anon)
    setRoles(makeAction(action="task_show",
                    question="Who can view public tasks in the list?"),
             everyone)
    setRoles(makeAction(action="task_update",
                    question="Who can edit public tasks in the list?"),
             everyone_but_anon)
    setRoles(makeAction(action="task_comment",
                    question="Who can comment on public tasks in the list?"),
             everyone)
    setRoles(makeAction(action="task_change_status",
                    question="Who can change the status of public tasks in the list?"),
             everyone)
    setRoles(makeAction(action="task_claim",
                    question="Who can claim public tasks in the list?"),
             everyone_but_anon)
    setRoles(makeAction(action="task_assign",
                    question="Who can assign public tasks in the list?"),
             members)
    setRoles(makeAction(action="tasklist_private",
                    question="Who can view private tasks in the list (don't edit this)"),
             members)


    open_policy = SimpleSecurityPolicy(name='open')
    medium_policy = SimpleSecurityPolicy(name='medium')
    closed_policy = SimpleSecurityPolicy(name='closed')

    setSecurity(open_policy, {"tasklist_show" : anon, 
                              "tasklist_update" : pm,
                              "task_create" : auth,
                              "task_show" : anon,
                              "task_update" : auth,
                              "task_comment" : auth,
                              "task_change_status" : anon,
                              "task_claim" : auth,
                              "task_assign" : pm,
                              "tasklist_private" : lo,
                              })

    

    setSecurity(medium_policy, {"tasklist_show" : anon, 
                              "tasklist_update" : pm,
                              "task_create" : pm,
                              "task_show" : anon,
                              "task_update" : pm,
                              "task_comment" : auth,
                              "task_change_status" : pm,
                              "task_claim" : auth,
                              "task_assign" : pm,
                              "tasklist_private" : lo,
                                })

    setSecurity(closed_policy, {"tasklist_show" : pa, 
                              "tasklist_update" : pa,
                              "task_create" : lo,
                              "task_show" : anon,
                              "task_update" : lo,
                              "task_comment" : lo,
                              "task_change_status" : lo,
                              "task_claim" : lo,
                              "task_assign" : lo,
                              "tasklist_private" : lo,
                                })
