
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

"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.util import _, log, set_lang, get_lang
from routes import url_for
from pylons import Response, c, g, cache, request, session, config
from tasktracker.models import Task, TaskList, Comment

from datebocks_helper import datebocks_field

from stripogram import html2safehtml
import sys, os

from formencode import htmlfill
from tasktracker.lib.base import render
from tasktracker.lib.secure_forms import *
from tasktracker.lib.urireader import get_twirlip_uri

from topp.utils.pretty_date import prettyDate
from random import random

import formencode.validators

from urllib import quote
import datetime

class SafeHTML(formencode.validators.String):
    def to_python(self, value, state):
        return html2safehtml(super(SafeHTML, self).to_python(value, state))

def debugThings(obj = None):
    foo = c
    import pdb; pdb.set_trace()

link_pattern = r'(http://\S{3,})'
import re
def htmlize(text):
    html = text.replace("\n", "<br/>")
    pat = re.compile(link_pattern)
    html = pat.sub('<a href="\\1">\\1</a>', html)
    return html

def previewText(text, length=25):
    #length might be an empty string b/c of tal
    if length == "":
        length = 25
    if not text or not length: return ""
    words = text[0:length + 1].split()
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

def editable_list(field, updateable_items=[], fixed_items=[]):
    out = ['<ul id="list_%s" class="task_list" field="%s">' % (field, field)]
    for item in fixed_items:
        out.append('<li class="unremovable_list_item">')
        out.append("<span>%s</span>" % item)
        out.append("</li>")

    for item in updateable_items:
        out.append('<li class="removable_list_item">')
        out.append("<span>%s</span>" % item)
        out.append("<span class='command delete_button'>[ - ]</span>")
        out.append("</li>")
        
    out.append("</ul>")
    return "\n".join(out)

def taskListDropDown(id):
    tasklist = [(tasklist.title, tasklist.id) 
                for tasklist in TaskList.selectBy(live=True, projectID=c.project.id) 
                if has_permission('tasklist', 'show', id=tasklist.id)]
    return select('task_listID', options_for_select(tasklist, selected=id))

def sortableColumn(field, fieldname = None, klass = None, colspan=1):
    span = """
    <th id="%s-heading" class="%s draggable-column-heading" colspan="%s">
    <span class="column-heading %s-column" sortOrder=''">%s
      <span style="display:none;" class="sort-arrows" id="%s-arrows">&nbsp;
       <span id="%s-down-arrow">&#x2193;</span>
       <span id="%s-up-arrow">&#x2191;</span>
      </span>
    </span>
    </th>""" % (field, klass or "%s-column" % field, colspan, field, fieldname or field, field, field, field) #""" #stupid syntax highliter
    return span

def editableField(task, field, ifNone = None, uneditable = False, ifNoneUneditable=None):
    if uneditable:
        editable = False
    else:
        editable = has_permission('task', 'change_field', id=task.id, field=field)
    if field == 'owner':
        #this is fairly complicated.  Cases:
        #1. person is a list owner.  Then we need an input box
        #2. someone owns task, and you can steal it.  'steal this'
        #3. someone owns task, but you can't steal it.  just 'owner'
        #4. Nobody owns, but you can claim task.  then you just need 'claim this' link.
        #5. else 'no owner'
        if not task.task_list.isListOwner(c.username):
            #can you claim it?
            if not editable or task.owner == c.username:
                return task.owner or ''

            pre = ''
            claimsteal = 'Claim'
            if task.owner:
                claimsteal = 'Steal'
                pre = task.owner + " " 
            return pre + """<input type="hidden" name="owner_%d" id="owner_%d" value="%s">
                            <input type="hidden" name="authenticator" id="authenticator" value="%s">
                          <a onclick="changeField(%d, &quot;owner&quot;); return false;">%s this!</a>""" % (task.id, task.id, c.username, session_key(), task.id, claimsteal)


    out = []
    contents = getattr(task, field)

    if not contents:
        if editable or ifNoneUneditable is None:
            contents = ifNone
        else:
            contents = ifNoneUneditable
        if contents is None:
            contents = "--"
    elif field == 'deadline':
        contents = readableDate(contents).replace(" ", "&nbsp;")
    elif field == 'priority':
        if contents == 'None':
            contents = '--'
    elif field == 'text':
        contents = htmlize(contents)
    elif field == 'status':
        contents = task.statusName()
        if not task.task_list.hasFeature('custom_status'):
            checked = False
            if task.status.done:
                checked = True
        
            return check_box('status', disabled=not editable, checked=checked, id='status_%d' % task.id, class_="low-profile-widget auto-size", onclick='changeField(%d, "status");' % (task.id))

    if editable:
        span = """<span id="%s-form_%d" style="display:none">""" % (field, task.id)

        span_contents = "%s <div></div>" % (_fieldHelpers[field](task))
        out.append("%s %s </span>" % (span, span_contents))
    
        out.append("""<span class="editable" """)
    else:
        out.append("""<span """)

    out.append("""id="%s-label_%d" """ % (field, task.id))

    if editable:
        out.append ("""onclick="viewChangeableField(%d, &quot;%s&quot;)" """ % (task.id, field))

    out.append(">%s</span>" % contents)
    
    return " ".join(out)

