
<label for="title"><b>Name:</b></label><br/>
<% h.text_field('title', size=80) %><br/>

<label for="text"><b>Description:</b></label><br/>
<% h.text_area('text', rows=10, cols=80) %><br/>
<br/>
<label for="managers"><b>Managers:</b></label><br/>
<& _managers.myt &>

<br/>
<br/>

<!-- Permissions -->
<& _permissions.myt &>
<!-- Features -->

<br/>
<label><b>Extra Features:</b></label><br/>
<input type="checkbox" id="feature_deadlines" name="feature_deadlines" value="1" class="features"/>
<label for="feature_deadlines">Specify deadlines</label><br/>

<input type="checkbox" name="feature_custom_status" value="1" class="features" onclick="$('edit_statuses').toggle();" id="custom_status"/>
<label for="custom_status">Allow custom status</label><br/>

<div id="edit_statuses" style="display:none; margin-left: 3em;">
   <% h.editable_list('statuses', [], ['done']) %>
   <input type="hidden" value="" id="statuses" name="statuses">
   <input id="add_status" name="add_status" size="20" type="text" value="" />
   <input type="submit" name="submit" value="Add" onclick="addItem('list_statuses', $('add_status').value);$('add_status').value=''; return false;"/>
   <input type="submit" name="submit" value="Cancel" onclick="$('edit_statuses').hide(); $('custom_status').checked=false; return false;"/>
   <br/><br/>
</div>

<input type="checkbox" name="feature_private_tasks" id="feature_private_tasks" value="1" class="features"/>
<label for="feature_private_tasks">Authorize private tasks on this list</label><br/>

<br/>
<b>By default, tasks are initially assigned to:</b><br/>
<input type="radio" name="initial_assign" value="0" checked="checked"/> The person who created them<br/>
<input type="radio" name="initial_assign" value="1"/> Unassigned <br/><br/>

<% h.submit('Submit', onclick='cull_old();') %>
<input type="submit" name="Cancel" value="Cancel" onclick="window.location.href='/tasklist/index'; return false;" />

