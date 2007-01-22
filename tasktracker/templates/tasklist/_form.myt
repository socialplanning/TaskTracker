
<label for="title">Name:</label><br/>
<% h.text_field('title', size=80) %><br/>

<label for="text">Description:</label><br/>
<% h.text_area('text', rows=10, cols=80) %><br/>
<br/>
<label for="managers">Managers:</label><br/>
<& _managers.myt &>

<br/>
<br/>

<!-- Permissions -->
<& _permissions.myt &>
<!-- Features -->

<br/>
Extra Features <% h.help('These are optional') %><br/>
<input type="checkbox" id="feature_deadlines" name="feature_deadlines" value="1" class="features"/>
<label for="feature_deadlines">Deadlines</label><br/>

<input type="checkbox" name="feature_custom_status" value="1" class="features" onclick="$('edit_statuses').toggle();" id="custom_status"/>
<label for="custom_status">Custom status</label><br/>

<div id="edit_statuses" style="display:none; margin-left: 3em;">
<% h.editable_list('statuses', [], ['done']) %>

   <input type="hidden" value="" id="statuses" name="statuses">
   <input id="add_status" name="add_status" size="20" type="text" value="" />
   <input type="submit" name="submit" value="Add" onclick="addItem('list_statuses', $('add_status').value);$('add_status').value=''; return false;"/>


</div>

<input type="checkbox" name="feature_private_tasks" id="feature_private_tasks" value="1" class="features"/>
<label for="feature_private_tasks">Private tasks</label><br/>

<br/>
By default, tasks are initially assigned to:<br/>
<input type="radio" name="initial_assign" value="0" checked="checked"/> The person who created them<br/>
<input type="radio" name="initial_assign" value="1"/> Unassigned <br/>

<% h.submit('Submit') %>
<input type="submit" name="Cancel" value="Cancel" onclick="document.location='/tasklist/index'; return false;" />