def _selectjs(field, id):
    return dict(onchange='changeField(%d, "%s");'  % (id, field))


def _prioritySelect(task):
    priority = task.priority
    id = task.id
    onchange = 'changeField(%d, "priority");'  % task.id
    return select('priority', options_for_select([(s, s) for s in 'High Medium Low None'.split()], priority),
                  method='post', originalvalue=priority, id='priority_%d' % id, class_="low-profile-widget", **_selectjs('priority', id))

def _deadlineInput(task):
    orig = "No deadline"
    if task.deadline:
        orig = task.deadline
    input_attrs = dict(originalvalue=str(orig)) 
    input_attrs['class'] = 'low-profile-widget'; 
    return datebocks_field('atask', 'deadline', options={'dateType':"'us'"}, attributes={'id':'deadline_%d' % task.id}, 
                           input_attributes=input_attrs, value=task.deadline)
                        
def _statusSelect(task):
    statuses = task.task_list.statuses
    status_names = [(s.name, s.name) for s in statuses]
    
    index = 0
    for status in statuses:
        if status == task.status:
            break
        index += 1

    return select('status', options_for_select(status_names, task.statusName()), 
                  method='post', originalvalue=task.statusName(),
                  id='status_%d' % task.id, class_="low-profile-widget", **_selectjs('status', task.id))


def _ownerInput(task):
    orig = task.owner or '--'
    id = task.id
    owner_names = sorted(c.usermapper.project_member_names(), key=str.lower)
    names = ['--']
    names.extend(owner_names)
    return select("owner", options_for_select(names, orig),
                  method="post", originalvalue=orig,
                  id="owner_%d" % id, class_="low-profile-widget", **_selectjs('owner', id))

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
                  method='post', originalvalue='All', id='deadline_filter', onchange=onblur)

def _updatedFilter(onblur = None, tasklist = None):
    return select('updated_filter', options_for_select([('Today', 0), ('Yesterday', -1), ('In the past week',"-7,0"), ('All','All')], 'All'),
                  method='post', originalvalue='All', id='updated_filter', onchange=onblur)

def _priorityFilter(onblur = None, tasklist = None):
    options = [(s, s) for s in 'High,Medium,Low'.split(',')]
    options.extend([('No priority','None'), ('All','All')])
    return select('priority_filter', options_for_select(options, 'All'),
                  method='post', originalvalue='All', id='priority_filter', onchange=onblur)

def _statusFilter(onblur = None, tasklist = None):
    statuses = [status.name for status in tasklist.statuses]
    status_dict = {'All':'All','All Uncompleted':'AllUncompleted'}
    for status in statuses:
        status_dict[status] = status
    return select('status_filter', options_for_select(status_dict.items(), 'All'),
                  method='post', originalvalue='All', id='status_filter', onchange=onblur)

def _ownerFilter(onblur = None, tasklist = None):
    owners = [task.owner for task in tasklist.tasks]
    owner_dict = dict()
    for owner in owners:
        if owner:
            owner_dict[owner] = owner
    options = owner_dict.items()
    options.extend([("No owner", ""), ("All","All")])
    return select('owner_filter', options_for_select(options, 'All'),
                  method='post', originalvalue='All', id='owner_filter', onchange=onblur)

allowed_permalink_params = set("sortBy sortOrder status deadline priority owner updated columnOrder".split())
def _get_permalink(dikt):
    permalink = ""
    for param in dikt:
        #prevent sql injection
        assert ' ' not in dikt[param], ("Abort to prevent SQL injection in %s" % dikt[param])

        if param in allowed_permalink_params:
            permalink = "%s%s=%s&" % (permalink, param, dikt[param])
    return permalink

def _get_permalink_without_filters(dikt):
    permalink = ""
    for param in dikt:
        if param in "sortBy sortOrder columnOrder".split():
            #prevent sql injection
            assert ' ' not in dikt[param], ("Abort to prevent SQL injection in %s" % dikt[param])

            permalink = "%s%s=%s&" % (permalink, param, dikt[param])
    return permalink

