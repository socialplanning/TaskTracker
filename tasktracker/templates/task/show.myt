<hr/><br/>
<span class="small">
<% h.link_to("&lt;&lt; return to tasklist", h.url_for(controller='tasklist', action='show', id=c.task.task_list.id), base_href=h.url_for(controller='tasklist', action='show', id=c.task.task_list.id), id="return_to_tasklist", class_="uses_permalink") %>
&nbsp;
<% h.link_to("&lt;&lt; return to list of lists", h.url_for(controller='tasklist', action='index')) %>
&nbsp;
<a id="permalink" permalink="<% c.permalink %>" base="" href="<% h.url_for(controller='tasklist', action='show') %>">permalink this view</a>
</span><br/>

<& task_list_title.myt &>

<span id="global-values" style="display:none" depth="<% c.depth %>"></span>

<div id="wrap-task-details">

<!-- The current task -->
<table class="task_list" width="100%">
<& task_item_row.myt, atask = c.task, is_preview = False, is_flat = True, editable_title = True &>
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

   <b>Previous activity:</b>
  </td>
  <td>&nbsp;</td>
 </tr>
 <tr>
  <td class="small task-detail-mainbar">
   <ul id="activity_<% c.task.id %>" class="activity_list">
    <%  h.render_actions(c.task.actions(), 0) %>
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
     complete="if( request.responseText.length ) change_description_updated(%s, 'comment', request.responseText); $('enter_comment_here').value = ''; $('edit_comment').hide(); $('comment').show();" % c.task.id) %>
  <label for="text">Comment:<label><br/>
  <textarea name="text" id="enter_comment_here" cols=80 rows=5></textarea><br/>
  <% h.submit("comment", onclick="if( $('enter_comment_here').value.length < 1 ) { cancel_comment(); return false; }") %>
  <% h.submit("cancel", onclick="cancel_comment(); return false;") %>
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
<% h.secure_link_to('delete this task', class_='post-link',
   confirm_msg='Are you sure you want to delete this task', url=h.url_for(controller='task', action='destroy', id=c.task.id)) %>
%
%

<br/><br/>

This task
% if c.task.parentID:
is part of the
  <a href = "<% h.url_for(controller='task', action='show', id=c.task.parent.id) %>"
     base_href = "<% h.url_for(controller='task', action='show', id=c.task.parent.id) %>"
     title = "<% h.quote(c.task.parent.text) %>"
     id = "title_<% c.task.parent.id %>"
     class = "uses_permalink">
   <% c.task.parent.title %> task</a>.
% #endif
<span
% if not len(c.task.liveChildren()):
style = "display:none;"
%
class="unfolded" id="subtasks">This task has
<a href="#nevermind" class="command" onclick="$('subtasks').hide(); $('edit_subtasks').show(); return false;"> 
<span class="num_subtasks"> <% len(c.task.liveDescendents()) %> </span> sub-tasks.
</a><br/>
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

<table id="next-prev-tasks"><tbody>
<tr>
<td>
% if c.prev:
<< previous task: 
  <a href = "<% h.url_for(controller='task', action='show', id=c.prev.id) %>"
     base_href = "<% h.url_for(controller='task', action='show', id=c.prev.id) %>"
     title = "<% h.quote(c.prev.text) %>"
     id = "title_<% c.prev.id %>"
     class = "uses_permalink big">
   <% c.prev.title %></a>
% #endif
</td>
<td align="right">
% if c.next:
next task:
  <a href = "<% h.url_for(controller='task', action='show', id=c.next.id) %>"
     base_href = "<% h.url_for(controller='task', action='show', id=c.next.id) %>"
     title = "<% h.quote(c.next.text) %>"
     id = "title_<% c.next.id %>"
     class = "uses_permalink big">
   <% c.next.title %></a> >>
% #endif
</td>
</tbody></table>

<& task_list_footer.myt, pre_footer = h.link_to('Go back to the task list', h.url_for(action='show', controller='tasklist', id=c.task.task_listID)) + ' | ' &>

<span id="post_add_task" func="count_subtasks"></span>

<span id="post_edit_task" func="change_description_updated"></span>

<script>
function cancel_comment() {
   $('enter_comment_here').value = '';
   $('edit_comment').hide();
   $('comment').show();
}

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
        var b = Builder.node('b', field_name + " from Today by <% c.username %>");
	var span = Builder.node('span');
	span.innerHTML = comment_text;
	var li = Builder.node('li', {}, [span, Builder.node('br'), b, Builder.node('hr')]);
      } else {
        var b = Builder.node('b', field_name + " updated Today by <% c.username %>");
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
