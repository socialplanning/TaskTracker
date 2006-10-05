function changeStatus(url, task_id) {
    new Ajax.Request(url, {asynchronous:true, evalScripts:true, method:'post', parameters:'status=' + $('status_' + task_id).value});
}

function hideCreate() {
    $('create').show();
    $('show_create').hide();
    $('create_anchor').scrollTo();
    return false;
}

mode = 'view';

function resetChildDepths(elem) {

  var children = elem.childNodes;
  var child_ul;
  var i;
  for (i in children) {
    if (children[i].tagName == 'UL') {
      child_ul = $A(children[i].childNodes);
      break;
    }
  }
  if (child_ul.length > 0) {
    //console.log(child_ul);
    var new_depth = parseInt(elem.childNodes[1].getAttribute('depth')) + 1;
    child_ul.each(function(child) {
      if (child.tagName == 'LI') {
	var title = child.childNodes[1];

	title.setAttribute('depth', new_depth);
	left = new_depth * 15;
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

observer.prototype={

    element: null,
    initialize : function() {

    },
    onStart : function(event_name, handle) {
	Droppables.remove (handle.handle);
    },
    onEnd : function(event_name, handle) {
	Droppables.add (handle.handle.id, {
		hoverclass : 'drop',
		onDrop : doDrop
	    });
    }
};

function doDrop(child, drop_target) {
 
  var id;

  if (drop_target == child) {
      return;
  }

  if (drop_target.id.match(/^title_/)) {
      id = parseInt(drop_target.id.replace(/^title_/, ''));
      var new_parent = $('task_' + id);
      //find new parent's contained ul
      var kids = new_parent.childNodes;
      for (i in kids) {
	  if (kids[i].tagName == 'UL') {
	      var ul = kids[i];
	      ul.insertBefore(child, ul.childNodes[0]);
	      //update sort_index
	      items = $A(ul.childNodes);
	      for (j in items) {
		  if (items[j].tagName == 'LI') {
		      sort_index = parseInt(items[j].getAttribute('sort_index'));
		      items[j].setAttribute('sort_index', sort_index + 1);
		  }
	      }	      

	      sort_index = parseInt(items[0].getAttribute('sort_index'));
	      items[0].setAttribute('sort_index', 0);

	      //set child indent
	      resetChildDepths(new_parent);
	      new Ajax.Request('/task/move/' + child.getAttribute('task_id') + '?new_parent=' + new_parent.getAttribute('task_id'), {asynchronous:true, evalScripts:true}); 
	      return;
	  }
      }
  } else {
      id = parseInt(drop_target.id.replace(/^handle_/, ''));
      var new_sibling = $('task_' + id);

      insertAfter(child, new_sibling);

      new_index = parseInt(new_sibling.getAttribute('sort_index'));

      var ul = child.parentNode;

      //update sort_index
      items = $A(ul.childNodes);
      for (j in items) {
	  if (items[j].tagName == 'LI') {
	      sort_index = parseInt(items[j].getAttribute('sort_index'));
	      if (items[j] == child) {
		  items[j].setAttribute('sort_index', new_index + 1);
	      } else if (sort_index > new_index) {
		  items[j].setAttribute('sort_index', sort_index + 1);
	      }
	  }
      }	      

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
      new Ajax.Request('/task/move/' + child.getAttribute('task_id') + '?new_sibling=' + new_sibling.getAttribute('task_id'), {asynchronous:true, evalScripts:true}); 

  }
}

function sortULBy(ul, column) {
    items = $A(ul.childNodes);
    items = items.findAll(function(x) {
	    return x.tagName == "LI"
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


function sortBy(column) {
    sortULBy($('tasks'), column)
}

var initialized = false;

function modeSwitch() {
    $A($('tasks').getElementsByTagName('span')).each(function(node) {
	    if (node.id.match('^(status-form|label)')) {
		node.toggle();
	    }
	});

    if (!initialized) {
      initialized = true;
      Draggables.addObserver(new observer());

      $A($('tasks').getElementsByTagName('li')).each(function(node) {
	  id = node.getAttribute('task_id');
	  drag = new Draggable(node.id, {
	      handle : 'handle_' + id, 
	      revert : true,
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
