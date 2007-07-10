<div id="permission_help">

<p>Task Tracker is designed to accommodate many different ways of getting things done. You can create task lists that match your particular needs by choosing the options that best work for you.</p>

<ul>

<li>If a set of tasks requires more direction, create a manger-directed list in which members can views tasks that have been assigned to them or <b>claim tasks</b> that have been left unassigned.</li>

<li>For a more collaborative project, allow members to <b>create new tasks</b> and <b>edit tasks</b>.</li>
</ul>

<p> The options further down the list add to or override those options further up. If you select to allow team members to edit any task, for instance, then they can also view this list, and claim tasks, and create new tasks. If you choose to allow non-members to create new tasks then they can also view this list and claim tasks.</p>

<p>The options are also designed to avoid incompatible choices. You cannot, for example, allow non-members to edit any tasks but restrict team members to only viewing the list.</p> 

</div>

<table><tbody><tr valign="top" padding="50px;">
<td>
<h2><% c.project.title %>'s project members can</h2>
<ul id="member_permissions"></ul>
</td>
<td width="20;">&nbsp;</td>

% if c.project_permission_level != "closed_policy":
<td>
<h2>Other users can</h2>
<ul id="other_permissions"></ul>
</td>
%

</tr></tbody></table>

<!-- these will be filled in by htmlfill, and then deleted by js -->

<input type="hidden" name="member_level" id="member_level_old" value="4">
<input type="hidden" name="other_level" id="other_level_old" value="0">

<script>
var options = ["not even see this list", "view this list", "and claim tasks", "and create new tasks", "and edit any task"];
var lists = ['member', 'other'];
checked = {};
lists.each(function(list_name) {
	var list = $(list_name + '_permissions');
	if( !list ) return;
	list.className = "undecorated_list";
	options.each(function(option, index) {
		var button = Builder.node('input', {
			id : list_name + '_level_' + index,
			name : list_name + '_level', 
			value : index, 
			type : "radio", 
			onclick : "permission_set(" + index + ", '" + list_name + "')"
		    });
                var label = Builder.node('label', {'for' : button.id}, option);
		var li = Builder.node('li', {id : list_name + '_item_' + index}, [button, label]);
		list.appendChild(li);
	    });
	//select the permission that was set on the server
	var old = $(list_name + '_level_old');
	$(list_name + '_level_' + old.value).checked = true;
	show_selected(list_name, old.value);
    });
lists.each(function(list_name) {
	/*    // move "not even see this list" to the bottom of the list in the next three lines.
        var m = $(list_name + '_item_0');
	if( !m ) return;
	m.parentNode.appendChild(m);*/
	old = $(list_name + '_level_old');
	permission_set(old.value, list_name);
    });

% if c.project_permission_level == "medium_policy":
for( var i = 2; i < options.length; ++ i ) {
  var m = $("other_item_" + i);
  if( !m ) continue;
  m.parentNode.removeChild(m);
}
%

function show_selected(list_name, index) {
    //also show what's selected
    var list = $(list_name + '_permissions');
    if( !list ) return;
    for (var i = 0; i < options.length; ++ i) {
	var radio = $(list_name + '_level_' + i);
	if( !radio ) continue;
	if( i <= index && (i == index || i > 0) ) {
	    removeClass(radio.parentNode, 'unselected-permission')
	    addClass(radio.parentNode, 'selected-permission');
	} else {
	    removeClass(radio.parentNode, 'selected-permission')
	    addClass(radio.parentNode, 'unselected-permission');
	}
    }
}

function permission_set(index, type) {
    //disable inappropriate options on 'anyone else'; enable appropriate ones
    var other = 'other';
    if( type == other ) other = 'member';

    var selected = null;
    for (var i = 0; i < options.length; ++ i) {
	var radio = $(other + '_level_' + i);
	if( !radio ) continue;
	if (radio.checked) {
	    selected = radio;
	}
	if( (other == 'other' && i > index) || (other == 'member' && i < index) ) {
	    radio.disabled = true;
	    addClass(radio.parentNode, "disabled-permission");
	} else {
	    radio.disabled = false;
	    removeClass(radio.parentNode, "disabled-permission");
	}
    }
    if( selected ) {
        if( (other == 'other' && selected.value > index) || (other == 'member' && selected.value < index) ) {
	    var radio = $(other + '_level_' + index);
	    if( radio ) radio.checked = true;
	}
    }

    show_selected(type, index);
}

function cull_old() {
  var old = $('member_level_old');
  if( old )
    old.parentNode.removeChild(old);
  old = $('other_level_old');
  if( old )
    old.parentNode.removeChild(old);
}

</script>
<hr/>