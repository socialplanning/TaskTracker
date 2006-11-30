// http://trac.mochikit.com/wiki/ParsingHtml
function evalHTML(value) {
    if (typeof(value) != 'string') {
	return null;
    }
    value = MochiKit.Format.strip(value);
    if (value.length == 0) {
	return null;
    }
    var parser = MochiKit.DOM.DIV();
    var html = MochiKit.DOM.currentDocument().createDocumentFragment();
    
    var child;
    parser.innerHTML = value;
    while ((child = parser.firstChild)) {
	html.appendChild(child);
    }
    return html;
}


// http://simon.incutio.com/archive/2004/05/26/addLoadEvent
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}

function hasReorderableTasks() {
    return ($('tasks') && $('tasks').getAttribute("hasReorderableTasks") == "True");
}

function createDragDrop() {
    if (!initialized && hasReorderableTasks()) {
        initialized = true;
        Draggables.addObserver(new observer());

        $A($('tasks').getElementsByTagName('li')).each(function(node) {
            var id = node.getAttribute('task_id');
            var drag = new Draggable(node.id, {
                handle : 'handle_' + id, 
                revert : true
                //ghosting : true
            });
            Droppables.add('title_' + id, {
                hoverclass : 'drop',
                onDrop : doDrop
            });
            Droppables.add('handle_' + id, {
                hoverclass : 'drop',
                onDrop : doDrop
            });
        });
	if ($('trash')) {
	    Droppables.add('trash', {
		    hoverclass : 'drop',
			onDrop : destroyTask,
			accept : 'deletable'
			});
	} 
    }
}

addLoadEvent(createDragDrop);

function toggle(obj) {
    obj.style.display = (obj.style.display != 'none' ? 'none' : '');
}

function filterDeadline() {
    var filtervalue = $('deadline_filter').value;

    if (filtervalue == 'All') {
	$A($('tasks').getElementsByTagName('li')).each(function(node) {
		node.show();
	    });
	return;
    }
    if (filtervalue == 'None') {
	$A($('tasks').getElementsByTagName('li')).each(function(node) {
		if (!node.getAttribute('deadline'))
		    node.show();
		else
		    node.hide();
	    });
	return;
    }
    
    var byThisDate = new Date();
    byThisDate.setDate(byThisDate.getDate() + parseInt(filtervalue) + 1);
    $A($('tasks').getElementsByTagName('li')).each(function(node) {
	    var deadline = node.getAttribute('deadline');
	    if (deadline) {
		var db = new DateBocks();
		var nodeDate = db.parseDateString(deadline);
		if (nodeDate < byThisDate) {
		    node.show();
		} else {
		    node.hide();
		}
	    } else {
		node.hide();
	    }
	});
}

function filterField(fieldname) {
    filtervalue = $(fieldname + '_filter').value;
    if (filtervalue == 'All') {
	$A($('tasks').getElementsByTagName('li')).each(function(node) {
		node.show();
	    });
	return;
    }
    $A($('tasks').getElementsByTagName('li')).each(function(node) {
	    if (node.getAttribute(fieldname) != filtervalue) {
		node.hide();
	    } else {
		node.show();
	    }
	});
}

function addTask(tasklist_id) {
    var title = $('title').value;
    var url = '/task/create/';
    var req = new Ajax.Request(url, {asynchronous:true, evalScripts:true, method:'post', parameters:'title='+title+';task_listID='+tasklist_id,
				     onSuccess:doneAddingTask.bind(title), onFailure:failedAddingTask});
}

function doneAddingTask(req) {
    $('tasks').appendChild(evalHTML(req.responseText));
    var id = parseInt(req.responseText.match(/task_id="\d+"/)[0].replace('task_id="', ''));
    var drag = new Draggable('task_' + id, {
	    handle : 'handle_' + id, 
	    revert : true
	});
    Droppables.add('title_' + id, {hoverclass:'drop', onDrop:doDrop});
    Droppables.add('handle_' + id, {hoverclass:'drop', onDrop:doDrop});
    
    $A(document.forms[0].getElements()).each(function(node) {
	    if (node.type == "checkbox") 
		node.checked = false;
	    else if (node.type == "submit" || node.type == "hidden")
		return;
	    else
		node.value = "";
	});
    $('title').focus();
    return;
}

