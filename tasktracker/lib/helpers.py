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

import imp, os

def readableDate(date):
    if date:
        return date.strftime("%d %B, %Y)
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
    tasklist = [(tasklist.title, tasklist.id) for tasklist in TaskList.selectBy(live=True)]
    return select('task_listID', options_for_select(tasklist, selected=id))

def taskDropDown(id, task_list, username, level):
    tasks = [("No parent task",0)] + [(task.title, task.id) for task in Task.selectBy(live=True, task_listID=task_list, private=False)]
    priv_tasks = Task.selectBy(private=True)
    if level <= Role.getLevel('ProjectAdmin'):
        priv_tasks = [(task.title, task.id) for task in Task.selectBy(private=True,live=True)]
    else:
        priv_tasks = [(task.title, task.id) for task in Task.selectBy(private=True, live=True) if
                      (task.task_list.isOwnedBy(username)
                       or task.owner == username)]
    return select('parentID', options_for_select(tasks + priv_tasks, selected=id))

from tasktracker.lib.base import c

def get_value(object_name, field_name):
    key = None
    if '.' in field_name:
        field_name, key = field_name.split('.')

    obj = getattr(c, object_name, None)
    if obj:
        if key:
            return getattr(obj, field_name, None).get(key, None)
        else:
            return getattr(obj, field_name, None)
    else:
        return None


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
