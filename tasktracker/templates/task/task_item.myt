<%args>
atask
is_preview = False
is_flat = False
editable_title = False
</%args>


<& task_item_row.myt, atask = atask, is_preview = is_preview, is_flat = is_flat, editable_title=editable_title &>

</tr>

<tr id="second_line_<% atask.id %>" class="second-line">
<td colspan="7">
 <span style = "clear:both; margin-left: <% (atask.depth() - c.depth) * 15 + 25 %>px;">
   <% h.previewText(atask.text, 400) %><br/>
   <ul class="activity_list">
   <% h.render_actions(atask.actions(), 1) %><br/>
   </ul>
   <ul class="command_list">
   <li><% h.link_to('View all activity', controller='task', action='show', id=atask.id) %> </li>
   <li><% h.link_to('Add a comment', controller='task', action='show', id=atask.id) %> </li>
% if h.has_permission(controller='task', action='update', id=atask.id):
   <li><% h.secure_link_to('Delete this task', class_='post-link',
   confirm_msg='Are you sure you want to delete this task', url=h.url_for(controller='task', action='destroy', id=atask.id)) %></li>
</ul>
%
</span>
</td>
</tr>