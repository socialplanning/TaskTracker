function oppositeStatus(status) {
    if (status == "completed") {
	return "uncompleted";
    } else {
	return "completed";
    }
}

function moveTask (task_id) {
    task_name = 'task_' + task_id;
    var task = $(task_name);

    parent = task;
    while (parent.nodeName != "UL") {
	parent = parent.parentNode;
    }

    $('toggle_' + task_id).enable();

    new Effect.Fade(task); 
    window.setTimeout('Effect.Appear("' + task_name + '", {duration:.3})', 1000);

    var target = oppositeStatus(parent.getAttribute('id'));
    window.setTimeout('appear("' + target + '", ' + '"' + task_id + '")', 1000);
}

function appear(target, task_id) {
    $(target).appendChild($('task_' + task_id));
    $('toggle_' + task_id).disable();
}

function toggleButtons() {
    var lists = $A(['completed', 'uncompleted']);
    lists.each(function(list) {
	    $A($(list).getElementsByTagName('span')).each(function(node) {
		    if (node.id.match('^(button|handle)')) {
			node.toggle();
		    }
		})
	});
}


var mode = 'toggle';

function hideCreate() {
    $('create').show();
    $('show_create').hide();
    $('create_anchor').scrollTo()
    return false;
}

function modeSwitch() {
    toggleButtons();

    $('completed_section').toggle();
    
    Sortable.create("uncompleted", {tag:'li',handle:'handle', onUpdate:function(){new Ajax.Request($('order').getAttribute('url'), {asynchronous:true, evalScripts:true, parameters:Sortable.serialize("uncompleted")})}})

    if (mode == 'toggle') {
	mode = 'reorder';
	$('modeName').innerHTML = 'Done reordering';
    } else {
	mode = 'toggle';
	$('modeName').innerHTML = 'Reorder';
    }
}