function failedAddingTask(req) {
}

function changeField(task_id, fieldname) {
    var field = $(fieldname + '_' + task_id);
    field.disabled = true;
    var url = '/task/change_field/' + task_id + '?field=' + fieldname;
    var req = new Ajax.Request(url, {asynchronous:true, evalScripts:true, method:'post', parameters:fieldname + '=' + field.value,
				     onSuccess:doneChangingField.bind([task_id, fieldname]), onFailure:failedChangingField.bind([task_id, fieldname])});
}

function viewChangeableField(task_id, fieldname) {
    $(fieldname + '-label_' + task_id).hide();
    $(fieldname + '-form_' + task_id).show();
}

function hideChangeableField(task_id, fieldname) {
    $(fieldname + '-form_' + task_id).hide();
    $(fieldname + '-label_' + task_id).show();
}

function updateTaskItem(task_id) {
    var tasktext = $('title_' + task_id);
    var taskitem = $('task_' + task_id);
    var completed = (taskitem.getAttribute('status') == 'done') ? 'completed-task' : 'uncompleted-task';
    var root;
    if (taskitem.childNodes[1].nodeType == 1) {
	root = (parseInt(taskitem.childNodes[1].getAttribute('depth')) === 0) ? 'root-task' : 'sub-task';
    } else {
	root = 'root-task';
    }
    tasktext.setAttribute('class', completed + ' ' + root);
}

function revertField(task_id, fieldname) {
    var field = $(fieldname + '_' + task_id);
    var orig = field.getAttribute('originalvalue');
    var fieldlabel = $(fieldname + '-label_' + task_id);
    field.value = orig;
    fieldlabel.innerHTML = orig;
    hideChangeableField(task_id, fieldname);
}

function doneChangingField(req) {
    if (req.responseText == "ok") {
	succeededChangingField.bind(this)(req);
    } else {
	failedChangingField.bind(this)(req);
    }
}

function succeededChangingField(req) {
    var task_id = this[0];
    var fieldname = this[1];
    var field = $(fieldname + '_' + task_id);
    var newvalue = (field.value ? field.value : "No " + fieldname);
    field.setAttribute('originalvalue', newvalue);
    field.disabled = false;
    field.style.color = "black"; 
    var label = $(fieldname + '-label_' + task_id);
    label.innerHTML = newvalue;
    $('task_' + task_id).setAttribute(fieldname, field.value);
    updateTaskItem(task_id);
    hideChangeableField(task_id, fieldname);
}

function failedChangingField(req) {    
    var task_id = this[0];
    var fieldname = this[1];
    var field = $(fieldname + '_' + task_id);
    var fieldlabel = $(fieldname + '-label_' + task_id);
    revertField(task_id, fieldname);
    field.disabled = false;
    fieldlabel.style.color = "red";
}

function doneMovingTask(req) {
    var task_id = this['task_id'];
    var old_parent_id = this['old_parent_id'];
    var new_parent_id = this['new_parent_id'];
    var new_sibling_id = this['new_sibling_id'];
    if (old_parent_id > 0 && old_parent_id != new_parent_id) {
        var old_parent = $('task_' + old_parent_id);
        var child = $('task_' + task_id);
        if (old_parent.getElementsByTagName('LI').length - child.getElementsByTagName('LI').length < 2) {
            flattenTask(old_parent_id);
        }
    }
    if (new_parent_id) {

        insertTaskUnderParent(task_id, new_parent_id);
        expandTask(new_parent_id);
    } else if (new_sibling_id) {
        insertTaskAfterSibling(task_id, new_sibling_id);
    }
    updateTaskItem(task_id);
}

function hideCreate() {
    $('create').show();
    $('show_create').hide();
    $('create_anchor').scrollTo();
    $('title').focus();
    return false;
}

var mode = 'view';

