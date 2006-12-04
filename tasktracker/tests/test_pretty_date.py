
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

from tasktracker.lib.pretty_date import _pretty_date_engine
from datetime import date

class TestPrettyDate:
    def test_pretty_date(self):
        now = date(2006, 1, 1)
        dates = {
            'Today' : date(2006, 1, 1),
            'Tomorrow' : date(2006, 1, 2),
            'Yesterday' : date(2005, 12, 31),
            'Tue' : date(2006, 1, 3),
            'Sat' : date(2006, 1, 7),
            'January  8' : date(2006, 1, 8),
            'December  8, 2006' : date(2006, 12, 8),
            'January  8, 2007' : date(2007, 1, 8)
            }

        for d in dates:
            pd = _pretty_date_engine(now, dates[d])
            assert pd == d
