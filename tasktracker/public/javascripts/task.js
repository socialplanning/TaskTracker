// Copyright (C) 2006 The Open Planning Project

// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the 
// Free Software Foundation, Inc., 
// 51 Franklin Street, Fifth Floor, 
// Boston, MA  02110-1301
// USA
// See http://www.gnu.org/licenses/gpl-faq.html#WMS for the explanation for this:

// As a special exception to GPL, any HTML file which merely makes
// function calls to this code, and for that purpose includes it by
// reference shall be deemed a separate work for copyright law
// purposes. In addition, the copyright holders of this code give you
// permission to combine this code with free software libraries that
// are released under the GNU LGPL. You may copy and distribute such a
// system following the terms of the GNU GPL for this code and the
// LGPL for the libraries. If you modify this code, you may extend
// this exception to your version of the code, but you are not
// obligated to do so. If you do not wish to do so, delete this
// exception statement from your version.

function find(thing, item) {
    if( length(thing) ) {
	var i;
	for( i = 0; i < thing.length; i++ )
	    if( thing[i] == item )
		return i;
    }
    return -1;
}

function insertBeforeInList(thing, newitem, olditem) {
    if( length(thing) ) {
	var i;
	for( i = thing.length - 1; i > -1; i-- ) {
	    thing[i+1] = thing[i];
	    if( thing[i] == olditem ) {
		thing[i] = newitem;
		return i;
	    }
	}
    }
    thing[0] = newitem;
    return -1;
}

function insertAfterInList(thing, newitem, olditem) {
    if( length(thing) ) {
	var i;
	for( i = thing.length - 1; i > -1; i-- ) {
	    thing[i+1] = thing[i];
	    if( thing[i] == olditem ) {
		thing[i+1] = newitem;
		return i;
	    }
	}
    }
    thing[0] = newitem;
    return -1;
}

function addClass(element, classname) {
    if (!hasClass(element, classname))
	element.className += element.className ? ' ' + classname : classname;
}

function removeClass(element, classname) {
    var removeMe = element.className.match(' ' + classname) ? ' ' + classname : classname;
    element.className = element.className.replace(removeMe, '');
}

function hasClass(element, classname) {
    return new RegExp('\\b' + classname + '\\b').test(element.className);
}

function length(thing) {
    return (thing && thing.length ? thing.length : 0);
}

function showFilterColumn(field) {
    $(field + '-filter-label').hide();
    $(field + '_filter').show();
    $(field + '_filter').focus();
}


var CustomDraggable = Class.create();
CustomDraggable.prototype = (new Rico.Draggable()).extend( {
	initialize: function( htmlElement, refElement, owner, name ) {
	    this.type        = 'Custom';
	    this.refElement  = $(refElement);
	    this.htmlElement = $(htmlElement);
	    this.owner       = $(owner);
	    this.name        = name;
	},

	startDrag: function() {
	    addClass(this.refElement, 'drag');
	    dndMgr.deregisterDropZone(this.owner.dropzone);
	    var dereg = function(list) {
		$A(list).each(function(node) {
			addClass($('draggable_' + node.getAttribute("task_id")), 'undroppable');
			dereg(node.childTasks);
			dndMgr.deregisterDropZone(node.dropzone);
		    })
	    };
	    dereg(this.owner.childTasks);
	},

	cancelDrag: function() {
	    removeClass(this.refElement, 'drag');
	    dndMgr.registerDropZone(this.owner.dropzone);
	    var reg = function(list) {
		$A(list).each(function(node) {
			removeClass($('draggable_' + node.getAttribute("task_id")), 'undroppable');
			reg(node.childTasks);
			dndMgr.registerDropZone(node.dropzone);
		    })
	    };
	    reg(this.owner.childTasks);
	},

	endDrag: function() {
	    dndMgr.registerDropZone(this.owner.dropzone);
	    var reg = function(list) {
		$A(list).each(function(node) {
			removeClass($('draggable_' + node.getAttribute("task_id")), 'undroppable');
			reg(node.childTasks);
			dndMgr.registerDropZone(node.dropzone);
		    })
	    };
	    reg(this.owner.childTasks);
	},

	getSingleObjectDragGUI: function() {
	    var el = this.htmlElement;
	    
	    var div = document.createElement("div");
	    div.className = 'customDraggable';
	    
	    div.style.width = this.htmlElement.offsetWidth;

	    var text = el.innerHTML;
	    new Insertion.Top( div, text );
	    return div;
	}
    } );




