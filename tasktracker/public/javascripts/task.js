function changeStatus(url, task_id) {
    url += "?status=" + $('status_' + task_id).value

    new Ajax.Request(url, {asynchronous:true, evalScripts:true}); 
    moveTask(task_id);

}

function oppositeStatus(status) {
    if (status == "completed") {
	return "uncompleted";
    } else {
	return "completed";
    }
}

function getParentList(task_id) {
    var parent = $('task_' + task_id);
    while (parent.nodeName != "UL") {
	parent = parent.parentNode;
    }
    return parent;
}

function moveTask(task_id) {
    var task_name = 'task_' + task_id;

    var parent = getParentList(task_id);
    $('toggle_' + task_id).enable();   /// huh???

    new Effect.Fade($(task_name)); 
    window.setTimeout(function () {
	    Effect.Appear(task_name, {duration: 0.3});
	}, 1000);

    var target = oppositeStatus(parent.getAttribute('id'));
    
    window.setTimeout(function () {
	    appear(target, task_id);
	}, 1000);
}

function appear(target, task_id) {
    $(target).appendChild($('task_' + task_id));
    $(target + '_section').show();
    var source = oppositeStatus(target);
     if($(source).getElementsByTagName('LI').length == 0)
	$(source + '_section').hide();

     if($('uncompleted').getElementsByTagName('LI').length < 2) {
	$('reorder_button').hide();
     } else {
	$('reorder_button').show();
     }

    $('toggle_' + task_id).setAttribute('checked', 
					getParentList(task_id).getAttribute('id') == 'completed');
    $('toggle_' + task_id).disable();   /// huh????
    
}

var mode = 'toggle';

function hideCreate() {
    $('create').show();
    $('show_create').hide();
    $('create_anchor').scrollTo();
    return false;
}

function modeSwitch() {
    var lists = $A(['completed', 'uncompleted']);
    lists.each(function(list) {
	    $A($(list).getElementsByTagName('span')).each(function(node) {
		    if (node.id.match('^(button|handle)')) {
			node.toggle();
		    }
		});
	});

    $('completed_section').toggle();
    
    Sortable.create("uncompleted", 
		    {tag:'li',
		     handle:'handle', 
		     onUpdate:function () {
			    new Ajax.Request($('order').getAttribute('url'), 
					     {asynchronous:true, 
					      evalScripts:true, 
					      parameters:Sortable.serialize("uncompleted")
						     });
			}
		    });

    if (mode == 'toggle') {
	mode = 'reorder';
	$('modeName').innerHTML = 'Done reordering';
	$('create_section').hide();
    } else {
	mode = 'toggle';
	$('modeName').innerHTML = 'Reorder';
	$('create_section').show();
    }
}