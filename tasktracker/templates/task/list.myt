<span class="small">
<hr/><br/>
<a href="<% h.url_for(controller='tasklist', action='index') %>">
&lt;&lt; return to list of lists</a>&nbsp;
<a id="permalink" permalink="<% c.permalink %>" base="" href="">permalink this view</a>
</span><br/>

<& task_list_title.myt &>

<!-- list headers -->

<table id="tasks" class="task_list" hasReorderableTasks="True">
<& task_list_header.myt &>

<!-- the actual task list -->

% for atask in c.tasks:  
<& task_list_item.myt, atask=atask &>
%

</table>

<br clear="both" />
<!-- the garbage bin -->
<!-- is currently hidden
<span tal:replace="structure python: h.image_tag('/images/trash.png', id='trash')" />
-->

<!-- the create setup -->

<div id="add_task_anchor">
<div class="draggable" id="movable_add_task" parentID="0" siblingID="0" style="padding:0px;  margin:0px; line-height: 1em;">
<span class="handle">

% subtask_link = """<div>[ + ]<a id="add_a_task" href = %s onclick="return false;">add a task</a> </div>""" % h.url_for(action='show_create', controller='task', task_listID=c.tasklist.id)
<& _hideable_show_create.myt, subtask_link=subtask_link &>

</span>
</div></div>

<!-- ----------------------------- -->
<hr/>

<span class="small">
% if h.has_permission('task', 'create', task_listID=c.tasklist.id):
<a href="#nevermind" onclick="restoreAddTask(); return false;">add a task</a>
%
&nbsp;
<!--
% if not c.tasklist.isWatchedBy(c.username):
<% h.link_to('watch this list', url=h.url_for(action='show_create', controller='watcher', targetID=c.tasklist.id, type='tasklist')) %>
% else:
<% h.link_to('edit watch settings', url=h.url_for(action='show_update', controller='watcher', id=c.tasklist.getWatcher(c.username).id)) %>
%
&nbsp;
-->
<% h.link_to('view list preferences', h.url_for(action='show_update', controller='tasklist', id=c.tasklist.id)) %> 
&nbsp;
<% h.secure_link_to('delete this list', h.url_for(action='destroy', controller='tasklist', id=c.tasklist.id)) %>

</span>