var CustomDropzone = Class.create();
CustomDropzone.prototype = (new Rico.Dropzone()).extend( {
	initialize: function( htmlElement, refElement, owner ) {
	    this.htmlElement     = $(htmlElement);
	    this.refElement      = $(refElement);
	    this.owner           = $(owner);
	    this.absoluteRect    = null;
	    this.acceptedObjects = [];
	},
	
	showHover: function() {
	    addClass(this.htmlElement, 'drop');
	},

	activate: function() {
	    return;
	},

	hideHover: function() {
	    removeClass(this.htmlElement, 'drop');
	},
	
	accept: function(draggableObjects) {
	    var l = draggableObjects.length;
	    var i;
	    for (i = 0; i < l; i++) {
		doDrop(draggableObjects[i].refElement, this.refElement);
	    }
	}
	
    } );

var myrules = {
    '.draggable' : function(element) {
	
	element.onclick = function(e) {
	    e = e || event;
	    if (hasClass(element, 'drag')) {
		removeClass(element, 'drag');
		return false;
	    } else {
		if (e.target && e.target.doclick) {
		    e.target.doclick(e);
		}
		else if (e.srcElement && e.srcElement.doclick) {
		    e.srcElement.doclick(e);
		}
	    }
	    
	}
    },

    '#add_a_task' : function(element) {
	element.doclick = function() {
	    hideCreate();
	    return false;
	}
    },
    '.treewidget' : function(element) {
	element.doclick = function() {
	    toggleCollapse(element.id.replace("handle_", ""));
	    return false;
	}
    },
    '.task_item' : function(element) {
	element.doclick = function() {
	    document.location = element.href;
	    return false;
	}
    },
    
    '#show_description' : function(element) {
	element.onclick = function() {
	    $('hideable_add_description').hide();
	    $('hideable_title_label').show();
	    $('description_field').show();
	    $('text').focus();  // TODO this line seems to cause a javascript exception (but still works)
	    return false;
	}
    }

};

Behaviour.register(myrules);

