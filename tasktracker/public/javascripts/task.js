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
	    showTaskCreate();
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
		    if( len_of(parent.childTasks) )
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
		enableDragDrop(node);
	    });
	/* TODO tell this to use rico instead of scriptaculous before you uncomment it
	if ($('trash')) {
	    Droppables.add('trash', {
		    hoverclass : 'drop',
			onDrop : destroyTask,
			accept : 'deletable'
			});*/
    }
}

function enableDragDrop(node) {
    var id = node.getAttribute('task_id');
    dndMgr.registerDraggable( node.draggable = new CustomDraggable('draggable_' + id, 'draggable_' + id, node.id, 'draggable-name') );
    dndMgr.registerDropZone( node.dropzone = new CustomDropzone( 'title_' + id, 'title_' + id, node.id ) );
    dndMgr.registerDropZone( new CustomDropzone( 'handle_' + id, 'handle_' + id ) );
}

function setupEmptyList() {
    in_task_show = $('subtasks') ? 1 : 0;
    if ($('tasks') && !($('tasks').getElementsByClassName('task-item').length) && !in_task_show)
	showTaskCreate();
}

addLoadEvent(createDragDrop);
addLoadEvent(setupEmptyList);
addLoadEvent(setTaskParents);

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

function filterUpdated() {
    var filtervalue = $('updated_filter').value;

    if (filtervalue == 'All') {
	return;
    }
    if (filtervalue == 'None') {
	$A($('tasks').getElementsByClassName('task-item')).each(function(node) {
		if (node.getAttribute('updated'))
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
	min = -1 * parseInt(dates[0]);
	max = -1 * parseInt(dates[1]);
    }
    var minDate = new Date();
    var byThisDate = new Date();
    minDate.setDate(minDate.getDate() - min);  //HERE IS WHERE I AM DOING A HACK
    byThisDate.setDate(byThisDate.getDate() + max + 1);
    $A($('tasks').getElementsByClassName('task-item')).each(function(node) {
	    var deadline = node.getAttribute('updated');
	    if (deadline) {
		var db = new DateBocks();
		var nodeDate = db.parseDateString(deadline);
		if (!(nodeDate < byThisDate)) {
		    node.hide();
		}
		if (min >= max && !(nodeDate >= minDate)) {
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
    if (fieldname == "updated") {
	filterUpdated();
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
    $A(["status", "deadline", "priority", "owner", "updated"]).each(function(field){
	    var filter = $(field + '_filter');
	    if( !filter )
		return;
	    var filtervalue = filter.value;
	    setPermalink(field, filtervalue);
	    //$(field + '-filter-label').innerHTML = filter.options[filter.selectedIndex].innerHTML;
	    if (filtervalue == "All")
		return;
	    filterField(field);
	});
}

filterLookups = new Object;
filterLookups.deadline = new Object;
filterLookups.deadline['Past due'] = '-1';
filterLookups.deadline['Due today'] = '0';
filterLookups.deadline['Due tomorrow'] = '1';
filterLookups.deadline['Due in the next week'] = '0,7';
filterLookups.deadline['No deadline'] = 'None';

filterLookups.priority = new Object;
filterLookups.priority['No priority'] = 'None';

filterLookups.owner = new Object;
filterLookups.owner['No owner'] = 'None';

filterLookups.updated = new Object;
filterLookups.updated['Today'] = '0';
filterLookups.updated['Yesterday'] = '-1';
filterLookups.updated['In the past week'] = '-7,0';

function sortAndFilter() {
    if( !hasReorderableTasks() )
	return;

    var options = $('permalink').getAttribute("permalink");
    options = options.split("&");
    var i;
    var needToFilter = false;
    var needToSort = false;
    var sortOrder = false;
    for( i = 0; i < options.length; ++i ) {
	var key = options[i].split("=");
	var val = key[1];
	key = key[0];
	if( key == "sortBy" ) {
	    needToSort = val;
	} else if( key == "sortOrder" ) {
	    if( val == "up" || val == "down" )
		sortOrder = val;
	} else {  // filters are the only other possibilities; it's the controller's responsibility to restrict param keys
	    var filter = $(key + "_filter");
	    if( filter ) { // no one's restricting values, though
		filter.value = val;

		if( filter.value != val ) {
		    // filterLookups is a dict that lets us specify user-friendly versions of filter options
		    val = filterLookups[key][val];
		    filter.value = val;
		}
		    
		if( filter.value == val ) // we don't bother filtering unless the value is a valid option
		    needToFilter = true;
	    }
	}
    }

    if( needToSort )
	sortBy(needToSort, sortOrder);

    if( needToFilter )
	filterListByAllFields();
}

function restoreAddTask() { 
    $('add_task_anchor').appendChild($('movable_add_task'));
    showTaskCreate();
    $('add_task_form_parentID').setAttribute("value", 0);
    $('add_task_form_siblingID').setAttribute("value", 0);
    return false;
}

function doneAddingTask(req) {
    var parentID = parseInt($('add_task_form_parentID').getAttribute("value"));
    var siblingID = parseInt($('add_task_form_siblingID').getAttribute("value"));
    var new_fragment = evalHTML(req.responseText);
    var new_item = new_fragment.firstChild; 

    var table = $('tasks');
    if (siblingID != 0){ 
	var sibling = $('task_' + siblingID);
	insertAfter(new_fragment, sibling);  //todo
    } else if (parentID != 0 && !hasClass(table, 'all_tasks')) {
	var parent = $('task_' + parentID);
	insertAfter(new_fragment, parent);  //todo
	updateTaskItem(parentID);
	if ($('movable_add_task')) {
	    $('movable_add_task').parentNode.appendChild($('movable_add_task'));
	}
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
	target.appendChild(new_fragment);
    }
    $('num_uncompleted').innerHTML = parseInt($('num_uncompleted').innerHTML) + 1;

    new_item.childTasks = []; 
    enableDragDrop(new_item);


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


    if ($('post_add_task')) {
	eval($('post_add_task').getAttribute('func'))();
    }

    return;
}
doneMovingTask = safeify(doneMovingTask, 'doneMovingTask');
doneAddingTask = safeify(doneAddingTask, 'doneAddingTask');


function failedAddingTask(req) {
    console.log("failed to add task");
}

function changeField(task_id, fieldname) {
    var field = $(fieldname + '_' + task_id);
    field.disabled = true;
    var authenticator = $('authenticator').value;
    var url = '/task/change_field/' + task_id + '?field=' + fieldname + '&authenticator=' + authenticator;
    var value = (field.type == 'checkbox') ? field.checked : field.value;
    var taskrow = $('task_' + task_id);
    var is_preview = taskrow.getAttribute("is_preview");
    var no_second_line = taskrow.getAttribute("no_second_line");
    var req = new Ajax.Request(url, {asynchronous:true, evalScripts:true, method:'post',
				     parameters:fieldname + '=' + value + "&is_preview=" + is_preview + "&no_second_line=" + no_second_line,
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
    if( len_of(taskitem.childTasks) ) {
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
    var newNode = evalHTML(req.responseText);
    var oldVersion = $('task_' + task_id);
    var parent = oldVersion.getAttribute("parentID");
    parent = $('task_' + parent);
    var place;
    if( parent && len_of(parent.childTasks) ) {
	for( place = 0; place < parent.childTasks.length; place++ ) {
	    if( parent.childTasks[place] == oldVersion )
		break;
	}
	parent.childTasks.removeItem(oldVersion);
    }

    oldVersion.parentNode.replaceChild(newNode, oldVersion);
    newNode = $('task_' + task_id);
    newNode.childTasks = oldVersion.childTasks;
    if( parent ) {
	if ( len_of(parent.childTasks) ) {
	    if( place >= parent.childTasks.length )
		parent.childTasks[length] = newNode;
	    else 
		insertBeforeInList(parent.childTasks, newNode, parent.childTasks[place]);
	} else {
	    parent.childTasks[0] = newNode;
	}
    }

    enableDragDrop(newNode);
    var fieldname = this[1];
    /*
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
    */
    if ($('post_edit_task')) {
	func = eval($('post_edit_task').getAttribute('func'));
	func(task_id, fieldname);
    }

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
	old_parent.childTasks.removeItem(child);
        if( !len_of(old_parent.childTasks) )
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

function showTaskCreate() {
    $('create').show();
    $('show_create').hide();
    //    $('create_anchor').scrollTo();
    $('title').focus();
    return false;
}

var mode = 'view';

function resetChildDepths(elem) {
    var children = elem.childTasks;
    
    if( len_of(children) ) {
        var new_depth = parseInt(elem.getElementsByTagName("SPAN")[0].getAttribute('depth')) + 1;
        $A(children).each(function(child) {
		var title = child.getElementsByTagName("SPAN")[0];		
		title.setAttribute('depth', new_depth);
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
    if( parent ) {
	insertAfterInList(parent.childTasks, child, new_sibling); 
    }
    var sib_ch = new_sibling.childTasks;
    var preceding_task = (len_of(sib_ch) ? 
			  sib_ch[sib_ch.length - 1] :
			  new_sibling);
    insertAfter(child, preceding_task);

    //update sort_index
    var new_index = parseInt(new_sibling.getAttribute('sort_index'));
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
	});

    //update depth
    var me = $('draggable_' + task_id);
    if ($('draggable_' + sibling_id).getAttribute('depth') > 0) {	
	$('task_' + task_id).setAttribute("parentID", new_sibling.getAttribute("parentID"));
	//	indentTaskItem(me, $('handle_' + sibling_id).style.marginLeft);
        resetChildDepths(parent);
    } else {
        me.setAttribute('depth', 0);
	$('task_' + task_id).setAttribute("parentID", 0);
        //title.style.paddingLeft = '0px'; 
        indentTaskItem(me, 0);
        resetChildDepths(child);
    }
    updateTaskItem(task_id);

    $A(child.childTasks).each(function(node) {
	    insertTaskUnderParent(node.getAttribute("task_id"), task_id, 1);
	});
}

function insertTaskUnderParent(child_id, parent_id, justmove) {
    var child = $('task_' + child_id);
    var new_parent = $('task_' + parent_id);

    var table = $('tasks');

    if( !justmove ) {
	if( len_of(new_parent.childTasks) ) {
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

    if( justmove )
	return;

    child.setAttribute("parentID", parent_id);
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
	    $('add_task_form_parentID').setAttribute("value", id);
	    $('add_task_form_siblingID').setAttribute("value", 0);
	    var new_parent = $('task_' + id);
	    var tr = document.createElement("TR");
	    tr.className = "taskrow";
	    tr.appendChild(child);
	    insertAfter(tr, new_parent);
	    // todo indentation
	} else {   // drop after a sibling node
	    id = parseInt(drop_target.id.replace(/^handle_/, ''));
	    $('add_task_form_parentID').setAttribute("value", 0);
	    $('add_task_form_siblingID').setAttribute("value", id);
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

// todo make this sort respect parenting
function sortULBy(ul, column, forward, parentID) {
    if( !parentID ) parentID = "0";
    items = $A(ul.getElementsByClassName('task-item')).filter( function(i) {
	    return i.getAttribute("parentID") == parentID;
	} );

    items = items.sort(function (x, y) {
	    var a = x.getAttribute(column);
	    var b = y.getAttribute(column);
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

    ul = ul.getElementsByTagName("TBODY")[0];
    items.each(function (x) {
	    ul.removeChild(x);
	    $A(x.childTasks).each(function(i) {
		    ul.removeChild(i);
		});
	});
    items.each (function (x) {
	    ul.appendChild(x);
	    $A(x.childTasks).each(function(i) {
		    ul.appendChild(i);
		});	    
	    if( len_of(x.childTasks) )
		sortULBy($('tasks'), column, forward, x.getAttribute("task_id"));
	});
}

function setCollapse(task_id, val) {
    var node = $('task_' + task_id);
    var button = $('handle_' + task_id);
    var tomatch = val ? "minus.png" : "plus.png";
    if( val ) 
	node.show();
    else 
	node.hide();
    if( !val || button.src.match("plus.png") )
	$A(node.childTasks).each(function(n) {
		setCollapse(n.getAttribute('task_id'), val);
	    });
}

function toggleCollapse(task_id) {
    var button = $('handle_' + task_id);
    if( button.src.match("minus.png") ) {
        button.src = button.src.replace("minus.png", "plus.png");
	$A($('task_' + task_id).childTasks).each(function(node) {
		//		node.show();
		setCollapse(node.getAttribute('task_id'), 1);
	    });
    } else if (button.src.match("plus.png")) {
        button.src = button.src.replace("plus.png", "minus.png");
	$A($('task_' + task_id).childTasks).each(function(node) {
		//		node.hide();
		setCollapse(node.getAttribute('task_id'), 0);
	    });
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

function sortBy(column, order) {
    $A(document.getElementsByClassName("sort-arrows")).each(function(e) {
	    e.hide();
	});

    $A(document.getElementsByClassName("column-heading")).each(function(e) {
	    if (hasClass(e, column + '-column')) {
		if( !order )
		    order = e.getAttribute('sortOrder') == 'up' ? 'down' : 'up';
		e.setAttribute('sortOrder', order);
		addClass(e, 'selected-column');
		order = e.getAttribute('sortOrder');
	    } else {
		e.setAttribute('sortOrder', '');
		removeClass(e, 'selected-column');
	    }
	});
    $(column + '-arrows').show();    

    var otherorder = (order == 'up') ? 'down' : 'up';
    addClass($(column + '-' + otherorder + '-arrow'), 'grayed-out');
    removeClass($(column + '-' + order + '-arrow'), "grayed-out");
    
    setPermalink("sortBy", column);
    setPermalink("sortOrder", order);

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

function setPermalink(newkey, newval) {
    var a_perm = $('permalink');
    var permalink = a_perm.getAttribute('permalink');
    var items = permalink.split("&");
    var i;
    for( i = 0; i < items.length; ++i ) {
	var key = items[i].split("=");
	var val = key[1];
	var key = key[0];
	if( key == newkey ) {
	    if( newval == "All" )
		permalink = permalink.replace(key + "=" + val + "&", '');
	    else
		permalink = permalink.replace(key + "=" + val, newkey + '=' + newval);
	    a_perm.setAttribute('permalink', permalink);
	    a_perm.href = a_perm.getAttribute("base") + '?' + a_perm.getAttribute("permalink");
	    return;
	}
    }
    if( newval == 'All' ) return;
    permalink += ( newkey + "=" + newval + '&' );
    a_perm.setAttribute('permalink', permalink);
    a_perm.href = a_perm.getAttribute("base") + '?' + a_perm.getAttribute("permalink");
}

addLoadEvent(function () { with_items ("unfolded", add_unfold, document.childNodes[0]); });
addLoadEvent(sortAndFilter);