<!-- Please also see show_update for the editable version -->

<h1> <% c.tasklist.title %></h1>

<span>
% if c.tasklist.text:
<% c.tasklist.text %>
%
</span>

<br/>

Managers:<br/>

<ul>
% for manager in c.administrators + c.managers:
     <li> <% manager %> </li>
%
</ul>


<!-- Permissions -->
<& _permissions.myt &>
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

<br/>
Extra Features:<br/>
% if c.feature_deadlines:
    Tasks have deadlines
% else:
    Tasks do not have deadlines
%
<br/>

% if c.feature_custom_status:
This list has custom task statuses.  The statuses are: <% ', '.join([s.name for s in c.tasklist.statuses]) %>
% else:
Tasks do not have custom statuses. 
%
<br/>

% if c.feature_private_tasks:
This list has private tasks.
% else:
This list does not have private tasks.
%
<br/>


<br/>
By default, tasks are initially
    By default, tasks are initially
% if c.tasklist.initial_assign:
      unassigned 
% else:
      assigned to the person who created them
%
