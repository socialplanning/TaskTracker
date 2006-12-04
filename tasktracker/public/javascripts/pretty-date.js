// WARNING: this file must be kept in sync with tasktracker/lib/pretty_date.py

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


function utc(d) {
    return Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
}

function date_diff(date1, date2) {
    var date1_UTC = utc(date1);
    var date2_UTC = utc(date2);
    return (date1_UTC - date2_UTC) / 86400000;
}

function dayOfWeek(day) {
    return "SunMonTueWedThuFriSatSun".substr(day * 3, 3);
}

function monthName(month) {
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    return months[month];
}


function pretty_date_engine(now, date) {
    var diff = date_diff(date, now);
    if (diff == -1) {
	return "Yesterday";
    }
    if (diff == 0) {
	return "Today";
    }
    if (diff == 1) {
	return "Tomorrow";
    }
    if (diff < 7 && diff > 0) {
	return dayOfWeek(date.getDay());
    }
    if (diff < 90 && date.getYear() == now.getYear()) {
	return monthName(date.getMonth()) + " " + date.getDate()
    }
    return monthName(date.getMonth()) + " " + date.getDate() + ", " + date.getFullYear();
}

function pretty_date_from_text(text) {
    parts = text.split("/");
    return pretty_date(new Date(parseInt(parts[2]), parseInt(parts[0])-1, parseInt(parts[1])));
}

function pretty_date(date) {
    var now = new Date();
    return pretty_date_engine(now, date);
}


function test_pretty_date() {
    var now = new Date(2006, 0, 1);
    var dates = {
	'Today' : new Date(2006, 0, 1),
	'Tomorrow' : new Date(2006, 0, 2),
	'Yesterday' : new Date(2005, 11, 31),
	'December 30, 2005' : new Date(2005, 11, 30),
	'Tue' : new Date(2006, 0, 3),
	'Sat' : new Date(2006, 0, 7),
	'January 8' : new Date(2006, 0, 8),
	'December 8, 2006' : new Date(2006, 11, 8),
	'January 8, 2007' : new Date(2007, 0, 8)
    };

    for (date in dates) {
	var pd = pretty_date_engine(now, dates[date]);
	if (pd != date) {
	    alert("failure mapping " + dates[date] + " to " + date + ", got " + pd);
	    break;
	}
    }
}
