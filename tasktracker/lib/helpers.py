
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
from tasktracker.models import Task, TaskList, Comment

from datebocks_helper import datebocks_field

from stripogram import html2safehtml, html2text
import imp, os

from formencode import htmlfill
from tasktracker.lib.base import render_response
from tasktracker.lib.secure_forms import *

from tasktracker.lib.pretty_date import prettyDate
from random import random
def debugThings(obj = None):
    foo = c
    import pdb; pdb.set_trace()

def previewText(text, length=25):
    #length might be an empty string b/c of tal
    if length == "":
        length = 25
    if not text or not length: return ""
    words = text.split()
    text = []
    total = 0
    while total < length and len(words):
        word = words.pop(0)
        text.append(word)
        total += len(word)
    if len(words):
        text.append ("...")
    return " ".join(text)

def isOverdue(deadline):
    if not deadline:
        return False
    import datetime
    if type(deadline) == type(datetime.date(2006,1,1)):
        date = deadline
    else:
        date = deadline.date()
    if date < datetime.date.today():
        return True
    return False

def readableDate(date):
    if date:
        return prettyDate(date)
    else:
        return "No deadline"

def help(text):
    help_id = 'help_' + str(random())[2:]
    return """
<img src="/images/question.png" onclick="$('%s').toggle();" class="help"/>
<div id="%s" onclick="$('%s').hide()" class="help_text" style="display: none;">%s</div>
""" % (help_id, help_id, help_id, text)

def editable_list(field, updateable_items=[], fixed_items=[]):
    out = ['<ul id="list_%s" class="task_list" field="%s">' % (field, field)]
    for item in updateable_items:
        out.append('<li class="removable_list_item">')
        out.append("<span>%s</span></li>" % item)
    for item in fixed_items:
        out.append('<li class="unremovable_list_item">')
        out.append("<span>%s</span></li>" % item)

    out.append("</ul>")
    return "\n".join(out)

def taskListDropDown(id):
    tasklist = [(tasklist.title, tasklist.id) 
                for tasklist in TaskList.selectBy(live=True, projectID=c.project.id) 
                if has_permission('tasklist', 'show', id=tasklist.id)]
    return select('task_listID', options_for_select(tasklist, selected=id))

def sortableColumn(field, fieldname = None):
    if fieldname is None:
        fieldname = field
    span = """
    <th class="%s-column" onclick="sortBy('%s');">
    <span class="column-heading %s-column" sortOrder=''">%s
      <span style="display:none;" class="sort-arrows" id="%s-arrows">&nbsp;
       <span id="%s-down-arrow">&#x2193;</span>
       <span id="%s-up-arrow">&#x2191;</span>
      </span>
    </span>
    </th>""" % (field, field, field, fieldname, field, field, field)
    return span

def editableField(task, field, ifNone = None):
    editable = has_permission('task', 'change_field', id=task.id, field=field)
    if field == 'owner':
        #this is fairly complicated.  Cases:
        #1. person is a list owner.  Then what's there now is good.
        #2. someone owns task.  Then need just 'owner' and that's it.
        #3. person can claim task.  then you just need 'claim this' link.
        #4. else 'no owner'
        if not task.task_list.isListOwner(c.username):
            if task.owner:
                editable = False
            if editable:
                return """<input type="hidden" name="owner_%d" id="owner_%d" value="%s">
                          <a onclick="changeField(%d, &quot;owner&quot;); return false;">Claim this!</a>""" % (task.id, task.id, c.username, task.id)


    out = []
    contents = getattr(task, field)

    if field == 'status' and not task.task_list.hasFeature('custom_status'):
        checked = False
        if task.status == 'done':
            checked = True
        return check_box('status', enabled=editable, checked=checked, id='status_%d' % task.id, **_selectjs('status', task.id))

    if editable:
        span = """<span class="%s-column" id="%s-form_%d" style="display:none">""" % (field, field, task.id)

        span_contents = "%s <div></div>" % (_fieldHelpers[field](task))
        out.append("%s %s </span>" % (span, span_contents))
    
        if not contents:
            contents = ifNone
            if contents is None:
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