function resetChildDepths(elem) {
    var child_ul = elem.getElementsByTagName('UL')[0].childNodes;

    if (child_ul.length > 0) {
        var new_depth = parseInt(elem.childNodes[1].getAttribute('depth')) + 1;
        $A(child_ul).each(function(child) {
            if (child.tagName == 'LI') {
                var title = child.childNodes[1];

                title.setAttribute('depth', new_depth);
                //var left = new_depth * 15;
                //title.style.paddingLeft = left + 'px'; 
                indentTaskItem(title,new_depth)
                resetChildDepths(child);
            }
        });
    }
}

function insertAfter(new_node, after) {
    if (after.nextSibling) {
        after.parentNode.insertBefore(new_node, after.nextSibling);
    } else {
        after.parentNode.appendChild(new_node);
    }
}

var observer = Class.create();

observer.prototype = {
    element: null,
    
    initialize : function() {
    },

    onStart : function(event_name, draggable, event) {
        Droppables.remove(draggable.handle);
	draggable.handle.setAttribute('drag', "true");
    },

    onEnd : function(event_name, draggable, event) {
        Droppables.add (draggable.handle.id, {
            hoverclass : 'drop',
            onDrop : doDrop
        });
        // TODO consume the event so it doesn't trigger a click on mouse-up
    }
};

function debugThing() { 
}

function indentTaskItem(task, depth) {
    var children = task.getElementsByTagName('IMG');
    var target; 
    for (var i = 0; i < children.length; i++) {
	var child = children[i];
	if (child.getAttribute('class').match('handle')) {
	    target = child; 
	    break; 
	}
    }
    target.style.paddingLeft = 15*depth + 'px'; 
}

function insertTaskAfterSibling(task_id, sibling_id) {
    var child = $('task_' + task_id);
    var new_sibling = $('task_' + sibling_id);

    insertAfter(child, new_sibling);

    var new_index = parseInt(new_sibling.getAttribute('sort_index'));
    var ul = child.parentNode;

    //update sort_index
    var items = ul.getElementsByTagName('LI');
    var j;
    $A(items).each(function(item) {
        if (item == child) {
            item.setAttribute('sort_index', new_index + 1);
        } else {
            var sort_index = parseInt(item.getAttribute('sort_index'));
            if (sort_index > new_index) {
                item.setAttribute('sort_index', sort_index + 1);
            }
        }
    });

    //update depth
    if (new_sibling.childNodes[1].getAttribute('depth') > 0) {
        var parent = child.parentNode.parentNode;
        resetChildDepths(parent);
    } else {
        var title = child.childNodes[1];

        title.setAttribute('depth', 0);
        //title.style.paddingLeft = '0px'; 
        indentTaskItem(title,0); 
        resetChildDepths(child);
    }
}

function insertTaskUnderParent(child_id, parent_id) {
    var child = $('task_' + child_id);
    var new_parent = $('task_' + parent_id);
    //find new parent's contained ul
    v = new_parent;

    var ul = new_parent.getElementsByTagName('UL');
    if (ul.length) {
        ul = ul[0];
        ul.insertBefore(child, ul.childNodes[0]);
        var items = ul.getElementsByTagName('LI');
        //update sort_index
        $A(items).each(function(item) {
            var sort_index = parseInt(item.getAttribute('sort_index'));
            item.setAttribute('sort_index', sort_index + 1);
        });
        var sort_index = parseInt(items[0].getAttribute('sort_index'));
        items[0].setAttribute('sort_index', 0);
        //set child indent

        var parenttitle = new_parent.childNodes[1];
        var parentdepth = parseInt(parenttitle.getAttribute('depth'));
        var title = child.childNodes[1];
        title.setAttribute('depth', parentdepth + 1);
        //title.style.paddingLeft = (parentdepth + 1) * 15 + 'px'; 
        indentTaskItem(title,parentdepth+1); 
        resetChildDepths(child);	
        return;
    }
}

function doneDestroyingTask(req) {
    var task_id = this;
    $('task_' + task_id).remove();
}

function failedDestroyingTask(req) {
    var task_id = this;
    $('task_' + task_id).show();    
}

