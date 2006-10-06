"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.util import _, log, set_lang, get_lang
from routes import url_for
from pylons import Response, c, g, cache, request, session
from tasktracker.models import Task, TaskList

import imp, os

def taskListDropDown(id):
    tasklist = [(tasklist.title, tasklist.id) for tasklist in TaskList.selectBy(live=True)]
    return select('task_listID', options_for_select(tasklist, selected=id))


from tasktracker.lib.base import c

def text_field_r(object_name, field_name, **kwargs):
    obj = getattr(c, object_name, None)
    if obj:
        value = getattr(obj, field_name, None)
    else:
        value = None

    return text_field(field_name, value=value, **kwargs)

def test(*args, **kwargs):
    oop = c
    import pdb; pdb.set_trace()

def text_area_r(object_name, field_name, **kwargs):
    obj = getattr(c, object_name, None)
    if obj:
        value = getattr(obj, field_name, None)
    else:
        value = None

    return text_area(field_name, content=value, **kwargs)

def check_box_r(object_name, field_name, **kwargs):
    obj = getattr(c, object_name, None)
    if obj:
        value = getattr(obj, bool(field_name), None)
    else:
        value = None

    return check_box(field_name, checked=value, **kwargs)


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
