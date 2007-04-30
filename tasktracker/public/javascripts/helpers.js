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

// no-op logging for IE:
if (typeof console == 'undefined') {
    console = {log: function (msg) {}};
}

function safeify(func, name) {
      return function () {
          try {
              return func.apply(this, arguments);
          } catch (e) {
              console.log('Error in ' + (name || func) + ' at ' + e.lineNumber + ': ' + e);
              return null;
          }
      }
 }

function find(thing, item) {
    if( len_of(thing) ) {
	var i;
	for( i = 0; i < thing.length; i++ )
	    if( thing[i] == item )
		return i;
    }
    return -1;
}

function insertBeforeInList(thing, newitem, olditem) {
    if( len_of(thing) ) {
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
    if( len_of(thing) ) {
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
    var re = new RegExp('\\b' + classname + '\\b');
    element.className = element.className.replace(re, '').trim().replace("  ", " ")
}

function hasClass(element, classname) {
    return new RegExp('\\b' + classname + '\\b').test(element.className);
}

function toggleClass(element, classname) {
    if( hasClass(element, classname) )
	removeClass(element, classname);
    else
	addClass(element, classname);
}

function len_of(thing) {
    return (thing && thing.length ? thing.length : 0);
}

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

function toggle(obj) {
    if( obj.style.display == 'none' ) {
	obj.style.display = obj.getAttribute('desired_display');
    } else {
	obj.setAttribute('desired_display', obj.style.display);
	obj.style.display = 'none';
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