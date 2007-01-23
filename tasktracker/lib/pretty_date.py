# WARNING: this file must be kept in sync with tasktracker/public/javascripts/pretty-date.js

# Copyright (C) 2006 The Open Planning Project

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 
# 51 Franklin Street, Fifth Floor, 
# Boston, MA  02110-1301
# USA

from datetime import date

def _date_diff(date1, date2):
    return (date1.toordinal() - date2.toordinal())


def _pretty_date_engine(now, date):
    diff = _date_diff(date, now)
    if (diff == -1):
	return "Yesterday"
    
    if (diff == 0):
	return "Today"
    
    if (diff == 1):
	return "Tomorrow"
    
    if (diff < 7 and diff > 0):
	return date.strftime("%A")
    
    if (diff < 90 and date.year == now.year):
	return date.strftime("%B %e")
    
    return date.strftime("%B %e, %Y")


def prettyDate(date):
    now = date.today()
    return _pretty_date_engine(now, date)




