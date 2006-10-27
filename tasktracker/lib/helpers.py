
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
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.util import _, log, set_lang, get_lang
from routes import url_for
from pylons import Response, c, g, cache, request, session
from tasktracker.models import Task, TaskList, Role

from datebocks_helper import datebocks_field

from stripogram import html2safehtml, html2text
import imp, os

def debugThings():
    foo = c
    import pdb; pdb.set_trace()

def readableDate(date):
    if date:
        return date.strftime("%d %B, %Y")
    else:
        return None

def list_with_checkboxes(id, updateable_items=[], fixed_items=[]):
    updateable_lis = "\n".join([
            """<li>
                 <input type="checkbox" id="item_%d" onclick="deleteItem('item_%d');"/>
                 <span>%s</span>
               </li>""" % (i, i, updateable_items[i])
            for i in range(0, len(updateable_items))])

    fixed_lis = "\n".join([
            """<li id="%s">
                 <input type="checkbox" disabled="disabled"/>
                 <span>%s</span>
               </li>""" % (item, item)
            for item in fixed_items])

    return """<ul id="%s" class="task_list">
    %s
    %s
    </ul>""" % (id, updateable_lis, fixed_lis);


def taskListDropDown(id):
    tasklist = [(tasklist.title, tasklist.id) for tasklist in TaskList.selectBy(live=True, projectID=c.project.id) if has_permission('tasklist', 'view', id=tasklist.id)]
    return select('task_listID', options_for_select(tasklist, selected=id))

def taskDropDown(id, task_list, username, level):
    tasks = [("No parent task",0)] + \
            [("%s%s" % ('%s%s' % (' ' * (task.depth() - 1), '\-->' * (task.depth() == True)), task.title), task.id)
             for task in Task.selectBy(live=True, task_listID=task_list)
             if has_permission('task', 'view', id=task_list)]
#    priv_tasks = Task.selectBy(private=True)
#    if level <= Role.getLevel('ProjectAdmin'):
#        priv_tasks = [(task.title, task.id) for task in Task.selectBy(private=True,live=True)]
#    else:
#        priv_tasks = [(task.title, task.id) for task in Task.selectBy(private=True, live=True) if
#                      (task.task_list.isOwnedBy(username)
#                       or task.owner == username)]
    return select('parentID', options_for_select(tasks, selected=id))

from tasktracker.lib.base import c

def get_value(object_name, field_name, default=None):
    key = None
    if '.' in field_name:
        field_name, key = field_name.split('.') # TODO only works for one level deep

    obj = getattr(c, object_name, None)
    if obj:
        if key:
            return getattr(obj, field_name, None).get(key, None)
        else:
            return getattr(obj, field_name, None)
    else:
        return default


def text_field_r(object_name, field_name, **kwargs):
    return text_field(field_name, value=get_value(object_name, field_name), **kwargs)

def text_area_r(object_name, field_name, **kwargs):
    return text_area(field_name, content=get_value(object_name, field_name), **kwargs)

def check_box_r(object_name, field_name, **kwargs):
    value = get_value(object_name, field_name)

    if value:
        checked = 'checked'
    else:
        checked = ''

    return check_box(field_name, checked=checked, **kwargs)

def has_permission(controller=None, action=None, **params):
    controller_name = controller

    d = 'tasktracker/controllers/%s' % controller_name
    module = imp.load_module(d, *imp.find_module(d))

    cap_controller = controller_name[0].upper() + controller_name[1:]

    controller = getattr(module, cap_controller + 'Controller')

    action_verb = getattr(controller, action).action
        
    action_name = controller_name + '_' + action_verb

    params['username'] = c.username

    if c.id:
        params.setdefault('id', c.id)

    return controller._has_permission(controller_name, action_name, params)

def priority_as_int(priority):
    if priority == 'High':
        return 1
    if priority == 'Medium':
        return 2
    if priority == 'Low':
        return 3
    if priority == 'None':
        return 9999;
    raise ValueError("priority must be one of 'High', 'Medium', 'Low', or 'None'")
