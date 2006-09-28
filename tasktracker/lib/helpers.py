"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.util import _, log, set_lang, get_lang
from routes import url_for

from tasktracker.models import Task, TaskList

def oppositeStatus(status):
    return Task.oppositeStatus(status)

def taskListDropDown(id):
    tasklist = [(tasklist.title, tasklist.id) for tasklist in TaskList.selectBy(live=True)]
    return select('task_listID', options_for_select(tasklist, selected=id))



from tasktracker.lib.base import c

def text_field_r(object_name, field_name, **kwargs):
    obj = getattr(c, object_name, None)
    if obj:
        value = getattr(obj, field_name)
    else:
        value = None

    return text_field(field_name, value=value, **kwargs)


def text_area_r(object_name, field_name, **kwargs):
    obj = getattr(c, object_name, None)
    if obj:
        value = getattr(obj, field_name)
    else:
        value = None

    return text_area(field_name, content=value, **kwargs)
