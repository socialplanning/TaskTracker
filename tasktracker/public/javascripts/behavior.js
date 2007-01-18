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

var Behavior = {
    rules : [],
    apply : function () {
	Behavior.rules.each (function (ruleset) {
		$H(ruleset).each(function (rule) {
			if (rule instanceof Function)
			    return;

			elements = $$(rule);
			elements.each (function (element) {
				ruleset[rule] (element)
			    });
		    });
	    });
    },

    register : function (rules) {
	this.rules.push(rules);
    },

    init : function () {
	Event.observe (window, 'load', Behavior.apply);
    }
};


Behavior.init();
