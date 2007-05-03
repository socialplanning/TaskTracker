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

function getElementsBySelector(parent, selector_string) {
    /*
      Things this does:
       S: [E].c
       S: [E]#t
       S: S S

      Things this does not do:
       everything else. most notably, standalone tagname and comma-separated lists of selectors and .class.otherclass

      Things to do with this:
       S: E
       S: S, S
       S: S.c
       optimization -- currently always searches by tagname first. this is definitely stupid in the case of tagname=* 
        and may be generally stupid; it seems likely that search-by-tagname will give the most results and should come last.
    */

    var selectors = selector_string.split(" ");
    var i;
    var search_in = [parent];
    var found = false;
    for( i = 0; i < selectors.length; ++i ) {
	var selector = selectors[i];
	var thisTry;

	thisTry = selector.split("#");
	if( thisTry.length > 1 ) {
	    var j;
	    var tagname = thisTry[0];
	    var sel = thisTry[1];
	    var els = [];
	    for( j = 0; j < search_in.length; ++j ) {
		els[els.length] = $A( search_in[j].getElementsByTagName(tagname || '*') ).filter( function(el) { return el.id == sel; } );
	    }
	    search_in = els.flatten();
	    found = true;
	    continue;
	} 

	thisTry = selector.split(".");
	if( thisTry.length > 1 ) {
	    var j;
	    var tagname = thisTry[0];
	    var sel = thisTry[1];
	    var els = [];
	    for( j = 0; j < search_in.length; ++j ) {
		els[els.length] = $A( search_in[j].getElementsByTagName(tagname || '*') ).filter( function(el) { return hasClass(el, sel); } );
	    }
	    search_in = els.flatten();
	    found = true;
	    continue;
	} 

    }
    return found ? search_in : [];
}

var Behavior = {
    rules : [],
    apply : function () {
	var i;
	for( i = 0; i < Behavior.rules.length; ++i ) {
	    var ruleset = Behavior.rules[i];
	    var rule;
	    for( rule in ruleset ) {
		if( rule instanceof Function )
		    continue;
		var elements = getElementsBySelector(document, rule);
		elements.each(ruleset[rule]);
	    }
	}
    },

    applySelectedRule : function (selector) {
	var i;
	for( i = 0; i < Behavior.rules.length; ++i ) {
	    var ruleset = Behavior.rules[i];
	    var rule = ruleset[selector];
	    if( !rule || !(rule instanceof Function) )
		continue;
	    var elements = getElementsBySelector(document, selector);
	    elements.each(rule);
	}
    },
    
    register : function (rules) {
	Behavior.rules.push( rules );
    },

    init : function () {
	Event.observe (window, 'load', Behavior.apply);
    }
};

Behavior.init();