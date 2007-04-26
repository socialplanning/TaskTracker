<span class="small">

 <a href="<% h.url_for(controller='tasklist', action='index') %>">
    my tasklists
 </a>
 &nbsp;&gt;&gt;

 <a id="permalink" permalink="<% c.permalink %>" base="<% h.url_for(controller='tasklist', action='show') %>"
                   href="<% h.url_for(controller='tasklist', action='show') + '?' + c.permalink %>">
   <% c.tasklist.title %>
 </a>

</span>

<br/>

<& task_list_title.myt &>

<span id="global-values"
     depth="0"
     move_url="<% h.url_for(controller='task', action='move', id='') %>" 
     change_url="<% h.url_for(controller='task', action='change_field', id='') %>" >
</span>
<!-- list headers -->

<table id="tasks" class="task_list" hasReorderableTasks="True">

 <& task_list_header.myt &>

<!-- the actual task list -->

% for atask in c.tasks:  
 <& task_list_item.myt, atask=atask &>
%

% if not c.tasks:
 <tr id="no_tasks_placeholder">
  <td colspan=6>
   There are no tasks on this list yet.
  </td>
 </tr>
%

</table>

<br clear="both" />

<!-- the garbage bin -->
<!-- is currently hidden
<span tal:replace="structure python: h.image_tag('trash.png', id='trash')" />
-->

<!-- the create setup -->

<div id="add_task_anchor">
 <div class="draggable" id="movable_add_task" parentID="0" siblingID="0" >
  <div class="handle">

% subtask_link = """<div>[ + ]<a id="add_a_task" href = %s onclick="return false;">add a task</a> </div>""" % h.url_for(action='show_create', controller='task', task_listID=c.tasklist.id)
   <& _hideable_show_create.myt, subtask_link=subtask_link &>

  </div>
 </div>
</div>

<hr/>

<span class="small">
% if h.has_permission('task', 'create', task_listID=c.tasklist.id):
 <a href="#nevermind" onclick="restoreAddTask(); return false;">add a task</a>
%
 &nbsp;

 <% h.link_to('view list preferences', h.url_for(action='show_update', controller='tasklist', id=c.tasklist.id)) %> 
% if h.has_permission('tasklist', 'destroy', id=c.tasklist.id):
 &nbsp;
 <% h.secure_link_to('delete this list', h.url_for(action='destroy', controller='tasklist', id=c.tasklist.id),
    class_='post-link', confirm_msg='Are you sure you want to delete this tasklist?') %>
% #endif

</span>
