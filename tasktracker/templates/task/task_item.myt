<%args>
atask
is_preview = False
no_second_row = False
is_flat = False
editable_title = False
</%args>

<%closure second_line>
% if not no_second_row:
 <div class="second-line"></div>
%
</%closure>

<% h.task_item_tr(atask, is_preview, no_second_row, is_flat, editable_title) %>

<td class="status-column 
% if atask.task_list.hasFeature('custom_status'): 
  custom-status 
%
">

<div class="first_line">
<% h.editableField(atask, 'status', uneditable = is_preview) %>
</div>
<& second_line &>
</td>

<td class="title-column">
<div class="first_line">
<span id="draggable_<% atask.id %>" depth="<% atask.depth() - c.depth %>" class="taskitem draggable">
% if not is_flat:
<% h.image_tag(h.test(atask.liveChildren(), 'plus.png', 'blank.png'),
   class_='treewidget handle',
   id='handle_%d' % atask.id,
   style='margin-left: %dpx;' % ((atask.depth() - c.depth) * 15)) %>
%
  <!-- title -->

% if editable_title:
  <span class = "task_item
% if atask.status == 'done':
  completed-task
% elif h.isOverdue(atask.deadline):
    overdue-task
% 

% if atask.parentID:
sub-task
% else:
root-task
%
">

<% h.editableField(atask, 'title', uneditable = is_preview) %>
</span>
% else:
  <a href = "<% h.url_for(controller='task', action='show', id=atask.id) %>"
     base_href = "<% h.url_for(controller='task', action='show', id=atask.id) %>"
     title = "<% atask.text %>"
     class = "task_item truncated uses_permalink 
% if atask.status == 'done':
    completed-task
% elif h.isOverdue(atask.deadline):
    overdue-task
% else:
    uncompleted-task
%

% if atask.parentID:
sub-task
% else:
root-task
%
% if is_preview:
preview-link
%
" id = "title_<% atask.id %>" ><% h.previewText(atask.title) %></a>
%
&nbsp;

% num_children = len(atask.uncompletedDescendents())
<span class="small"
% if not num_children: 
style="display:none"
%
> (<span class="num_subtasks"><% num_children %></span>
<span class="the-word-task">
% if num_children > 1:
tasks
% else:
task
%
</span>
left) </span>

% if atask.comments:
<span class="small"> <% len(atask.comments) %>
% if len(atask.comments) > 1:
comments
% else:
comment
%
</span>
%
% if atask.private:
-- (private)
%
</span>
</div>

% if not no_second_row:
 <div class="second-line">
  <span style = "clear:both; margin-left: <% (atask.depth() - c.depth) * 15 + 25 %>px;">
    <% h.previewText(atask.text, 75) %>
  </span></div>
%
</td>

% if atask.task_list.hasFeature('deadlines'):
<td class="deadline-column">
<div class="first_line">
<% h.editableField(atask, 'deadline', uneditable = is_preview) %>
</div>
<& second_line &>
</td>
%

<td class="priority-column">
<div class="first_line">
<% h.editableField(atask, 'priority', uneditable = is_preview) %>
</div>
<& second_line &>
</td>

<td class="owner-column">
<div class="first_line">
<% h.editableField(atask, 'owner', uneditable = is_preview) %>
</div>
<& second_line &>
</td>

<td class="updated-column">
<div class="first_line">
<% h.readableDate(atask.updated).replace(" ", "&nbsp;") %>
</div>
<& second_line &>
</td>

</tr>
