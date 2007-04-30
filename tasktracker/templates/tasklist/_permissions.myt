
<table><tbody><tr valign="top" padding="50px;">
<td>
<h2><% c.project.title %>'s team members can</h2>
<ul id="member_permissions"></ul>
</td>
<td width="20;">&nbsp;</td>
<td>
<h2>Anyone else can</h2>
<ul id="other_permissions"></ul>
</td>
</tr></tbody></table>

<!-- these will be filled in by htmlfill, and then deleted by js -->

<input type="hidden" name="member_level" id="member_level_old" value="0">
<input type="hidden" name="other_level" id="other_level_old" value="0">

<script>
var options = ["not even see this list", "view this list", "and claim tasks", "and create new tasks", "and edit any task"];
var lists = ['member', 'other'];
checked = {};
lists.each(function(list_name) {
	var list = $(list_name + '_permissions');
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
        // move "not even see this list" to the bottom of the list in the next three lines.
        var m = $(list_name + '_item_0');
	m.parentNode.appendChild(m);
	old = $(list_name + '_level_old');
	permission_set(old.value, list_name);
    });

function show_selected(list_name, index) {
    //also show what's selected
    for (var i = 0; i < options.length; ++ i) {
	var radio = $(list_name + '_level_' + i);
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
    if( (other == 'other' && selected.value > index) || (other == 'member' && selected.value < index) ) {
	$(other + '_level_' + index).checked = true;
    }

    show_selected(type, index);
}

function cull_old() {
  var old = $('member_level_old');
  old.parentNode.removeChild(old);
  old = $('other_level_old');
  old.parentNode.removeChild(old);
}

</script>
