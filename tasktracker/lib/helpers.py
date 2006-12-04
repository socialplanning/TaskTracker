
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
from tasktracker.models import Task, TaskList

from datebocks_helper import datebocks_field

from stripogram import html2safehtml, html2text
import imp, os

from formencode import htmlfill
from tasktracker.lib.base import render_response

from tasktracker.lib.pretty_date import pretty_date

def debugThings():
    foo = c
    import pdb; pdb.set_trace()

def readableDate(date):
    if date:
        return pretty_date(date)
    else:
        return "No deadline"

def help(text):
    from random import random
    help_id = 'help_' + str(random())[2:]
    return """
<img src="/images/question.png" onclick="$('%s').toggle();" class="help"/>
<div id="%s" onclick="$('%s').hide()" class="help_text" style="display: none;">%s</div>
""" % (help_id, help_id, help_id, text)

def list_with_minuses(id, updateable_items=[], fixed_items=[]):
    updateable_lis = "\n".join([
            """<li id="%s_item_%d">
                 <span>%s</span>
                 <span onclick="deleteItem('%s_item_%d');">[ - ]</span>
               </li>""" % (id, i, updateable_items[i].username, id, i)
            for i in range(0, len(updateable_items))])

    fixed_lis = "\n".join([
            """<li id="%s">
                 <span>%s</span>
               </li>""" % (item, item)
            for item in fixed_items])

    return """<ul id="%s" class="task_list">
    %s
    %s
    </ul>""" % (id, updateable_lis, fixed_lis);

def taskListDropDown(id):
    tasklist = [(tasklist.title, tasklist.id) 
                for tasklist in TaskList.selectBy(live=True, projectID=c.project.id) 
                if has_permission('tasklist', 'show', id=tasklist.id)]
    return select('task_listID', options_for_select(tasklist, selected=id))

def editableField(task, field):
    editable = has_permission('task', 'change_field', id=task.id, field=field)
    out = []
    contents = getattr(task, field)
    if editable:
        span = """<span class="%s-column" id="%s-form_%d" style="display:none">""" % (field, field, task.id)

        span_contents = "%s <div></div>" % (_fieldHelpers[field](task))
        out.append("%s %s </span>" % (span, span_contents))
    
        if not contents:
            contents = "No %s" % field
        elif field == 'deadline':
            contents = readableDate(contents)

        out.append("""<span class="%s-column editable" """ % field)
    else:
        out.append("""<span class="%s-column" """ % field)

    out.append("""id="%s-label_%d" """ % (field, task.id))

    if editable:
        out.append ("""onclick="viewChangeableField(%d, &quot;%s&quot;)" """ % (task.id, field))

    out.append(">%s</span>" % contents)
    
    return " ".join(out)


def _prioritySelect(task, onchange = None):
    priority = task.priority
    id = task.id
    if onchange is None:
        onchange = 'changeField(%d, "priority");'  % task.id
    return select('priority', options_for_select([(s, s) for s in 'High Medium Low None'.split()], priority),
                  method='post', originalvalue=priority, id='priority_%d' % id, 
                  onchange=onchange)

def _deadlineFilter():
    onchange = 'filterDeadline();'
    return select('deadline_filter', options_for_select([('All','All'), ('Thirty Days', 30), ('Seven Days', 7),
                                                         ('Three Days',3), ('Today',0), ('Overdue', -1), ('None','None')], 'All'),
                  method='post', originalvalue='All', id='deadline_filter', 
                  onchange=onchange)

def _priorityFilter(onchange = None):
    if onchange is None:
        onchange = 'filterField("priority");'
    return select('priority_filter', options_for_select([(s, s) for s in 'All High Medium Low None'.split()], 'All'),
                  method='post', originalvalue='All', id='priority_filter', 
                  onchange=onchange)

def _ownerFilter(tasklist):
    owners = [task.owner for task in tasklist.tasks]
    owner_dict = {'All':'All'}
    for owner in owners:
        if not owner:
            owner_dict["No owner"] = ""
        else:
            owner_dict[owner] = owner
    return select('owner_filter', options_for_select(owner_dict.items(), 'All'),
                  method='post', originalvalue='All', id='owner_filter', 
                  onchange='filterField("owner");')

