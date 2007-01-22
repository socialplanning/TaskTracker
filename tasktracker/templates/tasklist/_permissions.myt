
<b><% c.project.title %>'s team members can:</b>
<ul id="member_permissions"></ul>
<b>Anyone else can:</b>
<ul id="other_permissions"></ul>

<!-- these will be filled in by htmlfill, and then deleted by js -->

<input type="hidden" name="member_level" id="member_level_old" value="0">
<input type="hidden" name="other_level" id="other_level_old" value="0">

<script>
var options = ["not even see this list", "view this list", "and claim tasks", "and create new tasks", "and edit any task"];
var lists = ['member', 'other'];
checked = {};
lists.each(function(list_name) {
	list = $(list_name + '_permissions');
	list.className = "undecorated_list";
	options.each (function(option, index) {
		var button = Builder.node('input', {
			id : list_name + '_level_' + index,
			name : list_name + '_level', 
			value : index, 
			type : "radio", 
			onclick : list_name + '_permission_set(' + index + ')'
		    });
                var label = Builder.node('label', {'for' : button.id}, option);
		var li = Builder.node('li', {id : list_name + '_item_' + index}, [button, label]);
		list.appendChild(li);
	    });
	//select the permission that was set on the server
	old = $(list_name + '_level_old');
	$(list_name + '_level_' + old.value).checked = true;
	show_selected(list_name, old.value);
    });

lists.each(function(list_name) {
	old = $(list_name + '_level_old');
	eval(list_name + '_permission_set')(old.value);
	old.parentNode.removeChild(old);
    });

function show_selected(list_name, index) {
    //also show what's selected
    for (var i = 0; i < options.length; ++ i) {
	var radio = $(list_name + '_level_' + i);
	if (i <= index && i > 0) {
	    removeClass(radio.parentNode, 'unselected-permission')
	    addClass(radio.parentNode, 'selected-permission');
	} else {
	    removeClass(radio.parentNode, 'selected-permission')
	    addClass(radio.parentNode, 'unselected-permission');
	}
    }
}

function member_permission_set(index) {
    //disable inappropriate options on 'anyone else'; enable appropriate ones
    other_selected = null;
    for (var i = 0; i < options.length; ++ i) {
	var radio = $('other_level_' + i);
	if (radio.checked) {
	    other_selected = radio;
	}
	if (i > index) {
	    radio.disabled = true;
	    addClass(radio.parentNode, "disabled-permission");
	} else {
	    radio.disabled = false;
	    removeClass(radio.parentNode, "disabled-permission");
	}
    }
    if (other_selected.value > index) {
	$('other_level_' + index).checked = true;
    }

    show_selected('member', index);
}
function other_permission_set(index) {
    //disable inappropriate options on 'member'; enable appropriate ones
    member_selected = null;
    for (var i = 0; i < options.length; ++ i) {
	var radio = $('member_level_' + i);
	if (radio.checked) {
	    member_selected = radio;
	}
	if (i < index) {
	    radio.disabled = true;
	    addClass(radio.parentNode, "disabled-permission");
	} else {
	    radio.disabled = false;
	    removeClass(radio.parentNode, "disabled-permission");
	}
    }
    if (member_selected.value < index) {
	$('member_level_' + index).checked = true;
    }

    show_selected('other', index);
}


</script>