function destroyTask(child, drop_target) {
    var task_id = child.getAttribute('task_id');
    $('task_' + task_id).hide();
    var req = new Ajax.Request('/task/destroy/' + task_id, {asynchronous:true, evalScripts:true, method:'post',
        onSuccess:doneDestroyingTask.bind(task_id), onFailure:failedDestroyingTask.bind(task_id)});
}

function doDrop(child, drop_target, a) {
    var id;
    if (drop_target == child) {
        return;
    }
    var task_id = child.getAttribute('task_id');
    var old_parent_id = child.parentNode.parentNode.getAttribute('task_id');

    if (drop_target.id.match(/^title_/)) {   // drop under a parent node
        id = parseInt(drop_target.id.replace(/^title_/, ''));
        var new_parent = $('task_' + id);
	new Ajax.Request('/task/move/' + task_id, {asynchronous:true, evalScripts:true, method:'post',
            parameters:'new_parent=' + id,
            onSuccess:doneMovingTask.bind({task_id:task_id, old_parent_id:old_parent_id, new_parent_id:id}),
            onFailure:debugThing});
    } else {   // drop after a sibling node
        id = parseInt(drop_target.id.replace(/^handle_/, ''));
        var new_sibling = $('task_' + id);
        new Ajax.Request('/task/move/' + task_id, {asynchronous:true, evalScripts:true, method:'post',
            parameters:'new_sibling=' + id,
            onSuccess:doneMovingTask.bind({task_id:task_id, old_parent_id:old_parent_id, new_sibling_id:id}),
            onFailure:debugThing});
    }
}

function sortULBy(ul, column) {
    items = $A(ul.childNodes);
    items = items.findAll(function(x) {
        return x.tagName == "LI";
    });

    items = items.sort(function (x, y) {
        a = x.getAttribute(column);
        b = y.getAttribute(column);
        if (a > b) 
            return 1;
        else if (b > a) 
            return -1;
        else if (x.getAttribute('sort_index') > y.getAttribute('sort_index')) 
            return 1;
        else if (x.getAttribute('sort_index') < y.getAttribute('sort_index'))
            return -1;
        else
            return 0;
    });

    items.each (function (x) { ul.removeChild(x); });
    items.each (function (x) {
        ul.appendChild(x);
        child_ul = x.getElementsByTagName('UL');
        if (child_ul) {
            child_ul = child_ul[0];
            sortULBy(child_ul, column);
        }
    });
}

function toggleCollapse(task_id) {
    if($('handle_' + task_id).getAttribute('drag') == "true") {
	$('handle_' + task_id).setAttribute('drag', "");
	return;
    }

    $A($('task_' + task_id).childNodes).each(function(node) {        
        if (node.className) {
            if (node.className.match('^task_list')) {
                toggle(node);
            }
        }
    });
    var button = $('handle_' + task_id);
    if (button.src.match("minus.png")) {
        button.src = button.src.replace("minus.png", "plus.png");
    } else if (button.src.match("plus.png")) {
        button.src = button.src.replace("plus.png", "minus.png");
    }
}

function expandTask(task_id) {
    var collapse = $('handle_' + task_id);
    if (collapse.src.match("blank.png")) {
        collapse.src = collapse.src.replace("blank.png", "plus.png");
    } else if (collapse.src.match("minus.png")) {
        toggleCollapse(task_id);
    }
}

function flattenTask(task_id) {
    var collapse = $('handle_' + task_id);
    collapse.src = collapse.src.replace(/(plus|minus).png$/, "blank.png");
}

function sortBy(column) {
    sortULBy($('tasks'), column);
}

var initialized = false;

function modeSwitch() {

    if (mode == 'view') {
        $A($('tasks').getElementsByTagName('IMG')).each(function (x) {
            if (x.className == "handle") 
                x.style['cursor']="move";
        });
        mode = 'reorder';
        sortBy('sort_index');
        $('modeName').innerHTML = 'Done reordering';
        if ($('create_section')) 
            $('create_section').hide();
    } else {
        $A($('tasks').getElementsByTagName('IMG')).each(function (x) {
            if (x.className == "handle") 
                x.style['cursor']="";
        });
        mode = 'view';
        $('modeName').innerHTML = 'Reorder';
        if ($('create_section')) 
            $('create_section').show();
    }
}

