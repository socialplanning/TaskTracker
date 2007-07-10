<%args>
atask
is_preview = False
is_flat = False
editable_title = False
</%args>

<% h.task_item_tr(atask, is_preview, is_flat, editable_title) %>

<td class="status-column 
% if atask.task_list.hasFeature('custom_status'): 
  custom-status 
%
">

<% h.editableField(atask, 'status', uneditable = is_preview) %>
</td>

<td class="title-column">

<span id="draggable_<% atask.id %>" depth="<% atask.depth() - c.depth %>" class="taskitem draggable">
% if not is_flat:
<% h.image_tag(h.test(atask.liveChildren(), 'plus.png', 'blank.png'),
   class_='treewidget handle',
   id='handle_%d' % atask.id,
   style='margin-left: %.1fem;' % ((atask.depth() - c.depth) * 1.5)) %>
%
  <!-- title -->

% if editable_title:
  <span class = "task_item
% if atask.status.done:
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
     id = "title_<% atask.id %>"
     class = "task_item truncated uses_permalink 
% if atask.status.done:
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
"><% atask.title %></a>
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

</span>

</td>

<% h.generateMovableColumns(atask, is_preview, h.getColumnOrder(c.permalink)) %>

<td class="delete-task-column">
<% h.secure_link_to('delete', class_='post-link',
   confirm_msg='Are you sure you want to delete this task?',
   url=h.url_for(controller='task', action='destroy', id=atask.id)) %>
</td>

</tr>