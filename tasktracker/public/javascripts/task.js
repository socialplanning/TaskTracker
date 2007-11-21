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

var AddTaskDraggable = Class.create();
AddTaskDraggable.prototype = (new Rico.Draggable()).extend( {
	initialize: function( element, name ) {
	    this.type        = 'AddTask';
	    this.refElement  = $(element);
	    this.htmlElement  = this.refElement;
	    this.name        = name;
	}
    });

var ColumnDraggable = Class.create();
ColumnDraggable.prototype = (new Rico.Draggable()).extend( {
	initialize: function( name ) {
	    this.type        = 'Column';
	    this.htmlElement = $(name + '-heading');
	    this.name        = name;
	    this.parent      = $('column-heading');
	},

	startDrag: function() {
	    var element = this.htmlElement;
	    var subtractOne = false;
	    // when a column is picked up, all the other draggable/droppable column headers are assigned ordered indices
	    $A(this.parent.getElementsByClassName("draggable-column-heading")).each( function(col, i) {
		    if( col == element ) {
			col.tmpIndex = null;
			subtractOne = true;
		    }
		    else col.tmpIndex = subtractOne ? i - 1: i;
		});

	    // when a column is picked up, that column gets a class for css styling
	    $A($('tasks').getElementsByClassName(this.name + '-column')).each( function(col) {
		    addClass(col, "currently-dragged-column");
		});
	},

	__finishDrag: function() { 
	    $A($('tasks').getElementsByClassName(this.name + '-column')).each( function(col) {
		    removeClass(col, "currently-dragged-column");
		});
	},

	endDrag: function() { 
	    this.__finishDrag();
	},
	
	cancelDrag: function() {
	    this.__finishDrag();
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
    });

var TaskItemDraggable = Class.create();
TaskItemDraggable.prototype = (new Rico.Draggable()).extend( {
	initialize: function( htmlElement, refElement, owner, name ) {
	    this.type        = 'Custom';
	    this.refElement  = $(refElement);
	    this.htmlElement = $(htmlElement);
	    this.owner       = $(owner);
	    this.name        = name;
	},

	startDrag: function() {
	    addClass(this.refElement, 'drag');
	    this.owner.dropzones.each( function(dropzone) { dndMgr.deregisterDropZone(dropzone) } );
	    var dereg = function(list) {
		$A(list).each(function(node) {
			addClass($('draggable_' + node.getAttribute("task_id")), 'undroppable');
			dereg(node.childTasks);
			node.dropzones.each( function(dropzone) { dndMgr.deregisterDropZone(dropzone) } );
		    })
	    };
	    dereg(this.owner.childTasks);
	},

	cancelDrag: function() {
	    removeClass(this.refElement, 'drag');
	    this.endDrag();
	},

	endDrag: function() {
	    this.owner.dropzones.each( function(dropzone) { dndMgr.registerDropZone(dropzone) } );
	    var reg = function(list) {
		$A(list).each(function(node) {
			removeClass($('draggable_' + node.getAttribute("task_id")), 'undroppable');
			reg(node.childTasks);
			node.dropzones.each( function(dropzone) { dndMgr.registerDropZone(dropzone) } );
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

var ColumnDropzone = Class.create();
ColumnDropzone.prototype = (new Rico.Dropzone()).extend( {
	lastColIndex: -1,

	initialize: function( name ) {
	    this.colName         = name;
	    this.htmlElement     = $(name + '-heading');
	    this.absoluteRect    = null;
	    this.acceptedObjects = [];
	    this.halfWidth = this.htmlElement.offsetWidth / 2;
	},

	canAccept: function(draggableObjects) { 
	    var l = draggableObjects[0];
	    if( l.type != 'Column' ) return false;
	    if( l.name == this.colName ) return false; 
	    return true;
	},

	activate: function(draggableObjects) { return; },

	showHover: function(draggableObjects, e) {
	    var inLeftHalf = this.__mouseInMyLeftHalf(e);

	    // first, let's find out whether the columns are already in the correct position
	    var thisColIndex = this.htmlElement.tmpIndex;
	    if( inLeftHalf )
		thisColIndex -= 0.5;
	    else
		thisColIndex += 0.5;
	    if( thisColIndex == ColumnDropzone.lastColIndex ) {
		return;
	    }
	    
	    // at this point, we know we have to do an insertion
	    if( inLeftHalf ) {
		moveSecondBeforeFirst(this.colName, draggableObjects[0].name);
	    } else {
		moveSecondAfterFirst(this.colName, draggableObjects[0].name);
	    }
	    ColumnDropzone.lastColIndex = thisColIndex;
	}, 

	hideHover: function(draggableObjects) { return; },
	
	__mouseInMyLeftHalf: function(e) {
	    return e.clientX < ( this.getAbsoluteRect().left + this.halfWidth + (e.offsetX ? document.body.scrollLeft : 0) );
	},

	accept: function(draggableObjects) {
	    ColumnDropzone.lastColLeft = ColumnDropzone.lastColRight = null;
	    var order = [];
	    $A( $('column-heading').getElementsByTagName("TH") ).each( function(col) {
		    var name = col.id.replace("-heading", '');
		    if( name == 'status' ) return;
		    order[order.length] = name;
		});
	    order = order.join(",");
	    setPermalink("columnOrder", order);
	}
    } );

var TaskItemDropzone = Class.create();
TaskItemDropzone.prototype = (new Rico.Dropzone()).extend( {
	initialize: function( htmlElement, refElement, owner, task_id, drop_reparent, indicator) {
	    this.htmlElement     = $(htmlElement);
	    this.refElement      = $(refElement);
	    this.owner           = $(owner);
	    this.absoluteRect    = null;
	    this.acceptedObjects = [];
	    this.task_id = task_id;
	    this.indicator = $(indicator);
	    this.drop_reparent = drop_reparent;
	},
	
	showHover: function() {
	    removeClass(this.indicator, 'hidden');
	},

	activate: function() {
	    return;
	},

	hideHover: function() {
	    addClass(this.indicator, 'hidden');
	},

	canAccept: function(draggableObjects) { 
	    var l = draggableObjects.length;
	    var i;
	    for (i = 0; i < l; i++) {
		if( draggableObjects[i].type == 'Column' ) return false;
	    }
	    return true;
	},
	
	accept: function(draggableObjects) {
	    var l = draggableObjects.length;
	    var i;
	    for (i = 0; i < l; i++) {
		doDrop(draggableObjects[i].refElement, this.refElement, this);
	    }
	}
	
    } );

function createColumnDragDrop(field) {
    dndMgr.registerDraggable( new ColumnDraggable(field) );
    dndMgr.registerDropZone( new ColumnDropzone(field) );
}

function createDragDrop() {
    if (!initialized && hasReorderableTasks()) {
        initialized = true;

	dndMgr.registerDropZone (new TaskItemDropzone( 'sibling_dropzone_0', 'sibling_dropzone_0', 0, 0, false, 'sibling_dropzone_indicator_0'));

        $A($('tasks').getElementsByClassName('task-item')).each(function(node) {
		enableDragDrop(node);
	    });

	if( $('deadline-heading') ) createColumnDragDrop('deadline');
	if( $('updated-heading') ) createColumnDragDrop('updated');
	if( $('priority-heading') ) createColumnDragDrop('priority');
	if( $('owner-heading') ) createColumnDragDrop('owner');

	//dndMgr.registerDraggable( new AddTaskDraggable('movable_add_task', 'movable_add_task') );
	
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
    dndMgr.registerDraggable( node.draggable = new TaskItemDraggable('draggable_' + id, 'draggable_' + id, node.id, 'draggable-name') );
    node.dropzones = [];
    dndMgr.registerDropZone( node.dropzones[0] = new TaskItemDropzone( 'child_dropzone_' + id, 'child_dropzone_' + id, node.id, id, true, 'child_dropzone_indicator_' + id) );
    dndMgr.registerDropZone( node.dropzones[1] = new TaskItemDropzone( 'sibling_dropzone_' + id, 'sibling_dropzone_' + id, node.id, id, false, 'sibling_dropzone_indicator_' + id) );
}

var myrules = {
    '.draggable' : function(element) {
	element.onclick = function(e) {
	    e = e || event;
	    if (hasClass(element, 'drag')) {
		removeClass(element, 'drag');
		return false;
	    } else {
		if (e.target && e.target.doclick) {
		    return e.target.doclick(e);
		}
		else if (e.srcElement && e.srcElement.doclick) {
		    return e.srcElement.doclick(e);
		}
	    }
	}
    },
    'img.treewidget' : function(element) {
	element.doclick = function() {
	    toggleCollapse(element.id.replace("handle_", ""));
	    return false;
	}
    },
    'a.task_item' : function(element) {
	element.doclick = function() {
	    return true;
	}
    },
    
    'a#show_description' : function(element) {
	element.onclick = function() {
	    $('hideable_add_description').hide();
	    $('hideable_title_label').show();
	    $('description_field').show();
	    $('text').focus();
	    return false;
	}
    },

    '.post-link' : function(element) { 
	var form = Builder.node('form', {action: element.getAttribute("href"), method: 'POST'});
	form.style.display = 'inline';
	element.parentNode.insertBefore(form, element);
	element.onclick = function() {
	    var msg = element.getAttribute("confirm_msg");
	    if( (msg && confirm(msg)) || !msg ) {
		form.submit();
	    }
	    return false;
	}
    },

    'th.draggable-column-heading' : function(element) {
	element.onclick = function() {
            id = this.getAttribute("id");
	    if( !this.columnName )
		this.columnName = id.replace("-heading", '');
	    sortBy(this.columnName);
	    return false;
	}
    },

    '.unfolded' : function(element) {
	element.onclick = unfold;
    },

    'a.uses_permalink' : function(element) {
	var permalink = $("permalink");
	if( permalink ) {
	    element.href = element.getAttribute("base_href") + "?" + permalink.getAttribute("permalink");
	}
    }/*,

    'a.uses_permalink' : function(element) {
	onclick = function() {
	    var permalink = $("permalink");
	    if( permalink ) {
		var do_first = function() {		    
		    element.href = element.getAttribute("base_href") + "?" + permalink.getAttribute("permalink");
		    if( do_next ) do_next();
		};
		
		dofirst();
	    }
	}
	}*/

};

Behavior.register(myrules);

function showFilterColumn(field) {
    $(field + '-filter-label').hide();
    $(field + '_filter').show();
    $(field + '_filter').focus();
}

function hasTasks() {
    return $('tasks');
}

function hasReorderableTasks() {
    var tasks = hasTasks();
    return tasks && tasks.getAttribute("hasReorderableTasks") == "True" && tasks.getElementsByTagName("TH").length;
}

function setTaskParents() {
    var tasks = hasTasks();
    if( tasks ) {
	$A(tasks.getElementsByClassName('task-item')).each(function(task) {
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

function setupEmptyList() {
    var in_task_show = $('subtasks') ? 1 : 0;
    if ($('tasks') && !($('tasks').getElementsByClassName('task-item').length) && !in_task_show)
	showTaskCreate();
}

function filterDeadline(task) {
    var filtervalue = $('deadline_filter').value;
    if (filtervalue == 'All') {
	return false;
    }
    var deadline = task.getAttribute('deadline');

    if (filtervalue == 'None') {
	if( deadline != 'None' ) {
	    return true;
	} else return false;
    }
    
    if( deadline == 'None' ) {
	return true;
    }

    var dates = filtervalue.split(",");

    if( dates.length == 1 ) {
	var equalDate = new Date();
	equalDate.setHours(0,0,0,0);
	equalDate.setDate(equalDate.getDate() + parseInt(dates[0]));
	var db = new DateBocks();
	deadline = db.parseDateString(deadline);
	deadline.setHours(0,0,0,0);
	return !equalDate.equalsTo(deadline);
    } 

    var min; 
    var max;

    min = parseInt(dates[0]);
    max = parseInt(dates[1]);

    var minDate = new Date();
    minDate.setHours(0,0,0,0);
    var byThisDate = new Date();
    byThisDate.setHours(0,0,0,0);
    minDate.setDate(minDate.getDate() - min);
    byThisDate.setDate(byThisDate.getDate() + max + 1);

    var db = new DateBocks();
    var nodeDate = db.parseDateString(deadline);
	
    if( nodeDate > byThisDate ) {
	return true;
    }
    if( min < max && (nodeDate <= minDate) ) {
	return true;
    }
    return false;

}

function filterUpdated(task) {
    var filtervalue = $('updated_filter').value;

    if (filtervalue == 'All') {
	return false;
    }
    if (filtervalue == 'None') {
	if( task.getAttribute('updated') ) {
	    return true;
	} else return false;
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

    var deadline = task.getAttribute('updated');
    if( deadline ) {
	var db = new DateBocks();
	var nodeDate = db.parseDateString(deadline);
	if( !(nodeDate < byThisDate) ) {
	    return true;
	}
	if( min >= max && !(nodeDate >= minDate) ) {
	    return true;
	}
	return false;
    } else {
	return true;
    }
}

function filterField(fieldname, task) {
    // returns true if the task is filtered away (hidden)
    if( fieldname == "deadline" ) {
	return filterDeadline(task);
    }
    if( fieldname == "updated" ) {
	return filterUpdated(task);
    }
			
    var filtervalue = $(fieldname + '_filter').value.replace(' ', '%20');

    if( filtervalue == 'All' ) {
	return false;
    }
    if( fieldname == "status" && filtervalue == "AllUncompleted" ) {
	return( task.getAttribute(fieldname) == "done" );
    }
    
    return( task.getAttribute(fieldname) != filtervalue );    
}

function filterNodeByAllFields(node) {
    var already_filtered = false;
    
    var parent = $("task_" + node.getAttribute("parentID"));
    node.depth_adjustment = 0;
    if( parent )
	node.depth_adjustment = parent.depth_adjustment || 0;
    
    $A(["status", "deadline", "priority", "owner", "updated"]).each(function(field){
	    var dont_filter = false;
	    var filter = $(field + '_filter');
	    if( !filter )
		return;
	    var filtervalue = filter.value;
	    setPermalink(field, filtervalue);
	    if (filtervalue == "All")
		dont_filter = true;
	    if( !dont_filter && !already_filtered ) {
		if( filterField(field, node) ) {
		    var second_line = $('second_line_' + node.getAttribute("task_id"));
		    if( second_line ) second_line.hide();
		    --node.depth_adjustment;
		    already_filtered = true;
		}
	    }
	    reindentTask(node.getAttribute("task_id"), node.depth_adjustment);
	});
    return already_filtered;
}

function filterListByAllFields() {
    /*
      Each task has an integer depth_adjustment (da) attribute defaulting at 0.
      When iterating to a task:
        Show the task
        task.da := task.parent.da
	for each filter:
	  if( hide-flag )
	    hideTask(task)
	    When hiding a task:
              task.da := task.da - 1
	      reindentTask( task.depth + task.da )
     */
    $A($('tasks').getElementsByClassName('task-item')).each(function(node) { 
	    if( filterNodeByAllFields(node) ) {
		node.hide();
		$("second_line_" + node.getAttribute("task_id")).hide();
	    } else {
		node.show();
		$("second_line_" + node.getAttribute("task_id")).show();
	    }
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
    if( !hasReorderableTasks() || !$('permalink') )
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

function viewChangeableField(task_id, fieldname) {
    selected_form = $(fieldname + '-form_' + task_id);
    selected_label = $(fieldname + '-label_' + task_id);
    selected_label.hide();
    selected_form.show();
    $(fieldname + '_' + task_id).focus();
}

function hideChangeableField(task_id, fieldname) {
    selected_form = null;
    selected_label = null;

    $(fieldname + '-form_' + task_id).hide();
    $(fieldname + '-label_' + task_id).show();
}

function restoreAddTask() { 
    $('add_task_anchor').appendChild($('movable_add_task'));
    showTaskCreate();
    $('add_task_form_parentID').setAttribute("value", 0);
    $('add_task_form_siblingID').setAttribute("value", 0);
    return false;
}

function doneAddingTask(req) {
    //clear error
    $('error').innerHTML = '';

    //place new task in heirarchy
    var parentID = parseInt($('add_task_form_parentID').getAttribute("value"));
    var siblingID = parseInt($('add_task_form_siblingID').getAttribute("value"));
    var new_fragment = evalHTML(req.responseText);

    var new_item = new_fragment.firstChild; 
    
    var placeholder = $('no_tasks_placeholder');
    if( placeholder ) {
	placeholder.parentNode.removeChild(placeholder);
    }

    columns = getColumnOrder();
    //status, title are always first
    columns.shift();
    columns.unshift("title");
    columns.unshift("status");
    //rearrange new_fragment into current column order
    var last = new_item.getElementsByTagName("TD")[0];
    for (var i = 1; i < columns.length; i++) {
	column = columns[i];
	var cell = new_item.getElementsByClassName(column + "-column")[0];
	insertAfter(cell, last);
	last = cell;
    }

    var table = $('tasks');
    if (siblingID != 0){
	/* We have been inserted after a sibling. */
	var sibling = $('task_' + siblingID);
	insertAfter(new_fragment, sibling);  //todo
    } else if (parentID != 0 && !hasClass(table, 'all_tasks')) {
	/* We have been inserted under a parent.  */
	var parent = $('task_' + parentID);
	insertAfter(new_fragment, parent);  //todo
	updateTaskItem(parentID);
	if ($('movable_add_task')) {
	    $('movable_add_task').parentNode.appendChild($('movable_add_task'));
	}
    } else {
	/* We have been inserted nowhere so append. */
	target = table; 
	// scan for magic ie TBODY 
	for (i = 0; i < table.childNodes.length; ++i) {
	    child = table.childNodes[i]; 
	    if (child.tagName == 'TBODY') {
		target = child; 
		break; 
	    }
	}
	tt = target;
	nf = new_fragment;
	target.appendChild(new_fragment);
    }
    //$('num_uncompleted').innerHTML = parseInt($('num_uncompleted').innerHTML) + 1;

    new_item.childTasks = []; 
    enableDragDrop(new_item);

    //Behavior.apply();

    sortAndFilter();

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

//doneAddingTask = safeify(doneAddingTask, 'doneAddingTask');
//succeededChangingField = safeify(succeededChangingField, 'suceededChangingField');

function failedAddingTask(req) {
    $('error').innerHTML = req.responseText;
    console.log("failed to add task");
}

//failedAddingTask = safeify(failedAddingTask, 'failedAddingTask');

function changeField(task_id, fieldname) {
    if( changeEventsDisabled ) {
	return;
    }
    var field = $(fieldname + '_' + task_id);
    field.disabled = true;
    var authenticator = $('authenticator').value;
    var base_url = $('global-values').getAttribute('change_url');
    var url = base_url + task_id + '?field=' + fieldname + '&authenticator=' + authenticator;
    var value = (field.type == 'checkbox') ? field.checked : field.value;
    value = encodeURIComponent(value);
    var taskrow = $('task_' + task_id);
    var is_preview = taskrow.getAttribute("is_preview");
    var is_flat = taskrow.getAttribute("is_flat");
    var editable_title = taskrow.getAttribute("editable_title");
    var depth = $("global-values"); depth = (depth ? depth.getAttribute('depth') : 0);
    var columnOrder;
    if( $('permalink') ) {
	columnOrder = $('permalink').getAttribute("permalink");
	if( columnOrder ) {
	    columnOrder = columnOrder.match(/columnOrder=[\w,]+/);
	    if( columnOrder ) 
		columnOrder = columnOrder[0];
	}
    }
    
    var req = new Ajax.Request(url, {asynchronous:true, evalScripts:true, method:'post',
				     parameters:fieldname + '=' + value + "&is_preview=" + is_preview +
				     "&is_flat=" + is_flat + 
				     "&editable_title=" + editable_title + "&depth=" + depth +
				     (columnOrder ? "&columnOrder=" + columnOrder : ''),
				     onSuccess:doneChangingField.bind([task_id, fieldname]),
				     onFailure:failedChangingField.bind([task_id, fieldname])});
}

var selected_form;
var selected_label;

function recalculateUncompletedChildren(taskitem) {
    var uncompletedTasks = 0;
    var countTasks = function(task) {
	if( task.getAttribute('status') != 'done' )
	    ++uncompletedTasks;
	task.childTasks.each( function(child) { countTasks(child); } );
    }
    taskitem.childTasks.each( function(child) { countTasks(child); } );
    
    var num_subtasks = taskitem.getElementsByClassName("num_subtasks")[0];
    num_subtasks.innerHTML = uncompletedTasks;
    if( uncompletedTasks == 0 )
	num_subtasks.parentNode.hide();
    else
	num_subtasks.parentNode.show();
    var the_word_task = taskitem.getElementsByClassName("the-word-task")[0];
    if( uncompletedTasks == 1 )
	the_word_task.innerHTML = "task";
    else
	the_word_task.innerHTML = "tasks";
}

function updateTaskItem(task_id) {
    var tasktext = $('title_' + task_id);
    var taskitem = $('task_' + task_id);
    var handle = $('handle_' + task_id);
    var completed;
    if( taskitem.getAttribute('status') == 'done' )
	completed = 'completed-task';
    else {
	var db = new DateBocks();
	var date = taskitem.getAttribute('deadline');
	completed = 'uncompleted-task';
	if( date && date != 'None' ) {
	    var now = new Date();
	    if (date && db.parseDateString(date) < now) {
		completed = 'overdue-task';
	    }
	}
    }
    var root;
    if( taskitem.childNodes[1].nodeType == 1 ) {
	root = (parseInt(taskitem.childNodes[1].getAttribute('depth')) === 0) ? 'root-task' : 'sub-task';
    } else {
	root = 'root-task';
    }
    tasktext.setAttribute('class', completed + ' ' + root);
    if( len_of(taskitem.childTasks) ) {
	expandTask(task_id);
    } else {
	flattenTask(task_id);
    }
    
    recalculateUncompletedChildren(taskitem);

    uncompletedTasks = 0;
    /* TODO THIS DOES NOT EVEN REMOTELY BELONG HERE. */
    $A(document.getElementsByClassName("task-item")).each(function(task) {
	    if (task.getAttribute('status') != 'done')
		++uncompletedTasks;
	});
    //$('num_uncompleted').innerHTML = uncompletedTasks;
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

function updateParentTask(parent) {
    recalculateUncompletedChildren(parent);
    var myParentId = parent.getAttribute("parentID");
    if( myParentId ) {
	var myParent = $('task_' + myParentId);
	if( myParent )
	    updateParentTask(myParent);
    }
}

function succeededChangingField(req) {
    var task_id = this[0];
    var fieldname = this[1];
    var field = $(fieldname + '_' + task_id);
    field.disabled = false;

    var newNode = evalHTML(req.responseText);
    var oldVersion = $('task_' + task_id);
    var parent = $('task_' + oldVersion.getAttribute("parentID"));

    oldVersion.parentNode.replaceChild(newNode, oldVersion);
    newNode = $('task_' + task_id);
    newNode.childTasks = oldVersion.childTasks;

    var place;
    if( parent && len_of(parent.childTasks) ) {
	for( place = 0; place < parent.childTasks.length; place++ ) {
	    if( parent.childTasks[place] == oldVersion )
		break;
	}
    }
    if( parent && parent.getAttribute('is_flat') != 'True' ) {
	if ( len_of(parent.childTasks) ) {
	    if( place >= parent.childTasks.length ) {
		parent.childTasks[length] = newNode;
	    } else  {
		insertBeforeInList(parent.childTasks, newNode, parent.childTasks[place]);
	    }
	} else {
	    parent.childTasks[0] = newNode;
	}
	parent.childTasks.removeItem(oldVersion);
    }



    if ($('post_edit_task')) {
	func = eval($('post_edit_task').getAttribute('func'));
	func(task_id, fieldname);
    }

    enableDragDrop(newNode);

    if( parent )
	updateParentTask(parent);

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

function reindentTask(task_id, adjustment) {
    var task = $("task_" + task_id);
    var title = task.getElementsByTagName("SPAN")[0];
    var handle = $$('#task_' + task_id + " .handle")[0];
    var depth = parseInt(title.getAttribute("depth")) + adjustment;
    handle.style.marginLeft = 15 * depth + 'px';
}

function doneMovingTask(req) {
    var order = eval(req.responseText);
    var breaking_row = $$('#breaking-row')[0].parentNode;

    var last_task = breaking_row;
    order.each(function(task_rec) {
	    var task = $('task_' + task_rec.id);    

	    if (task_rec.has_children) {
		expandTask(task_rec.id);
	    } else {
		flattenTask(task_rec.id);
	    }

	    var depth = task_rec.depth;
	    var title = task.getElementsByTagName("SPAN")[0];
	    title.setAttribute('depth', depth);
	    var handle = $$('#task_' + task_rec.id + " .handle")[0];
	    handle.style.marginLeft = 15 * depth + 'px';

	    var second_line = $('second_line_' + task_rec.id);
	    insertAfter(task, last_task);
	    insertAfter(second_line, task);
	    last_task = second_line;
	});

}

//doneMovingTask = safeify(doneMovingTask, 'doneMovingTask');

function showTaskCreate() {
    var create = $('create');
    if( create ) {
        removeClass(create, 'hidden');
        $('show_create').hide();
    //  $('create_anchor').scrollTo();
        $('title').focus();
    }
    return false;
}

var mode = 'view';

function doneDestroyingTask(req) {
    var task_id = this;
    $('task_' + task_id).remove();
    $('second_line_' + task_id).remove();
}

function failedDestroyingTask(req) {
    var task_id = this;
    $('task_' + task_id).show();
    $('second_line_' + task_id).show();
}

function destroyTask(child, drop_target) {
    var task_id = child.getAttribute('task_id');
    $('task_' + task_id).hide();
    $('second_line_' + task_id).hide();
    var req = new Ajax.Request('/task/destroy/' + task_id, {asynchronous:true, evalScripts:true, method:'post',
        onSuccess:doneDestroyingTask.bind(task_id), onFailure:failedDestroyingTask.bind(task_id)});
}

function doDrop(child, drop_target, dropzone) {
    var id;
    if (drop_target == child) {
        return;
    }
    // if it's "add a task" element
    if( !child.id.match("draggable") ) {  // TODO be more specific
	if( drop_target.id.match(/^title_/) ) {   // drop under a parent node
	    id = parseInt(drop_target.id.replace(/^title_/, ''));
	    $('add_task_form_parentID').setAttribute("value", id);
	    $('add_task_form_siblingID').setAttribute("value", 0);
	    var new_parent = $('task_' + id);
	    var tr = document.createElement("TR");
	    tr.className = "taskrow";
	    var td = document.createElement("TD");
	    td.appendChild(child);
	    tr.appendChild(td);
	    insertAfter(tr, new_parent);
	    // todo indentation
	} else {   // drop after a sibling node
	    // todo look into this block sometime. does it ever happen?
	    id = parseInt(drop_target.id.replace(/^handle_/, ''));
	    $('add_task_form_parentID').setAttribute("value", 0);
	    $('add_task_form_siblingID').setAttribute("value", id);
	    var new_sibling = $('task_' + id);
	    var new_parent = new_sibling.parentNode;
	    var tr = document.createElement("TR");
	    tr.className = "taskrow";
	    tr.appendChild(child);
	    insertAfter(child, new_sibling);
	}
	return;
    }

    // otherwise, it's a task
    var task_id = child.id.replace("draggable_", "");
    var old_parent_id = $('task_' + task_id).getAttribute("parentID");
    id = parseInt(dropzone.task_id);
    var base_url = $('global-values').getAttribute("move_url");
    if (dropzone.drop_reparent) {   // drop under a parent node
        var new_parent = $('task_' + id);
	new Ajax.Request(base_url + task_id, {asynchronous:true, evalScripts:true, method:'post',
            parameters:'new_parent=' + id,
            onSuccess:doneMovingTask,
            onFailure:debugThing});
    } else {   // drop after a sibling node
        var new_sibling = $('task_' + id);
        new Ajax.Request(base_url + task_id, {asynchronous:true, evalScripts:true, method:'post',
            parameters:'new_sibling=' + id,
            onSuccess:doneMovingTask,
            onFailure:debugThing});
    }
}

function removeRow(ul, row) {
    ul.removeChild(row);
    //find corresponding second line
    var id = row.getAttribute('task_id');
    row.second_line = $('second_line_' + id);
    ul.removeChild(row.second_line);
}

function format_for_sorting(num) {
    num = "0" + num;
    while(num.length < 15) {
	num = "0" + num;
    }
    return num
}

function sortListBy(ul, column, forward, parentID, the_tasks) {
    if( !parentID ) parentID = "0";

    var items = $A(the_tasks).filter( function(i) {
	    return i.getAttribute("parentID") == parentID;
	} );
    
    var hack_for_priority = (column == 'priority');
    var priority_hack_dict = {'High':1, 'Medium':2, 'Low':3, 'None':4};
    for( i = 0; i < items.length; i++ ) {
	var item = items[i];
	var attrib = item.getAttribute(column);
	var sort_index = format_for_sorting(item.getAttribute('sort_index'));
	if( hack_for_priority ) {
	    key = priority_hack_dict[attrib];
	}
	else if( attrib ) {
	    key = attrib;
	} else  {
	    if (forward == 1) {
		key = undefined; //sorts last
	    } else {
		key = 0; // numbers sort before strings
	    }
	}
	items[i] = [key, sort_index, item];
    }

    items = items.sort();  // is there really no way to do a reverse sort?
    if( forward < 0 ) items = items.reverse();

    ul = ul.getElementsByTagName("TBODY")[0];
    for (i = 0; i < items.length; i++) {
	var item = items[i][2];
	items[i] = item;
	removeRow(ul, item);
	$A(item.childTasks).each(function(i) {
		removeRow(ul, i);
	    });
    }
    items.each (function (x) {
	    ul.appendChild(x);
	    ul.appendChild(x.second_line);
	    $A(x.childTasks).each(function(i) {
		    ul.appendChild(i);
		    ul.appendChild(i.second_line);
		});	    
	    if( len_of(x.childTasks) )
		sortListBy($('tasks'), column, forward, x.getAttribute("task_id"), the_tasks);
	});
}

function setCollapse(task_id, val) {
    var node = $('task_' + task_id);
    var button = $('handle_' + task_id);
    var tomatch = val ? "minus.png" : "plus.png";
    if( val ) {
	if( !filterNodeByAllFields(node) ) {
	    node.show();
	    $('second_line_' + task_id).show();
	}
    } else {
	node.hide();
        $('second_line_' + task_id).hide();
    }
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
		setCollapse(node.getAttribute('task_id'), 1);
	    });
    } else if (button.src.match("plus.png")) {
        button.src = button.src.replace("plus.png", "minus.png");
	$A($('task_' + task_id).childTasks).each(function(node) {
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
    var sort_arrows = new Array;
    var columns = ["status", "priority", "owner", "deadline", "updated"];
    for( var i = 0; i < columns.length; ++i ) {
        var arrow = document.getElementById(columns[i] + "-arrows");
        if( arrow ) {
            if( columns[i] == column ) arrow.show();
            else arrow.hide();
        }
    }

    var the_columns = document.getElementById("column-heading").getElementsByTagName("TH");
    for( var i = 0; i < the_columns.length; ++i ) {
        var e = the_columns[i];
        if( e.id == column + "-heading" ) {
            e = e.childNodes[1];
            if( !order )
                order = e.getAttribute('sortOrder') == 'up' ? 'down' : 'up';
            e.setAttribute('sortOrder', order);
            addClass(e, 'selected-column');
	} else {
            e = e.childNodes[1];
	    e.setAttribute('sortOrder', '');
	    removeClass(e, 'selected-column');
	}
    }

    var otherorder = (order == 'up') ? 'down' : 'up';
    addClass($(column + '-' + otherorder + '-arrow'), 'grayed-out');
    removeClass($(column + '-' + order + '-arrow'), "grayed-out");

    setPermalink("sortBy", column);
    setPermalink("sortOrder", order);
    var the_tasks = $('tasks').getElementsByClassName("task-item");

    sortListBy($('tasks'), column, order == 'up' ? 1 : -1, "0", the_tasks);
}

sortBy = safeify(sortBy, "sortBy");
var initialized = false;

function unfold () {
	var other = $('edit_' + this.id);
	other.style['display'] = 'block';
	$(this).hide();
}

function setPermalink(newkey, newval) {
    var a_perm = $('permalink');
    if( !a_perm ) return;
    var permalink = a_perm.getAttribute('permalink');

    function wrapitup() {
	a_perm.setAttribute('permalink', permalink);
	a_perm.href = a_perm.getAttribute("base") + '?' + a_perm.getAttribute("permalink");
	Behavior.applySelectedRule("a.uses_permalink");
    }

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
	    wrapitup();
	    return;
	}
    }
    if( newval == 'All' ) return;
    permalink += ( newkey + "=" + newval + '&' );
    wrapitup();
}

function onBodyClick(event) {
    trigger = Event.element(event);

    //is the trigger in the selected form?

    node = trigger;
    while (node.parentNode) {
	if (node == selected_form) {
	    return; //let this be handled elsewhere.
	}
	node = node.parentNode;
    }

    if (selected_form) {
	selected_form.hide();
	selected_form = null;
	selected_label.show();
	selected_label = null;

    }
}


var column_name_regex = new RegExp("(\\w+)-heading");

function getColumnOrder() {
    var t1 = $('tasks').getElementsByTagName("TR")[0];
    var columns = new Array();
    $A(t1.getElementsByTagName("TH")).each(function (th) {
	colname = column_name_regex.exec(th.id)[1];
	columns.push(colname);
    });
    return columns;
}

function moveSecondNextToFirst(a, b, before) {
    var x = a + '-column';
    var y = b + '-column';
    $A( $('tasks').getElementsByTagName("TR") ).each( function(row) {
            if( hasClass(row, "second-line") ) return;
	    var one = row.getElementsByClassName(x)[0];
	    var two = row.getElementsByClassName(y)[0];
	    if( one && two ) {
		if( before )
		    row.insertBefore(two, one);
		else
		    insertAfter(two, one);
	    }
	});
    /*  this would be good if this was supposed to be a swap.
	var cloneA = one.cloneNode(true);
	var cloneB = two.cloneNode(true);
	row.replaceChild(cloneB, one);
	row.replaceChild(cloneA, two);
    */
}

function moveSecondBeforeFirst(a, b) {
    moveSecondNextToFirst(a, b, true);
}

function moveSecondAfterFirst(a, b) {
    moveSecondNextToFirst(a, b, false);
}

Event.observe (document, 'mousedown', onBodyClick);

addLoadEvent(createDragDrop);
addLoadEvent(setupEmptyList);
addLoadEvent(setTaskParents);

addLoadEvent(sortAndFilter);
