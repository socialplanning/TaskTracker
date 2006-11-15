
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

import formencode
import datetime, time
from formencode.validators import *
from formencode.api import * 

# -----
#from TurboGears:

#Copyright (c) 2005, 2006 Kevin Dangoor and contributors. TurboGears
#is a trademark of Kevin Dangoor.

#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the
#"Software"), to deal in the Software without restriction, including
#without limitation the rights to use, copy, modify, merge, publish,
#distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so, subject to
#the following conditions:

#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

class DateTimeConverter(FancyValidator):

    """
    Converts Python date and datetime objects into string representation and back.
    """
    messages = {
        'badFormat': 'Invalid datetime format',
        'empty': 'Empty values not allowed',
    }

    def __init__(self, format = "%m/%d/%Y %H:%M:%S", allow_empty = None,
                *args, **kwargs):
        if allow_empty is not None:
            warnings.warn("Use not_empty instead of allow_empty",
                          DeprecationWarning, 2)
            not_empty = not allow_empty
            kw["not_empty"] = not_empty
        super(FancyValidator, self).__init__(*args, **kwargs)
        self.format = format

    def _to_python(self, value, state):
        """ parse a string and return a datetime object. """

        if (not self.not_empty) and value and not (value.get('date', None)) and not(value.get('time',None)):
            return ''

        if value and isinstance(value, datetime.datetime):
            return value
        else:
            try:
                value = value['date'] + ' ' + (value['time'] or '17:00:00')
                tpl = time.strptime(value, self.format)
            except ValueError:
                raise Invalid(self.message('badFormat', state), value, state)
            # shoudn't use time.mktime() because it can give OverflowError,
            # depending on the date (e.g. pre 1970) and underlying C library
            return datetime.datetime(year=tpl.tm_year, month=tpl.tm_mon, day=tpl.tm_mday,
                    hour=tpl.tm_hour, minute=tpl.tm_min, second=tpl.tm_sec)

    def _from_python(self, value, state):
        if not value:
            return None
        elif isinstance(value, datetime):
            # Python stdlib can only handle dates with year greater than 1900
            if value.year <= 1900:
                thestr = strftime_before1900(value, self.format)
            else:
                thestr = value.strftime(self.format)
            out = {}
            out['date'], out['time'] = thestr.split(" ")
            return out
        else:
            return value
# -----
