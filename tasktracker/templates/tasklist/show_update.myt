<!-- Please also see show_preferences for the non-editable version -->

<% h.secure_form(h.url(action='update'), method='post') %>

<div id="title" class="editable unfolded">
<h1> <% c.tasklist.title %></h1>
</div>
<div id="edit_title" class="folded">
<% h.text_field('title') %><br/>
</div>

<div id="text" class="editable unfolded">
<span>
% if c.tasklist.text:
<% c.tasklist.text %>
% else:
[no description]
%
</span>
</div>
<div id="edit_text" class="folded">
<% h.text_area('text', rows=10, cols=80) %><br/>
</div>

<br/>


<label for="managers"><b>Managers:</b></label><br/>
<div id="managers_div" class="unfolded editable">
<ul>
% for manager in c.managers + c.administrators:
     <li> <% manager %> </li>
%
</ul>
</div>
<div id="edit_managers_div" class="folded">

<& _managers.myt &>
</div>

<br/>
<br/>

<!-- Permissions -->
<span onclick="show_permissions();" class="editable" id="permissions_section">
<& _permissions.myt &>
</span>
<script>
function show_permissions() {
  lists.each(function(list_name) {
      for (var i = 0; i < 5; i ++) {  
        var item = $(list_name + '_item_' + i);
        var button = $(list_name + '_level_' + i);
	item.show();
        button.show();
      }
  });
  removeClass($('permissions_section'), 'editable');
  $('permissions_section').title = null;
}

// on startup for show_update, hide radio buttons
// and hide all options that are not true.
lists.each(function(list_name) {
    for( var i = 0; i < 5; ++i ) {
      var old = parseInt( $(list_name + '_level_old').value );
      if( i > old || ( !i && old ) ) {
        var item = $(list_name + '_item_' + i);
	item.hide();
      }
      var button = $(list_name + '_level_' + i);
      button.hide();
    }
  });
</script>


<!-- Features -->

<br/>
<b>Extra Features:</b><br/>


<div id="deadlines" class="editable unfolded">
% if c.feature_deadlines:
    Tasks have deadlines
% else:
    Tasks do not have deadlines
%
  <br/>
</div>
<div id="edit_deadlines" class="folded">
  <input type="checkbox" name="feature_deadlines" value="1" class="features"/>Deadlines<br/>
</div>


% if c.feature_custom_status:
This list has custom task statuses.  The statuses are: <% ', '.join([s.name for s in c.tasklist.statuses]) %>
% else:
Tasks do not have custom statuses. 
%
<br/>

<div id="edit_private" class="folded">
<input type="checkbox" name="feature_private_tasks" value="1" class="features" id="feature_private_tasks"/>Private tasks<br/>
</div>

<div id="private" class="editable unfolded">
% if c.feature_private_tasks:
This list has private tasks.
<script>
$('feature_private_tasks').onclick=function() {return confirm('All private tasks will be made public.  Proceed?')};
</script>
% else:
This list does not have private tasks.
%
<br/>
</div>

<br/>

<div id="initial_assign" class="unfolded editable">
    By default, tasks are initially
% if c.tasklist.initial_assign:
      unassigned 
% else:
      assigned to the person who created them
%
</div>
<div id="edit_initial_assign" class="folded">
  By default, tasks are initially assigned to:<br/>
  <input type="radio" name="initial_assign" value="0" checked="checked"/> The person who created them<br/>
  <input type="radio" name="initial_assign" value="1"/> Unassigned <br/>
</div>
<br/>

<% h.submit('Submit', onclick='cull_old();') %>
<input type="submit" name="Cancel" value="Cancel" onclick="document.location='/tasklist/index';"/>

<script language="JavaScript">

   with_items ("editable", function(node) { node.title="Click to change this."; }, document.childNodes[0]);
   
</script>

</form>
