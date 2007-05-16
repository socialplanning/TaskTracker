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

function updateItem(list) {
    //update the form variable
    list = $(list);
    var items = list.getElementsByTagName('li')
    $(list.getAttribute('field')).value = $A(items).map(getItemName).join(",");
}

function deleteItem(item_name) {
    var list = $(item_name).parentNode;
    $(item_name).remove();
    updateItem(list);
}

function getItemName(item_li) {
    return item_li.getElementsByTagName('span')[0].childNodes[0].nodeValue;
}

function addItem(list, item) {
    item = item.replace(/[,&<>?=\000-\017"']/g, '');
 
    if( item.length < 1 ) {
        return;
    }

    //prevent duplication

    var item_list = $(list);
    var items = item_list.getElementsByTagName('li');

    for( var i = 0; i < items.length; ++i ) {
        if( getItemName(items[i]) == item ) {
            return;
        }
    } 

    //add the html element

    var item_name =  + list + "_" + 'item_' + items.length;
    var li = Builder.node('li', {className : "removable_list_item"}, [Builder.node('span', item)]);
    var last_item = item_list.firstChild;
    while( last_item.nextSibling ) {
	last_item = last_item.nextSibling;
    }
    item_list.insertBefore(li, last_item);

    li.appendChild( Builder.node('span', {className : "command delete_button"}, '[ - ]') );
    Behavior.applySelectedRule('li.removable_list_item .delete_button');

    updateItem(list);
}

var myrules = {
    'li.removable_list_item .delete_button' : function(element) {
	element.onclick = function() {
	    deleteItem(element.parentNode);
	}
    }
};

Behavior.register(myrules);