// "ported" from http://trac.mochikit.com/wiki/ParsingHtml
function evalHTML(value) {
    if (typeof(value) != 'string') {
	return null;
    }
    value = value.strip();
    if (value.length == 0) {
	return null;
    }
    // work around absurd ie innerHTML limitations 
    var parser = document.createElement("DIV");
    parser.innerHTML = "<TABLE><TBODY>" + value + "</TBODY></TABLE>";
    
    var body = parser.firstChild.firstChild; 

    var html = document.createDocumentFragment();

    var child; 
    for (i = 0; i < body.childNodes.length; i++) {
	child = body.childNodes[i];
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

function setTaskParents() {
    if (hasReorderableTasks()) {
	$A($('tasks').getElementsByClassName('task-item')).each(function(task) {
		var parentID;
		var parent;
		if( !task.childTasks ) task.childTasks = [];
		if( (parentID = task.getAttribute("parentID")) && (parent = $('task_' + parentID)) ) {
		    if( length(parent.childTasks) )
			parent.childTasks[parent.childTasks.length] = task;
		    else
			parent.childTasks = [task]
		}
	    });
    }
}

function createDragDrop() {
    if (!initialized && hasReorderableTasks()) {
        initialized = true;

        $A($('tasks').getElementsByClassName('task-item')).each(function(node) {
		var id = node.getAttribute('task_id');
		dndMgr.registerDraggable( node.draggable = new CustomDraggable('draggable_' + id, 'draggable_' + id, node.id, 'draggable-name') );
		dndMgr.registerDropZone( node.dropzone = new CustomDropzone( 'title_' + id, 'title_' + id, node.id ) );
		//		dndMgr.registerDropZone( new CustomDropzone( 'handle_' + id, 'handle_' + id ) );
	    });
	/*
	if ($('trash')) {
	    Droppables.add('trash', {
		    hoverclass : 'drop',
			onDrop : destroyTask,
			accept : 'deletable'
			});*/
    }
}

function setupEmptyList() {
    if ($('tasks') && !($('tasks').getElementsByClassName('task-item').length))
	hideCreate();
}

addLoadEvent(createDragDrop);
addLoadEvent(setupEmptyList);
addLoadEvent(setTaskParents);

function toggle(obj) {
    obj.style.display = (obj.style.display != 'none' ? 'none' : '');  //todo hey, this is no good.
}

function filterDeadline() {
    var filtervalue = $('deadline_filter').value;

    if (filtervalue == 'All') {
	return;
    }
    if (filtervalue == 'None') {
	$A($('tasks').getElementsByClassName('task-item')).each(function(node) {
		if (node.getAttribute('deadline'))
		    node.hide();
	    });
	return;
    }
    
    var dates = filtervalue.split(",");
    var min; 
    var max;
    if (dates.length == 1) {
	min = -1 * parseInt(dates[0]);
	max = parseInt(dates[0]);
    } else {
	min = parseInt(dates[0]);
	max = parseInt(dates[1]);
    }
    var minDate = new Date();
    var byThisDate = new Date();
    minDate.setDate(minDate.getDate() - min);
    byThisDate.setDate(byThisDate.getDate() + max + 1);
    $A($('tasks').getElementsByClassName('task-item')).each(function(node) {
	    var deadline = node.getAttribute('deadline');
	    if (deadline) {
		var db = new DateBocks();
		var nodeDate = db.parseDateString(deadline);
		if (!(nodeDate < byThisDate)) {
		    node.hide();
		}
		if (min <= max && !(nodeDate > minDate)) {
		    node.hide();
		}
	    } else {
		node.hide();
	    }
	});
}

function filterField(fieldname) {
    if (fieldname == "deadline") {
	filterDeadline();
	return;
    }
			
    filtervalue = $(fieldname + '_filter').value;
    if (filtervalue == 'All') {
	return;
    }
    $A($('tasks').getElementsByClassName('task-item')).each(function(node) {
	    if (node.getAttribute(fieldname) != filtervalue) {
		node.hide();
	    }
	});
}

function filterListByAllFields() {
    $A($('tasks').getElementsByClassName('task-item')).each(function(node) {
	    node.show();
	});
    $A(["status", "deadline", "priority", "owner"]).each(function(field){
	    var filter = $(field + '_filter');
	    var filtervalue = filter.value;
	    $(field + '-filter-label').innerHTML = filter.options[filter.selectedIndex].innerHTML;
	    if (filtervalue == "All")
		return;
	    filterField(field);
	});
}

function restoreAddTask() { 
    $('add_task_anchor').appendChild($('movable_add_task'));
    hideCreate();
    $('add_task_form').getInputs()[1].setAttribute("value", 0);
    $('add_task_form').getInputs()[2].setAttribute("value", 0);
    return false;
}

function doneAddingTask(req) {
    var forminputs = $('add_task_form').getInputs();
    var parentID = parseInt(forminputs[1].getAttribute("value"));
    var siblingID = parseInt(forminputs[2].getAttribute("value"));
    var node = evalHTML(req.responseText);

    var table = $('tasks');
    if (siblingID != 0){ 
	var sibling = $('task_' + siblingID);
	insertAfter(node, sibling);  //todo
    } else if (parentID != 0) {
	var parent = $('task_' + parentID);
	insertAfter(node, parent);  //todo
	updateTaskItem(parentID);
	$('movable_add_task').parentNode.appendChild($('movable_add_task'));
    } else {
	target = table; 
	// scan for magic ie TBODY 
	for (i = 0; i < table.childNodes.length; ++i) {
	    child = table.childNodes[i]; 
	    if (child.tagName == 'TBODY') {
		target = child; 
		break; 
	    }
	}
	target.appendChild(node);
    }
    
    $('num_uncompleted').innerHTML = parseInt($('num_uncompleted').innerHTML) + 1;

    var id = parseInt(req.responseText.match(/task_id="\d+"/)[0].replace('task_id="', ''));

    dndMgr.registerDraggable( node.draggable = new CustomDraggable('draggable_' + id, 'draggable_' + id, 'task_' + id, 'draggable-name') );
    dndMgr.registerDropZone( node.dropzone = new CustomDropzone( 'title_' + id, 'title_' + id, 'task_' + id ) );
    Behaviour.apply();

    $A($('add_task_form').getElements()).each(function(node) {
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
    $(fieldname + '_' + task_id).focus();
}

function hideChangeableField(task_id, fieldname) {
    $(fieldname + '-form_' + task_id).hide();
    $(fieldname + '-label_' + task_id).show();
}

function updateTaskItem(task_id) {
    var tasktext = $('title_' + task_id);
    var taskitem = $('task_' + task_id);
    var handle = $('handle_' + task_id);
    var completed;
    if (taskitem.getAttribute('status') == 'done') 
	completed = 'completed-task';
    else {
	var db = new DateBocks();
	var date = taskitem.getAttribute('deadline');
	var now = new Date();
	if (date && db.parseDateString(date) < now) {
	    completed = 'overdue-task';
	}
	else
	    completed = 'uncompleted-task';
    }
    var root;
    if (taskitem.childNodes[1].nodeType == 1) {
	root = (parseInt(taskitem.childNodes[1].getAttribute('depth')) === 0) ? 'root-task' : 'sub-task';
    } else {
	root = 'root-task';
    }
    tasktext.setAttribute('class', completed + ' ' + root);
    if( length(taskitem.childTasks) ) {
	expandTask(task_id);
    } else {
	flattenTask(task_id);  // todo test this half
    }
    var uncompletedTasks = 0;
    $A(document.getElementsByClassName("task-item")).each(function(task) {
	    if (task.getAttribute('status') != 'done')
		uncompletedTasks++;
	});
    $('num_uncompleted').innerHTML = uncompletedTasks;
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
    if (req.status == 200) {
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
    if (fieldname == 'deadline') {
	label.innerHTML = pretty_date_from_text(newvalue);
    } else {
	label.innerHTML = newvalue;
    }
    $('task_' + task_id).setAttribute(fieldname, req.responseText);
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
	oop = old_parent;
	chil = child;
	old_parent.childTasks.removeItem(child);
        if( !length(old_parent.childTasks) )
            flattenTask(old_parent_id);
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
    //    $('create_anchor').scrollTo();
    $('title').focus();
    return false;
}

var mode = 'view';

function resetChildDepths(elem) {
    var children = elem.childTasks;
    
    if( length(children) ) {
        var new_depth = parseInt(children[0].getAttribute('depth')) + 1;
        $A(children).each(function(child) {
		var title = child.childNodes[1];		
		title.setAttribute('depth', new_depth);
		//var left = new_depth * 15;
		//title.style.paddingLeft = left + 'px'; 
		indentTaskItem(title, new_depth);
		resetChildDepths(child);
	    });
    }
}

function insertAfter(new_node, after) {
    if( after.nextSibling ) {
        after.parentNode.insertBefore(new_node, after.nextSibling);
    } else {
        after.parentNode.appendChild(new_node);
    }
}

function debugThing() { 
}

function indentTaskItem(task, depth) {
    var children = task.getElementsByTagName('IMG');
    var target; 
    for( var i = 0; i < children.length; i++ ) {
	var child = children[i];
	if( hasClass(child, 'handle') ) {
	    target = child; 
	    break; 
	}
    }
    target.style.marginLeft = 15*depth + 'px'; 
}

// TODO test this!
function insertTaskAfterSibling(task_id, sibling_id) {
    var child = $('task_' + task_id);
    var new_sibling = $('task_' + sibling_id);

    var parent = $('task_' + new_sibling.getAttribute('parentID'));
    insertAfterInList(parent.childTasks, child, new_sibling);
    insertAfter(child, new_sibling);
    
    var new_index = parseInt(new_sibling.getAttribute('sort_index'));

    //update sort_index
    // TODO fix this!
    /*
    var items = $('tasks').getElementsByTagName('task-item');
    $A(items).each(function(item) {
        if (item == child) {
            item.setAttribute('sort_index', new_index + 1);
        } else {
            var sort_index = parseInt(item.getAttribute('sort_index'));
            if (sort_index > new_index) {
                item.setAttribute('sort_index', sort_index + 1);
            }
        }
	});*/

    /*  TODO this is definitely broken.. fix it
    //update depth
    if ($('draggable_' + sibling_id).getAttribute('depth') > 0) {
        resetChildDepths(parent);
    } else {
        $('draggable_' + child_id).setAttribute('depth', 0);
        //title.style.paddingLeft = '0px'; 
        indentTaskItem(title, 0);
        resetChildDepths(child);
	}*/
}

function insertTaskUnderParent(child_id, parent_id, justmove) {
    var child = $('task_' + child_id);
    var new_parent = $('task_' + parent_id);

    var table = $('tasks');

    if( !justmove ) {
	if( length(new_parent.childTasks) ) {
	    insertBeforeInList(new_parent.childTasks, child, new_parent.childTasks[0]);
	}
	else {
	    new_parent.childTasks[0] = child;
	}
    }
    insertAfter(child, new_parent);

    //set child indent
    var parentdepth = parseInt($('draggable_' + parent_id).getAttribute('depth'));
    var title = $('draggable_' + child_id);
    title.setAttribute('depth', parentdepth + 1);

    indentTaskItem(title,parentdepth+1); 
    resetChildDepths(child);	

    $A(child.childTasks).each(function(node) {
	    insertTaskUnderParent(node.getAttribute("task_id"), child_id, 1);
	});

    //todo update all taskitems
    if( justmove )
	return;

    var items = new_parent.childTasks;
    //update sort_index
    $A(items).each(function(item) {
            var sort_index = parseInt(item.getAttribute('sort_index'));
            item.setAttribute('sort_index', sort_index + 1);
        });
    var sort_index = parseInt(items[0].getAttribute('sort_index'));
    items[0].setAttribute('sort_index', 0);
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
    // if it's "add a task" element
    if (!child.id.match("draggable")) {  // TODO be more specific
	if (drop_target.id.match(/^title_/)) {   // drop under a parent node
	    id = parseInt(drop_target.id.replace(/^title_/, ''));
	    $('add_task_form').getInputs()[1].setAttribute("value", id);
	    $('add_task_form').getInputs()[2].setAttribute("value", 0);
	    var new_parent = $('task_' + id);
	    var tr = document.createElement("TR");
	    tr.className = "taskrow";
	    tr.appendChild(child);
	    insertAfter(tr, new_parent);
	    // todo indentation
	} else {   // drop after a sibling node
	    id = parseInt(drop_target.id.replace(/^handle_/, ''));
	    $('add_task_form').getInputs()[1].setAttribute("value", 0);
	    $('add_task_form').getInputs()[2].setAttribute("value", id);
	    var new_sibling = $('task_' + id);
	    var ul = new_sibling.parentNode;
	    var li = document.createElement("li");
	    li.className = "taskrow";
	    li.appendChild(child);
	    insertAfter(child, new_sibling);
	}
	return;
    }

    // otherwise, it's a task
    var task_id = child.id.replace("draggable_", "");
    var old_parent_id = $('task_' + task_id).getAttribute("parentID");

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

// todo fix this function!
function sortULBy(ul, column, forward) {
    /*
    items = $A(ul.childNodes);
    items = items.findAll(function(x) {
	    return x.tagName == "LI";
	});

    items = items.sort(function (x, y) {
	    a = x.getAttribute(column);
	    b = y.getAttribute(column);
	    if (!a && b)
		return 1 * forward;
	    else if (!b && a)
		return -1 * forward;
	    else if (a > b) 
		return 1 * forward;
	    else if (b > a) 
		return -1  * forward;
	    else if (x.getAttribute('sort_index') > y.getAttribute('sort_index')) 
		return 1  * forward;
	    else if (x.getAttribute('sort_index') < y.getAttribute('sort_index'))
		return -1  * forward;
	    else
		return 0;
	});

    items.each (function (x) { ul.removeChild(x); });
    items.each (function (x) {
        ul.appendChild(x);
        child_ul = x.getElementsByClassName('task_list');
        if( child_ul.length ) {
            child_ul = child_ul[0];
            sortULBy(child_ul, column, forward);
        }
	});*/
}

function toggleCollapse(task_id) {
    $A($('task_' + task_id).childTasks).each(function(node) {
	    toggle(node);
	    toggleCollapse(node.getAttribute('task_id'));
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
    $A(document.getElementsByClassName("sort-arrows")).each(function(e) {
	    e.hide();
	});
    var order;
    $A(document.getElementsByClassName("column-heading")).each(function(e) {
	    if (hasClass(e, column + '-column')) {
		e.setAttribute('sortOrder', e.getAttribute('sortOrder') == 'up' ? 'down' : 'up');
		order = e.getAttribute('sortOrder');
	    } else {
		e.setAttribute('sortOrder', '');
	    }
	});
    $(column + '-arrows').show();    

    var otherorder = (order == 'up') ? 'down' : 'up';
    addClass($(column + '-' + otherorder + '-arrow'), 'grayed-out');
    removeClass($(column + '-' + order + '-arrow'), "grayed-out");

    // todo rename this
    sortULBy($('tasks'), column, order == 'up' ? 1 : -1);
}

var initialized = false;

function with_items (klass, func, parent) {
    $A(parent.childNodes).each(function (node) {
        if (node.nodeType == 1) {
	    with_items(klass, func, node);
	    if (hasClass(node, klass))
		func(node);
	}
    });
}

function unfold () {
	var other = $('edit_' + this.id);
	other.style['display'] = 'block';
	$(this).hide();
}

function add_unfold(node) {
	node.onclick = unfold.bind(node);
}

addLoadEvent(function () { with_items ("unfolded", add_unfold, document.childNodes[0]); });