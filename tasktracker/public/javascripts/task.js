function changeStatus(url, task_id) {
    //    url += "?status=" + $('status_' + task_id).value;

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
function drop(child, drop_target) {
  var new_parent = drop_target.parentNode.parentNode.parentNode;

  //find new parent's contained ul
  var kids = new_parent.childNodes;
  for (i in kids) {
    if (kids[i].tagName == 'UL') {
      kids[i].insertBefore(child, kids[i].childNodes[0]);
      //set child indent
      resetChildDepths(new_parent);
     
      //tell the server
      new Ajax.Request('/task/move/' + child.getAttribute('task_id') + '?new_parent=' + new_parent.getAttribute('task_id'), {asynchronous:true, evalScripts:true}); 
      return;
    }
  }
}

var initialized = false;

function modeSwitch() {
    $A($('tasks').getElementsByTagName('span')).each(function(node) {
	    if (node.id.match('^(status-form|handle|label)')) {
		node.toggle();
	    }
	});

    if (!initialized) {
      initialized = true;
      $A($('tasks').getElementsByTagName('li')).each(function(node) {
	  id = node.getAttribute('task_id');
	  new Draggable(node.id, {
	      handle : 'handle_' + id, 
	      revert : true,
	      ghosting : true
          });
	
	  Droppables.add('title_' + id, {
	      hoverclass : 'drop',
	      onDrop : drop
	  });
       });
    }


    if (mode == 'view') {
	mode = 'reorder';
	$('modeName').innerHTML = 'Done reordering';
	$('create_section').hide();
    } else {
	mode = 'view';
	$('modeName').innerHTML = 'Reorder';
	$('create_section').show();
    }
}
