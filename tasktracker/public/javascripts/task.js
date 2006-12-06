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

function addClass(element, classname) {
    element.className += element.className ? ' ' + classname : classname;
}

function removeClass(element, classname) {
    var removeMe = element.className.match(' ' + classname) ? ' ' + classname : classname;
    element.className = element.className.replace(removeMe, '');
}

function hasClass(element, classname) {
    return new RegExp('\\b' + classname + '\\b').test(element.className);
}

var myrules = {
    '.draggable' : function(element) {
	var drag = new Draggable(element.id, {
                handle : element.id, 
                revert : true
            });

	element.onclick = function(e) {
	    e = e || event 
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
    var parser = document.createElement("DIV");
    var html = document.createDocumentFragment();
    
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

function setupEmptyList() {
    if ($('tasks') && !($('tasks').getElementsByTagName('li').length))
	hideCreate();
}

addLoadEvent(createDragDrop);
addLoadEvent(setupEmptyList);

function toggle(obj) {
    obj.style.display = (obj.style.display != 'none' ? 'none' : '');
}

function filterDeadline() {
    var filtervalue = $('deadline_filter').value;

    if (filtervalue == 'All') {
	return;
    }
    if (filtervalue == 'None') {
	$A($('tasks').getElementsByTagName('li')).each(function(node) {
		if (node.getAttribute('deadline'))
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
		if (!(nodeDate < byThisDate)) {
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
    $A($('tasks').getElementsByTagName('li')).each(function(node) {
	    if (node.getAttribute(fieldname) != filtervalue) {
		node.hide();
	    }
	});
}

function filterListByAllFields() {
    $A($('tasks').getElementsByTagName('li')).each(function(node) {
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
    document.forms[0].getInputs()[1].setAttribute("value", 0);
    document.forms[0].getInputs()[2].setAttribute("value", 0);
    return false;
}

function doneAddingTask(req) {
    var parentID = parseInt(document.forms[0].getInputs()[1].getAttribute("value"));
    var siblingID = parseInt(document.forms[0].getInputs()[2].getAttribute("value"));
    if (siblingID != 0) {
	var sibling = $('task_' + siblingID);
	insertAfter(evalHTML(req.responseText), sibling);
    } else if (parentID != 0) {
	var parent = $('task_' + parentID);
	var ul = parent.getElementsByTagName("ul")[0];
	ul.insertBefore(evalHTML(req.responseText), ul.childNodes[0]);
	//	ul.appendChild(evalHTML(req.responseText));
	updateTaskItem(parentID);
	$('movable_add_task').parentNode.appendChild($('movable_add_task'));
    } else {
	var ul = $('tasks');
	evalHTML(req.responseText);
	ul.appendChild(evalHTML(req.responseText));
    }
    
    $('num_uncompleted').innerHTML = parseInt($('num_uncompleted').innerHTML) + 1;

    var id = parseInt(req.responseText.match(/task_id="\d+"/)[0].replace('task_id="', ''));

    Droppables.add('title_' + id, {hoverclass:'drop', onDrop:doDrop});
    Droppables.add('handle_' + id, {hoverclass:'drop', onDrop:doDrop});
    Behaviour.apply();
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
    var completed = (taskitem.getAttribute('status') == 'done') ? 'completed-task' : 'uncompleted-task';
    var root;
    if (taskitem.childNodes[1].nodeType == 1) {
	root = (parseInt(taskitem.childNodes[1].getAttribute('depth')) === 0) ? 'root-task' : 'sub-task';
    } else {
	root = 'root-task';
    }
    tasktext.setAttribute('class', completed + ' ' + root);  // TODO MAKE THIS USE ADDCLASS
    if( taskitem.getElementsByTagName("UL")[0].getElementsByTagName("LI").length ) {
	expandTask(task_id);
    } else {
	flattenTask(task_id);
    }
    var uncompletedTasks = 0;
    $A(document.getElementsByTagName("li")).each(function(task) {
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
    //    $('create_anchor').scrollTo();
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
	addClass(draggable.handle, 'drag');
    },

    onEnd : function(event_name, draggable, event) {
        Droppables.add (draggable.handle.id, {
            hoverclass : 'drop',
            onDrop : doDrop
        });
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
    target.style.marginLeft = 15*depth + 'px'; 
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
    // if it's "add a task" element
    if (!child.id.match("draggable")) {  // TODO be more specific
	if (drop_target.id.match(/^title_/)) {   // drop under a parent node
	    id = parseInt(drop_target.id.replace(/^title_/, ''));
	    document.forms[0].getInputs()[1].setAttribute("value", id);
	    document.forms[0].getInputs()[2].setAttribute("value", 0);
	    var new_parent = $('task_' + id);
	    var ul = new_parent.getElementsByTagName("ul")[0];
	    var li = document.createElement("li");
	    li.className = "taskrow";
	    li.appendChild(child);
	    ul.insertBefore(li, ul.childNodes[0]);
	} else {   // drop after a sibling node
	    id = parseInt(drop_target.id.replace(/^handle_/, ''));
	    document.forms[0].getInputs()[1].setAttribute("value", 0);
	    document.forms[0].getInputs()[2].setAttribute("value", id);
	    var new_sibling = $('task_' + id);
	    var ul = new_sibling.parentNode;
	    var li = document.createElement("li");
	    li.className = "taskrow";
	    li.appendChild(child);
	    insertAfter(child, new_sibling);
	}
	return;
    }
    var task_id = child.id.replace("draggable_", "");
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

function sortULBy(ul, column, forward) {
    items = $A(ul.childNodes);
    items = items.findAll(function(x) {
	    return x.tagName == "LI";
	});

    items = items.sort(function (x, y) {
	    a = x.getAttribute(column);
	    b = y.getAttribute(column);
	    console.log(a, b, a > b, a < b);
	    if (a > b) 
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
    });
}

function toggleCollapse(task_id) {
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
	
    sortULBy($('tasks'), column, order == 'up' ? 1 : -1);
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