def _selectjs(field, id):
    def _onblur(field, id):
        return '$("%s-form_%d").hide(); $("%s-label_%d").show();' % (field, id, field, id)

    def _onchange(field, id):
        return 'changeField(%d, "%s");'  % (id, field)

    return dict(onblur=_onblur(field, id), onchange=_onchange(field, id))

def _prioritySelect(task):
    priority = task.priority
    id = task.id
    onchange = 'changeField(%d, "priority");'  % task.id
    return select('priority', options_for_select([(s, s) for s in 'High Medium Low None'.split()], priority),
                  method='post', originalvalue=priority, id='priority_%d' % id, **_selectjs('priority', id))

def _deadlineInput(task):
    orig = "No deadline"
    if task.deadline:
        orig = task.deadline
    return datebocks_field('atask', 'deadline', options={'dateType':"'us'"}, attributes={'id':'deadline_%d' % task.id}, 
                           input_attributes=dict(originalvalue=str(orig)), value=task.deadline)
                        
def _statusSelect(task):
    statuses = task.task_list.statuses
    status_names = [(s.name, s.name) for s in statuses]
    
    index = 0
    for status in statuses:
        if status.name == task.status:
            break
        index += 1

    return select('status', options_for_select(status_names, task.status), 
                  method='post', originalvalue=task.status,
                  id='status_%d' % task.id, **_selectjs('status', task.id))

def _ownerInput(task):
    orig = "No owner"
    if task.owner:
        orig = task.owner    

        input = text_field('owner', autocomplete="off", originalvalue=orig, size=15,
                           id="owner_%d" % task.id, value=task.owner, **_selectjs("owner", task.id))
        span = """<span class="autocomplete" id="owner_auto_complete_%d"></span>""" % task.id
        script = """<script type="text/javascript">
             new Ajax.Autocompleter('owner_%d',
             'owner_auto_complete_%d', '../../../task/auto_complete_for/owner', {});</script>""" % (task.id, task.id)
        return "%s\n%s\n%s" % (input, span, script)

def columnFilter(field, tasklist = None):
    out = []
    onblur = """filterListByAllFields();"""
    filter = globals()["_%sFilter" % field](onblur = onblur, tasklist = tasklist)
    onclick = """showFilterColumn('%s');""" % field
    span = """<span id="%s-filter-label" onclick="%s">All</span>""" % (field, onclick)
    
    return filter

def _deadlineFilter(onblur = None, tasklist = None):
    return select('deadline_filter', options_for_select([('Past due', -1), ('Due today', 0), ('Due tomorrow',1),
                                                         ('Due in the next week',"0,7"), ('No deadline','None'), ('All','All')], 'All'),
                  method='post', originalvalue='All', id='deadline_filter', 
                  onblur=onblur, onchange=onblur)

def _updatedFilter(onblur = None, tasklist = None):
    return select('updated_filter', options_for_select([('Today', 0), ('Yesterday', -1), ('In the past week',"-7,0"), ('All','All')], 'All'),
                  method='post', originalvalue='All', id='updated_filter', 
                  onblur=onblur, onchange=onblur)

def _priorityFilter(onblur = None, tasklist = None):
    options = [(s, s) for s in 'High,Medium,Low'.split(',')]
    options.extend([('No priority','None'), ('All','All')])
    return select('priority_filter', options_for_select(options, 'All'),
                  method='post', originalvalue='All', id='priority_filter',
                  onblur=onblur, onchange=onblur)

def _statusFilter(onblur = None, tasklist = None):
    statuses = [status.name for status in tasklist.statuses]
    status_dict = {'All':'All'}
    for status in statuses:
        status_dict[status] = status
    return select('status_filter', options_for_select(status_dict.items(), 'All'),
                  method='post', originalvalue='All', id='status_filter', 
                  onblur=onblur, onchange=onblur)

def _ownerFilter(onblur = None, tasklist = None):
    owners = [task.owner for task in tasklist.tasks]
    owner_dict = dict()
    for owner in owners:
        if not owner:
            pass 
        else:
            owner_dict[owner] = owner
    options = owner_dict.items()
    options.extend([("No owner", ""), ("All","All")])
    return select('owner_filter', options_for_select(options, 'All'),
                  method='post', originalvalue='All', id='owner_filter', 
                  onblur=onblur, onchange=onblur)

