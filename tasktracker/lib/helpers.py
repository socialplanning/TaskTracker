"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.util import _, log, set_lang, get_lang
from routes import url_for

def oppositeStatus(status):
    if status == 'completed':
        return 'uncompleted'
    else:
        return 'completed'
