<!-- Please also see show_update for the editable version -->

<span class="small">
 <a href="<% h.url_for(controller='tasklist', action='index') %>">
    all lists</a
 >&nbsp;&raquo;
 <a id="permalink" permalink="<% c.permalink %>" base="<% h.url_for(controller='tasklist', action='show') %>"
                   href="<% h.url_for(controller='tasklist', action='show') + '?' + c.permalink %>">
   <% c.tasklist.title %></a
 ></span>

<div id="title">
<h1> <% c.tasklist.title %></h1>
</div>

<div id="text">
<span>
% if c.tasklist.text:
<% c.tasklist.text %>
%
</span>
</div>

<div id="managers-section">
 <h2>Managers</h2>

 <div id="managers_div">
  <ul>
% for manager in c.administrators + c.managers:
   <li> <% manager %> </li>
%
  </ul>
 </div>
</div>

<!-- Permissions -->
<div id="permissions_section">
<& _permissions.myt &>
</div>

<script>
lists.each(function(list_name) {
for (var i = 0; i < 5; i ++) {
  button = $(list_name + '_level_' + i);
  button.hide();
  button.disabled = true;
}
});

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

<div id="features-section">
 <h2>Extra Features</h2>

 <div id="deadlines">
% if c.feature_deadlines:
    Tasks have deadlines
% else:
    Tasks do not have deadlines
%
 </div>

 <div id="initial_assign">
By default, tasks are initially
% if c.tasklist.initial_assign:
      unassigned 
% else:
      assigned to the person who created them
%
 </div>

 <div id="custom_statuses">
% if c.feature_custom_status:
This list has custom task statuses.  The statuses are: <% ', '.join([s.name for s in c.tasklist.statuses]) %>
% else:
Tasks do not have custom statuses. 
%
 </div>