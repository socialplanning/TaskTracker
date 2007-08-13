<div id="title">
 <label for="title">Name</label>
<% h.text_field('title', size=80) %>
</div>

<div id="text">
 <label for="text">Description</label>
<% h.text_area('text', rows=10, cols=80) %><br/>
</div>

<div id="managers-section">
 <h2><label for="managers">Task list managers</label></h2>
 <p>Task list managers can perform all task list functions, set permissions for others, add and remove features, and delete the list.</p>
 <p>In addition to the team members added below, all project administrators also have these privileges. Project administrators are labelled on the project's team page.</p>
<& _managers.myt &>
</div>

<div id="permissions_section">
<!-- Permissions -->
<& _permissions.myt &>
</div>

<!-- Features -->

<div id="features-section">
 <h2>Extra Features</h2>

 <div id="deadlines">
  <input type="checkbox" id="feature_deadlines"
         name="feature_deadlines" value="1" class="features"/>
  <label for="feature_deadlines">Specify deadlines</label>
 </div>

 <div id="initial_assign">
  By default, tasks are initially assigned to
  <input type="radio" name="initial_assign" value="0" checked="checked"/>
The person who created them
  <input type="radio" name="initial_assign" value="1"/>
Unassigned
 </div>

 <div id="custom_statuses">
  <input type="checkbox" name="feature_custom_status"
   value="1" class="features"
   onclick="$('edit_statuses').toggle();" id="custom_status"/>
  <label for="custom_status">Allow custom status</label>

  <div id="edit_statuses" style="display:none; margin-left: 3em;">
   <% h.editable_list('statuses', [], ['done']) %>
   <input type="hidden" value="" id="statuses" name="statuses">
   <input id="add_status" name="add_status" size="20" type="text" value="" />
   <input type="submit" name="submit" value="Add"
          onclick="addItem('list_statuses', $('add_status').value);$('add_status').value='';$('add_status').focus();return false;"/>
   <input type="submit" name="submit" value="Cancel"
          onclick="$('edit_statuses').hide(); $('custom_status').checked=false; return false;"/>
  </div>
 </div>
</div>

<% h.submit('Save changes', onclick='cull_old();') %>
<% h.submit('Cancel', onclick='window.location.href="%s"; return false;' % h.url_for(controller='tasklist')) %>