def _textArea(task):
    id = task.id
    orig = task.text
    area = text_area('text_%d' % id, id = 'text_%d' % id, originalvalue=orig, 
                     content=orig, rows=5, cols=80)
    onclick = """changeField(%d, "text"); $("text-form_%d").hide(); $("text-label_%d").innerHTML = $("text_%d").value; 
                 $("text-label_%d").show(); return false;""" % (id, id, id, id, id)
    button = submit('submit', onclick = onclick)
    cancel = submit('cancel', onclick = "hideChangeableField(%d, 'text'); return false;" % id)
    return "%s %s %s" % (area, button, cancel)

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

    controller_name = controller

    module_name = 'tasktracker.controllers.%s' % controller_name
    __import__(module_name)
    module = sys.modules[module_name]

    cap_controller = controller_name[0].upper() + controller_name[1:]

    controller = getattr(module, cap_controller + 'Controller')

    if params.get('using_verb') == True:
        action_verb = action
    else:
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
    response = render(template)
    d = sqlobject_to_dict(obj)
    d.update(extra_dict)
    response = htmlfill.render(response, d, encoding='utf8')
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
    if cutoff == 0:
        cutoff = len(actions)
    rendered_actions = []

    count = 0
    for action in actions:
        if not isinstance(action, Comment) and 'Created' in action.getChangedFields():
            user = action.updatedBy
            result = "Created %s by %s" % (prettyDate(action.dateArchived), user)
        else:
            result = render_action(action)
            if not result:
                continue
        count += 1
        rendered_actions.append(result)
        if count >= cutoff:
            break

    if not rendered_actions:
        return ''
    head = "\n".join ("<li>%s<hr></li>\n" % action for action in rendered_actions[:-1])
    return "%s\n<li>%s</li>" % (head, rendered_actions[-1])

def render_action(action):
    if isinstance(action, Comment):
        comment = action.text
        user = action.user
        comment += "<br/>Comment from %s by %s" % (prettyDate(action.date), user)
    else:
        fields = action.getChangedFields()
        if not fields:
            return ''
        for field in ['Sort_Index', 'Parentid']:
            if field in fields:
                fields.remove(field)
        if not fields:
            return ''
        if "Num_Children" in fields:
            fields.remove("Num_Children")
        if 'Statusid' in fields:
            fields.remove('Statusid')
            fields.append('Status')
        if 'Text' in fields:
            fields.remove('Text')
            fields.append('Description')
        user = action.updatedBy
        comment = "%s updated %s by %s" % (", ".join (fields), prettyDate(action.dateArchived), user)
    return comment


def task_item_tr(task, is_preview, is_flat, editable_title):
    id = task.id
    statusName = task.statusName()
    if isinstance(statusName, unicode):
        statusName = statusName.encode('utf8')
    tr = ['<tr parentID="%s" id="task_%d" task_id="%d" status="%s" ' % (task.parentID, id, id, quote(statusName))]

    for prop in ['sort_index', 'owner', 'deadline', 'priority', 'updated']:
        value = getattr(task, prop)
        if not value and prop != 'sort_index':
            value = '' #handle null owner
        tr.append('%s = "%s" ' % (prop, quote(str(value))))

    tr.append('is_preview = "%s" ' % is_preview)
    tr.append('is_flat = "%s" ' % is_flat)
    tr.append('editable_title = "%s" ' % editable_title)
    if is_preview:
        tr.append("""onclick = "window.location.href = '%s'" """ % url_for(controller='task', action='show', id=id))
    tr.append('class = "taskrow task-item ')
    if has_permission('task', 'update', id=id):
        tr.append('deletable')
    else:
        tr.append('nondeletable')
    if task.status.done:
        tr.append(' completed-task')
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

    if count == 1:
        return word

    plural = special_plurals.get(word, None)
    if plural:
        return plural
        
    if word.endswith("x") or word.endswith("s") or word.endswith("ch") or word.endswith("sh"):
        return word + "es"
    else:
        return word + "s"

def taskListUpdated(taskList):
    updated = taskList.updated
    for task in taskList.tasks:
        if task.updated > updated:
            updated = task.updated

    return updated

