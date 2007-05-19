# Copyright (C) 2006-2007 The Open Planning Project

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

#datebocks helper ported from ruby by David Turner <novalis@gnu.org>
#w/modifications by Ethan Jucovy <ejucovy@openplans.org>

#include CalendarHelper

# options
# 
#    prop. name               | description
#  -------------------------------------------------------------------------------------------------
#   dateType                  | the format to display the date (iso, de, us, dd/mm/yyyy, dd-mm-yyyy, mm/dd/yyyy, mm.dd.yyyy, yyyy-mm-dd)
#   calendarAlign             | where to align the calendar (can also be set in the calendar_options) (Ex: Br, Bl, Tl, Tr) 
#   messageSpanSuffix         | default is 'Msg'
#   messageSpanErrorClass     | default is 'error'
#   messageSpanSuccessClass   | default is ''

# calendar_options
# 
# To use javascript code as a value, prefix with "javascript:"
# 
#    prop. name   | description
#  -------------------------------------------------------------------------------------------------
#   inputField    | the ID of an input field to store the date
#   displayArea   | the ID of a DIV or other element to show the date
#   button        | ID of a button or other element that will trigger the calendar
#   eventName     | event that will trigger the calendar, without the "on" prefix (default: "click")
#   ifFormat      | date format that will be stored in the input field
#   daFormat      | the date format that will be used to display the date in displayArea
#   singleClick   | (true/false) wether the calendar is in single click mode or not (default: true)
#   firstDay      | numeric: 0 to 6.  "0" means display Sunday first, "1" means display Monday first, etc.
#   align         | alignment (default: "Br"); if you don't know what's this see the calendar documentation
#   range         | array with 2 elements.  Default: [1900, 2999] -- the range of years available
#   weekNumbers   | (true/false) if it's true (default) the calendar will display week numbers
#   flat          | null or element ID; if not null the calendar will be a flat calendar having the parent with the given ID
#   flatCallback  | function that receives a JS Date object and returns an URL to point the browser to (for flat calendar)
#   disableFunc   | function that receives a JS Date object and should return true if that date has to be disabled in the calendar
#   onSelect      | function that gets called when a date is selected.  You don't _have_ to supply this (the default is generally okay)
#   onClose       | function that gets called when the calendar is closed.  [default]
#   onUpdate      | function that gets called after the date is updated in the input field.  Receives a reference to the calendar.
#   date          | the date that the calendar will be initially displayed to
#   showsTime     | default: false; if true the calendar will include a time selector
#   timeFormat    | the time format; can be "12" or "24", default is "12"
#   electric      | if true (default) then given fields/date areas are updated for each move; otherwise they're updated only on close
#   step          | configures the step of the years in drop-down boxes; default: 2
#   position      | configures the calendar absolute position; default: null
#   cache         | if "true" (but default: "false") it will reuse the same calendar object, where possible
#   showOthers    | if "true" (but default: "false") it will show days from other months too

from webhelpers.rails import *
from tasktracker.lib.base import c

def options_for_javascript(dict):
    items = []
    for k, v in dict.items():
        items.append('%s : %s' % (k, v))
    return '{%s}' % ",".join(items)

def datebocks_field(object_name, field_name, options = None, calendar_options = None, attributes = None, input_attributes = None, value = None):
    if options is None:
        options = dict()

    if calendar_options is None:
        calendar_options = dict()

    if attributes is None:
        attributes = dict()

    if input_attributes is None:
        input_attributes = dict()
        
    attribute_str = str()
    keys = attributes.keys()
    if 'class' in keys:
        attributes['class'] = '%s dateBocks' % attributes['class']
    else:
        attributes['class'] = 'dateBocks'
    if not 'id' in keys:
        attributes['id'] = 'dateBocks'

    try:
        task_id = int(attributes['id'].split('_')[1])
    except:
        task_id = 0

    keys = attributes.keys()
    for key in keys:
        if key != 'id':
            attribute_str = attribute_str + '%s="%s" ' % (key, attributes[key])

    calendar_ref = attributes['id']
    if not options.has_key('name'):
        options['name'] =  calendar_ref

    options['dateBocksElementId'] = "'%s'" % calendar_ref
    datebocks_options = dict(options)
    del datebocks_options['name']

    calendar_options['inputField']     = "'%s'" % calendar_ref                          # id of the input field
    calendar_options['button']         = "'%sButton'" % calendar_ref               # trigger for the calendar (button ID)
    calendar_options['help']           = "'%sHelp'" % calendar_ref                # trigger for the help menu

    if not calendar_options.has_key('ifFormat'):
        calendar_options['ifFormat']     = calendar_ref + 'Obj.calendarIfFormat' # format of the input field

    if not calendar_options.has_key('align'):
        calendar_options['align']        = calendar_ref + 'Obj.calendarAlign'    # alignment (defaults to "Bl")

    if not calendar_options.has_key('singleClick'):
        calendar_options['singleClick']  = 'true'

    if not value:
        obj = getattr(c, object_name, None)
        if obj:
            value = getattr(obj, field_name, None)
        else:
            value =  None

    if value:
        value = value.strftime("%m-%d-%Y")
    
    retval = "".join(["""
    <span """, attribute_str, """>
      <script type="text/javascript">
        var """, calendar_ref, """Obj = new DateBocks(
          """, options_for_javascript(datebocks_options), """
        );
      </script>
      <span>
        <span class="dateBocksInput">""",
                      text_field(options['name'], 
                                 value=value, 
                                 id=calendar_ref, 
                                 onChange=calendar_ref + "Obj.magicDate();",
                                 onKeyPress=calendar_ref + "Obj.keyObserver(event, 'parse'); return " + calendar_ref + "Obj.keyObserver(event, 'return');", 
                                 onClick="this.select();", **input_attributes), """</span>
        <span class="dateBocksIcon">""", image_tag('icon-calendar.gif', alt='Calendar', id=calendar_ref + 'Button', style = 'cursor: pointer;'), """</span>
        <span class="dateBocksHelp">""", image_tag('icon-help.gif', alt='Help', id=calendar_ref + 'Help', style = 'cursor: pointer' ), """</span>
      </span>
      <!-- div id=\"""", calendar_ref, """Message" style="display:none"><div id=\"""", calendar_ref, """Msg"></div></div -->
      <script type="text/javascript">
        Calendar.setup(""",options_for_javascript(calendar_options), """);        
      </script>
    </span>"""])
    
    return retval