def _ownerInput(task):
    orig = "No owner"
    if task.owner:
        orig = task.owner    

    input = """<input autocomplete="off" originalvalue="%s" name="owner" size="15" type="text"
              id="owner_%d" value="%s" onchange='changeField(%d, "owner");'/>""" % (orig, task.id, task.owner, task.id)
    span = """<span class="autocomplete" id="owner_auto_complete_%d"></span>""" % task.id
    script = """<script type="text/javascript">new Ajax.Autocompleter('owner_%d', 'owner_auto_complete_%d', '../../../task/auto_complete_for_owner/', {});</script>""" % (task.id, task.id)
    return "%s\n%s\n%s" % (input, span, script)
    
def _deadlineInput(task):
    orig = "No deadline"
    if task.deadline:
        orig = task.deadline
    return datebocks_field('atask', 'deadline', options={'dateType':"'us'"}, attributes={'id':'deadline_%d' % task.id}, 
                           input_attributes=dict(originalvalue="%s" % orig), value=task.deadline)
                        
def _statusSelect(task):
    statuses = task.task_list.statuses
    status_names = [(s.name, s.name) for s in statuses]
    index = 0
    for status in statuses:
        if status.name == task.status:
            break
        index += 1
    
#    status_change_url = url_for(controller='task',
#                                  action='change_field',
#                                  id=task.id, field=field)
    return select('status', 
                  options_for_select(status_names, task.status), 
                  method='post', 
                  originalvalue=task.status,
                  id='status_%d' % task.id,
                  onchange='changeField(%d, "status");' % task.id)

_fieldHelpers = dict(status=_statusSelect, deadline=_deadlineInput, priority=_prioritySelect, owner=_ownerInput)
    
def _childTasksForTaskDropDown(this_task_id, task_list_id, parent_id=0, depth=0):
    tasks = []
    for task in Task.selectBy(task_listID=task_list_id, parentID=parent_id):
        if has_permission('task', 'show', id=task.id) and not task.id == this_task_id:
            item = ("%s %s" % ('...' * (depth), task.title), task.id)
            tasks.append(item)
            tasks += _childTasksForTaskDropDown(this_task_id, task_list_id, task.id, depth + 1)
    return tasks

def taskDropDown(id, task_list, initial_value=0, include_this_task=False):
    tasks = [("No parent task",0)]
    if include_this_task:
        id=None
    tasks += _childTasksForTaskDropDown(id, task_list)
    if hasattr(initial_value, 'id'):
        initial_value = initial_value.id
    return select('parentID', options_for_select(tasks, selected=initial_value))

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


def has_permission(controller, action, **params):
#    if action is None:
#        module = imp.load_module('tasktracker/lib/base', *imp.find_module('tasktracker/lib/base'))
#        controller = getattr(module, 'BaseController')

    controller_name = controller

    d = 'tasktracker/controllers/%s' % controller_name
    module = imp.load_module(d, *imp.find_module(d))

    cap_controller = controller_name[0].upper() + controller_name[1:]

    controller = getattr(module, cap_controller + 'Controller')

    action_verb = getattr(controller, action)
    action_verb = action_verb.action

    params['username'] = c.username

    if c.id:
        params.setdefault('id', c.id)

    return controller._has_permission(controller_name, action_verb, params)

def priority_as_int(priority_name):
    priorities = {'High' : 1, 'Medium' : 2, 'Low' : 3, 'None' : 9999}
    priority = priorities.get(priority_name, None)
    if not priority:
        raise ValueError("priority must be one of 'High', 'Medium', 'Low', or 'None'")
    return priority

def interest_levels():
    return [('Just the highlights', 0), ('The works', 1)]

def sqlobject_to_dict(obj):
    out = {}
    columns = obj.__class__.sqlmeta.columns
    for column in columns.keys():
        out[column] = getattr(obj, column)
        
    return out

def filled_render(template, obj, extra_dict={}):
    response = render_response('zpt', template)
    d = sqlobject_to_dict(obj)
    d.update(extra_dict)
    response.content = [htmlfill.render("".join(response.content), d)]
    return response