def permalink_to_sql(permalink):
    terms = permalink.split("&")
    sql = []
    orderBy = None
    sortOrder = None
    for term in terms:
        if not term: continue
        key, val = term.split("=")
        if key == "deadline":
            now = datetime.date.today()
            if val == '-1':
                sql.append("deadline < '%s'" % now)
            elif val == '0':
                sql.append("deadline = '%s'" % now)
            elif val == '1':
                now += datetime.timedelta(days=1)
                sql.append("deadline = '%s'" % now)
            elif val == '0,7':
                then = now + datetime.timedelta(days=7)
                sql.append("deadline >= '%s' AND deadline < '%s'" % (now, then))
            elif val.lower() == 'none':
                sql.append("deadline is null")
            else: continue
        if key == "updated":
            now = datetime.date.today()
            if val == '0':
                sql.append("updated = '%s'" % now)
            elif val == '-1':
                then = now - datetime.timedelta(days=1)
                sql.append("updated >= '%s' AND updated < '%s'" % (now, then))
            elif val == '-0.7':
                then = now - datetime.timedelta(days=7)
                sql.append("updated >= '%s' AND updated < '%s'" % (now, then))
            else: continue
        elif key in "priority owner status".split():
            sql.append("%s='%s'" % (key, val))
        elif key == "sortOrder":
            if val == "up": sortOrder = "ASC"
            elif val == "down": sortOrder = "DESC"
        elif key == "sortBy":
            orderBy = val

    body = ""
    if len(sql):
        body = "AND %s" % " AND ".join(sql)
    return (body, orderBy, sortOrder)

def getColumnOrder(permalink):
    permalink = permalink.split("&")
    for part in permalink:
        if not part: continue
        lhs, rhs = part.split("=")
        if lhs == "columnOrder":
            return rhs.split(",")
    return list()

def _orderMovableColumns(columns, column_order):
    ret = str()
    for col in column_order:
        if col in columns:
            ret += columns[col]
            del columns[col]
    for col in columns:
        ret += columns[col]
    return ret

def generateMovableColumnFilters(column_order):
    columns = dict()
    if c.tasklist.hasFeature('deadlines'):
        columns['deadline'] = """<td class="deadline-column filter-line">%s</td>""" % columnFilter('deadline')
    columns['priority'] = """<td class="priority-column filter-line">%s</td>""" % columnFilter('priority')
    columns['owner'] = """<td class="owner-column filter-line">%s</td>""" % columnFilter('owner', c.tasklist)
    columns['updated'] = """<td class="updated-column filter-line">%s</td>""" % columnFilter('updated')
    return _orderMovableColumns(columns, column_order)

def generateMovableColumnHeaders(column_order):
    columns = dict()
    if c.tasklist.hasFeature("deadlines"):
        columns['deadline'] = sortableColumn("deadline")
    columns['priority'] = sortableColumn('priority')
    columns['owner'] = sortableColumn("owner", "assigned&nbsp;to")
    columns['updated'] = sortableColumn('updated', 'updated')
    return _orderMovableColumns(columns, column_order)
    
def generateMovableColumns(atask, is_preview, column_order):
    columns = dict()
    if atask.task_list.hasFeature('deadlines'):
        columns['deadline'] = \
            """<td class="deadline-column">
            <div class="first_line">
             %s
            </div>
            </td>""" % editableField(atask, 'deadline', uneditable = is_preview)

    columns['priority'] = \
        """
        <td class="priority-column">
         <div class="first_line">
          %s
         </div>
        </td>
        """ % editableField(atask, 'priority', uneditable = is_preview)

    columns['owner'] = \
        """
        <td class="owner-column">
         <div class="first_line">
          %s
         </div>
        </td>
        """ % editableField(atask, 'owner', uneditable = is_preview)

    columns['updated'] = \
        """
        <td class="updated-column">
         <div class="first_line">
          %s
         </div>
        </td>
        """ % readableDate(atask.updated).replace(" ", "&nbsp;")

    return _orderMovableColumns(columns, column_order)

def is_task_allowed(task, permalink):
    terms = permalink.split("&")
    for term in terms:
        if not term: continue
        key, val = term.split("=")
        if key == "deadline":
            now = datetime.date.today()
            if val == '-1':
                if task.deadline >= now:
                    return False
            elif val == '0':
                if task.deadline != now:
                    return False
            elif val == '1':
                now += datetime.timedelta(days=1)
                if task.deadline != now:
                    return False
            elif val == '0,7':
                then = now + datetime.timedelta(days=7)
                if task.deadline < now or task.deadline > then:
                    return False
            elif val.lower() == 'none':
                if task.deadline is not None:
                    return False
            else: continue
        if key == "updated":
            now = datetime.date.today()
            if val == '0':
                if task.updated != now:
                    return False
            elif val == '-1':
                then = now - datetime.timedelta(days=1)
                if task.updated <= now or task.update > then:
                    return False
            elif val == '-0.7':
                then = now - datetime.timedelta(days=7)
                if task.updated <= now or task.update > then:
                    return False
            else: continue
        elif key in "priority owner status".split():
            if getattr(task, key) != val:
                return False
        
    return True

def twirlip_link():
    try:
        twirlip_server = get_twirlip_uri(config)
        return '<a href="%s/watch/control" rel="include"></a>' % twirlip_server
    except KeyError:
        return ''
