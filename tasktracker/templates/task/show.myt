<hr/><br/>
<span class="small">
<% h.link_to("&lt;&lt; return to tasklist", h.url_for(controller='tasklist', action='show', id=c.task.task_list.id)) %>

<% h.link_to("&lt;&lt; return to list of lists", h.url_for(controller='tasklist', action='index')) %>
</span><br/>

<& task_list_title.myt &>

<span id="global-values" style="display:none" depth="<% c.depth %>"></span>

<br/><br/>

<!-- The previous task -->

% if c.task.previousTask():
<table class="task_list preview" width="100%">
<& task_item.myt, atask = c.task.previousTask(), no_second_row = True, is_preview = True, is_flat = True &>
</table>
%
<div id="wrap-task-details">

<!-- The current task -->
<table class="task_list" width="100%">
<& task_item.myt, atask = c.task, no_second_row = True, is_preview = False, is_flat = True, editable_title = True &>
</table>

<table id="activity-table">
 <tr>
  <td class="small task-detail-mainbar">

<% h.editableField(c.task, 'text', 'Add a description') %>
   <br/>
   <span id="description_updated_<% c.task.id %>">
% if h.field_last_updated(c.task, 'text'):
      Description last updated 
   <% h.field_last_updated(c.task, 'text') %>
%
   </span>
   <hr/>

   <b>Latest activity:</b>
  </td>
  <td>&nbsp;</td>
 </tr>
 <tr>
  <td class="small task-detail-mainbar">
   <ul id="activity_<% c.task.id %>" class="activity_list">
    <%  h.render_actions(c.task.actions()) %>
   </ul>
  </td>
  <td id="task-detail-sidebar-cell">
   <div id="task-detail-sidebar" class="small">
    Task created by <% c.task.creator %>
 <% h.prettyDate(c.task.created) %>
   </div>
  </td>
 </tr>

 <tr>
  <td class="task-detail-mainbar">
   <hr/>
  </td>
 </tr>
</table>


% if h.has_permission(controller='task', action='comment', id=c.task.id):
<span id="comment" class="unfolded"><span class="command">add comment</span>&nbsp;</span>
<div id="edit_comment" class="folded">
 <% h.secure_form_remote_tag(html=dict(id="add_comment_form"), url=h.url_for(action='comment', task_id=c.task.id),
     complete="change_description_updated(%s, 'comment', request.responseText); $('enter_comment_here').value = ''; $('edit_comment').hide(); $('comment').show();" % c.task.id) %>
  <label for="text">Comment:<label><br/>
  <textarea name="text" id="enter_comment_here" cols=80 rows=5></textarea><br/>
  <% h.submit("comment") %>
  <% h.submit("cancel", onclick="$('edit_comment').hide(); $('comment').show(); return false;") %>
 </form>
</div>
% 

% if c.task.task_list.hasFeature("private_tasks"):
|
% if h.has_permission(controller='task', action='update_private', id=c.task.id):
<span id="private">
<& _private.myt &>
</span>
%
% if h.has_permission(controller='task', action='update', id=c.task.id):
<% h.secure_link_to('delete this task',
   confirm='Are you sure you want to delete this task', url=h.url_for(controller='task', action='destroy', id=c.task.id)) %>
%
%

<br/><br/>

<span 
% if not len(c.task.liveChildren()):
style = "display:none;"
%
class="unfolded" id="subtasks">
 This task has <span class="num_subtasks"> <% len(c.task.liveDescendents()) %> </span> sub-tasks.
 <span class="command" onclick="$('subtasks').hide(); $('edit_subtasks').show();">View them.</span><br/>
</span>

<span class="folded" id="edit_subtasks">
 <span class="command" onclick="$('edit_subtasks').hide(); $('subtasks').show();">
  hide sub-tasks
 </span>

 <div class="child_tasks">
 <table width="100%" id="tasks" class="all_tasks" hasReorderableTasks="True">
% for atask in c.task.liveChildren():
<& task_list_item.myt, atask=atask &>
%
 </table>
 </div>

 <br/>
 <hr/>
</span>

</div>

<& _hideable_show_create.myt, subtask_link = '[ + ]<a href="%s" onclick="showTaskCreate();return false;">add a sub-task</a>' % h.url_for(action='show_create', controller='task', task_listID=c.tasklist.id, parentID=c.task.id), parentID = '<input type="hidden" name="parentID" value ="%s"' %  c.task.id  &>

<br/>

<!-- The next task -->

% if c.task.nextTask():
<table class="task_list preview" width="100%">
  <& task_item.myt, atask = c.task.nextTask(), no_second_row = True, is_preview = True, is_flat = True &>
</table>
%

<& task_list_footer.myt, pre_footer = h.link_to('Go back to the task list', h.url_for(action='show', controller='tasklist', id=c.task.task_listID)) + ' | ' &>

<span id="post_add_task" func="count_subtasks"></span>

<span id="post_edit_task" func="change_description_updated"></span>

<script>
function change_description_updated(task_id, field_name, comment_text) {
    var desc = $('description_updated_' + task_id);
    if( desc ) {
      if( field_name == 'text' ) {
        desc.innerHTML = "Description last updated Today by you";
	field_name = 'description';
      }
    }
    var act = $('activity_' + task_id);
    if( act ) {
      field_name = field_name[0].toUpperCase() + field_name.substr(1);
      if( field_name == 'Comment' ) {
        var b = Builder.node('b', field_name + " from Today by you");
	var span = Builder.node('span');
	span.innerHTML = comment_text;
	var li = Builder.node('li', {}, [span, Builder.node('br'), b, Builder.node('hr')]);
      } else {
        var b = Builder.node('b', field_name + " updated Today by you");
	var li = Builder.node('li', {}, [b, Builder.node('hr')]);
      }
      act.insertBefore(li, act.childNodes[0]);
    }
}

function count_subtasks() {

with_items ("num_subtasks", function(node) { node.innerHTML = parseInt(node.innerHTML) + 1;; }, document.childNodes[0]); 

$('subtasks').show();

}
</script>
