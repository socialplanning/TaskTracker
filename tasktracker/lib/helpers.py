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