def _textArea(task):
    orig = task.text
    area = text_area('text_%d' % task.id, id = 'text_%d' % task.id, originalvalue=orig, 
                     content=orig, rows=5, cols=80)
    onclick = """changeField(%d, "text"); $("text-form_%d").hide(); $("text-label_%d").innerHTML = $("text_%d").value; 
                 $("text-label_%d").show(); return false;""" % (task.id, task.id, task.id, task.id, task.id)
    button = submit('submit', onclick = onclick)
    return area + button

def _titleInput(task):
    orig = task.title
    return text_field('title_%d' % task.id, id = 'title_%d' % task.id, originalvalue=orig, 
                      value=orig, **_selectjs("title", task.id))


_fieldHelpers = dict(status=_statusSelect, deadline=_deadlineInput, priority=_prioritySelect, owner=_ownerInput, text=_textArea, title=_titleInput)
    
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
    response = render_response(template)
    d = sqlobject_to_dict(obj)
    d.update(extra_dict)
    response.content = [htmlfill.render("".join(response.content), d)]
    return response

#FIXME: merge with previewText
def shorter(text):
    if len(text) <= 100:
        return text
    else:
        segment = text[:100]
        #make sure we're not stopping in the middle of a tag.
        i = len(segment) - 1
        for c in reversed(segment):
            if c == '>':
                break #good
            if c == '<':
                segment = segment[:i]
            i -= 1

        hidden_id = 'hidden_' + str(random())[2:]
        return '<span id="%s">%s</span> <span id="more_%s" onclick="%s.show(); more_%s.hide();">(more...)</span>' % (hidden_id, segment, hidden_id, hidden_id, hidden_id)

def render_actions(actions, cutoff=5):
    returns = []
    actionslice = actions[:cutoff]
    for action in actionslice:
        last_action = False
        if action == actionslice[-1]:
            last_action = True
        returns.append(render_action(action, last_action))
    return "\n".join(returns)

def render_action(action, last_action=False):
    if isinstance(action, Comment):
        comment = html2safehtml(action.text)
        comment += "<br/>Comment from %s by %s" % (prettyDate(action.date), action.user)
    else:
        fields = action.getChangedFields()
        if not fields:
            return ''
        for field in ['Sort_Index', 'Parentid']:
            if field in fields:
                fields.remove (field)
        if not fields:
            return ''
        if 'Text' in fields:
            fields.remove('Text')
            fields.append('Description')
        if 'Private' in fields:
            fields.remove('Private')
            fields.append('Privacy')
        comment = "%s updated %s by %s" % (", ".join (fields), prettyDate(action.dateArchived), action.updatedBy)
    if last_action:
        hr = ''
    else:
        hr = "<hr/>"
    return '<li>%s%s</li>' % (comment, hr)


def field_last_updated(task, field):
    the_version = None
    for version in reversed(list(task.versions)):
        if field.title() in version.getChangedFields():
            the_version = version
            break
    if not the_version:
        return ""
    return "<b>%s by %s</b>" % (prettyDate(the_version.dateArchived), the_version.updatedBy)


def task_item_tr(task, is_preview, no_second_row, is_flat, editable_title):
    tr = ['<tr parentID="%s" id="task_%d" task_id="%d" ' % (task.parentID, task.id, task.id)]

    for prop in ['sort_index', 'owner', 'deadline', 'priority', 'status', 'updated']:
            tr.append('%s = "%s" ' % (prop, getattr(task, prop)))

    tr.append('is_preview = "%s" ' % is_preview)
    tr.append('no_second_row = "%s" ' % no_second_row)
    tr.append('is_flat = "%s" ' % is_flat)
    tr.append('editable_title = "%s" ' % editable_title)

    tr.append('class = "taskrow task-item ')
    if has_permission('task', 'update', id=task.id):
        tr.append ('deletable ')
    else:
        tr.append ('nondeletable ')
    tr.append ('">')
    return "".join(tr)
             

def test(cond, true, false):
    if cond:
        return true
    else:
        return false

special_plurals = dict(child='children')

def plural(word, count):
    try:
        count = len(count)
    except:
        pass

    plural = special_plurals.get(word, None)
    if plural:
        return plural
        
    if word.endswith("x") or word.endswith("s") or word.endswith("ch") or word.endswith("sh"):
        return word + "es"
    else:
        return word + "s"
