function toggle(obj) {
    obj.style.display = (obj.style.display != 'none' ? 'none' : '');
}

function changeField(url, task_id, fieldname) {
    var field = $(fieldname + '_' + task_id);
    console.log('changed: ', fieldname);
    field.disabled = true;
    var req = new Ajax.Request(url, {asynchronous:true, evalScripts:true, method:'post', parameters:fieldname + '=' + field.value,
				     onSuccess:doneChangingField.bind([task_id, fieldname]), onFailure:failedChangingField.bind([task_id, fieldname])});
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

function doneChangingField(req) {
    var task_id = this[0];
    var fieldname = this[1];
    var field = $(fieldname + '_' + task_id);
    field.setAttribute('originalvalue', field.selectedIndex);
    field.disabled = false;
    field.style.color = "black"; 
    var node = $('label_' + task_id);
    var newfield = $(fieldname + '_' + task_id).getValue(field.selectedIndex);
    node.innerHTML = newfield;
    $('task_' + task_id).setAttribute(fieldname, newfield);
    updateTaskItem(task_id);
}

function failedChangingField(req) {
    var task_id = this[0];
    var fieldname = this[1];
    var field = $(fieldname + '_' + task_id);
    var orig = field.getAttribute('originalvalue');
    field.style.color = "red";
    field.disabled = false;
    field.selectedIndex = orig;
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
                var left = new_depth * 15;
                title.style.paddingLeft = left + 'px'; 
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

    onStart : function(event_name, handle) {
        Droppables.remove (handle.handle);
    },

    onEnd : function(event_name, handle, event) {
        Droppables.add (handle.handle.id, {
            hoverclass : 'drop',
            onDrop : doDrop
        });	
        // TODO consume the event so it doesn't trigger a click on mouse-up
    }
};

function debugThing() { 
    console.log("FAILED");
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
        title.style.paddingLeft = '0px'; 
        resetChildDepths(child);
    }
}

function insertTaskUnderParent(child_id, parent_id) {
    var child = $('task_' + child_id);
    var new_parent = $('task_' + parent_id);

    //find new parent's contained ul
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
        title.style.paddingLeft = (parentdepth + 1) * 15 + 'px'; 

        resetChildDepths(child);
        return;
    }
}

function doneDestroyingTask(req) {
    var task_id = this;
    $('task_' + task_id).remove();
}

function failedDestroyingTask(req) {
    console.log("Failed to destroy the task " + this);
    var task_id = this;
    $('task_' + task_id).show();    
}

function destroyTask(child, drop_target) {
    var task_id = child.getAttribute('task_id');
    $('task_' + task_id).hide();
    var req = new Ajax.Request('/task/destroy/' + task_id, {asynchronous:true, evalScripts:true, method:'post',
        onSuccess:doneDestroyingTask.bind(task_id), onFailure:failedDestroyingTask.bind(task_id)});
}

function doDrop(child, drop_target) {
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
    $A($('task_' + task_id).childNodes).each(function(node) {        
        if (node.className) {
            if (node.className.match('^task_list')) {
                toggle(node);
            }
        }
    });
    var button = $('collapseButton_' + task_id);
    var handle = $('handle_' + task_id);
    if (button.src.match("minus.png")) {
        button.src = button.src.replace("minus.png", "plus.png");
        handle.src = handle.src.replace("closed.png", "open.png");
    } else if (button.src.match("plus.png")) {
        button.src = button.src.replace("plus.png", "minus.png");
        handle.src = handle.src.replace("open.png", "closed.png");
    }
}

function expandTask(task_id) {
    var collapse = $('collapseButton_' + task_id);
    var handle = $('handle_' + task_id);
    if (collapse.src.match("blank.png")) {
        collapse.src = collapse.src.replace("blank.png", "plus.png");
        handle.src = handle.src.replace("file.png", "folder_open.png");
    } else if (collapse.src.match("minus.png")) {
        toggleCollapse(task_id);
    }
}

function flattenTask(task_id) {
    var collapse = $('collapseButton_' + task_id);
    var handle = $('handle_' + task_id);
    collapse.src = collapse.src.replace(/(plus|minus).png$/, "blank.png");
    handle.src = handle.src.replace(/folder_(open|closed).png/, "file.png");
}

function sortBy(column) {
    sortULBy($('tasks'), column);
}

var initialized = false;

function modeSwitch() {
    $A($('tasks').getElementsByTagName('span')).each(function(node) {
        if (node.id.match('^(label)')) {
            var id = node.id.split('_')[1];
            toggle(node);
        }
        else if (node.id.match('^status-form')) {
            toggle(node);
        }
    });

    if (!initialized) {
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
        Droppables.add('trash', {
            hoverclass : 'drop',
            onDrop : destroyTask,
            accept : 'deletable'
        });
    }


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
