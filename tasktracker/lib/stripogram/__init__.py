
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

# Copyright (c) 2001 Chris Withers
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
#
# $Id: __init__.py,v 1.11 2003/01/07 10:57:21 fresh Exp $

from html2text import HTML2Text
from html2safehtml import HTML2SafeHTML

def html2text(s, ignore_tags=(), indent_width=4, page_width=80):
    ignore_tags = [t.lower() for t in ignore_tags]
    parser = HTML2Text(ignore_tags, indent_width, page_width)
    parser.feed(s)
    parser.close()
    parser.generate()
    return parser.result

def html2safehtml(s, valid_tags=('b', 'a', 'i', 'br', 'p', 'em', 'strong')):
    valid_tags = [t.lower() for t in valid_tags]
    parser = HTML2SafeHTML(valid_tags)
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result

try:
    from AccessControl import ModuleSecurityInfo
except ImportError:
    # no Zope around
    pass
except AttributeError, e:
    # Something else is weird
    import warnings
    warnings.warn("Cannot import AccessControl: %s" % e)
else:
    ModuleSecurityInfo('Products.stripogram').declareObjectPublic()
    ModuleSecurityInfo('Products.stripogram').declarePublic('html2text', 'html2safehtml')
