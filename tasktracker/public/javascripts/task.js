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
	after.parentNode.append(new_node);
    }

}

function drop(child, drop_target) {
 
  var id;

  if (drop_target.id.match(/^title_/)) {
      id = parseInt(drop_target.id.replace(/^title_/, ''));
      var new_parent = $('task_' + id);
      //find new parent's contained ul
      var kids = new_parent.childNodes;
      for (i in kids) {
	  if (kids[i].tagName == 'UL') {
	      kids[i].insertBefore(child, kids[i].childNodes[0]);
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
	  Droppables.add('handle_' + id, {
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
