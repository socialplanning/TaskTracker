
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

from pylons import g

import uuid
from logging import error
import atomixlib
import urllib
from atomixlib.mapper import *
import httplib2
h = httplib2.Http()
from utils import threaded
from threading import Lock
import datetime

#next three functions adapted from amplee demo
def build_url(base_uri, collection, resource_name=None):
    if resource_name:
        return "%s/%s/%s" % (base_uri, collection, urllib.quote(resource_name))
    return "%s/%s/" % (base_uri, collection)

def headers():
    mime_type = 'application/atom+xml'
    headers={'Content-Type': mime_type,
             'Connection': 'close'}
    return headers

def do_create_resource(base_uri, collection, entry):
    url = build_url(base_uri, collection)
    body = atomixlib.s_entry(entry)
    r, c = h.request(url, method='POST', body=body, headers=headers())

    return c

def do_update_resource(base_uri, collection, resource_name, entry):
    url = build_url(base_uri, collection, resource_name)
    body = atomixlib.s_entry(entry)
    r, c = h.request(url, method='PUT', body=body, headers=headers())

    return c

def task_diff(before, after):
    items = []
    for attribute in "deadline owner priority status text title".split():
        after_attribute = getattr(after, attribute)
        if getattr(before, attribute) != after_attribute:
            items.append ("%s was changed to %s" % (attribute, after_attribute))

    return ", ". join(items)

class AtomStoreLink(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.recent_entries = {}
        self.reaper()
        self.lock = Lock()

    @threaded()
    def reaper(self):
        while 1:
            import time
            time.sleep(60)
            self.lock.acquire()
            try:
                for key in self.recent_entries.keys():
                    if self.recent_entries[key].updated.value + datetime.timedelta(0, 30*60, 0) < datetime.datetime.now() :
                        del self.recent_entries[key]
            finally:
                self.lock.release()
    
    def _create_task_entry(self, task):
        text = u" ".join(["<div>",
                          "Title: <em>%s</em><br/>" % task.title,
                          "Created on %s" % task.created,
                          "</div>",
                          ])

        entry = Entry()
        entry.id = ID(u'urn:uuid:%s' % uuid.uuid4())
        entry.title = PlainTextTitle(unicode("%s #%d") % (task.title, task.id))
        entry.author = unicode(task.owner)
        entry.content = HTMLContent(text)
        return entry

    def _handle_request(self, c, task):
        if not c.startswith("<"):
            #it's too late now to do anything except log the error.
            from warnings import warn
            warn ("Failed to store atom entry for update of task %s (id %d): %s" % (task.title, task.id, c))
            return False
        return c

    def _create_and_send_task_entry(self, task):
        entry = self._create_task_entry(task)
        c = self._handle_request (do_create_resource(self.base_url, 'tasks', entry), task)
        if not c:
            return
        self.lock.acquire()
        self.recent_entries[task.id] = atomixlib.d_entry(c)
        self.lock.release()

    @threaded()
    def task_created(self, task):
        #create a note for this task, 
        self._create_and_send_task_entry(task)

    @threaded()
    def task_updated(self, pre_task, task):
        entry = self.recent_entries.get(task.id, None)
        if entry:
            entry.content.value += u"<div>Update (%s): %s</div>" % (task.updated, task_diff(pre_task, task))
            c = self._handle_request (do_update_resource(self.base_url, 'tasks', entry.id.value, entry), task)
            if not c:
                return
        else:

            entry = self._create_task_entry(task)
            entry.content.value = u"<div>%s</div>" % task_diff(pre_task, task)
            c = self._handle_request (do_create_resource(self.base_url, 'tasks', entry), task)
            if not c:
                return

            self.lock.acquire()
            self.recent_entries[task.id] = atomixlib.d_entry(c)
            self.lock.release()

def task_created(task):
    if hasattr(g, 'atom_store_link'):
        g.atom_store_link.task_created(task)

def task_updated(pre_task, task):
    if hasattr(g, 'atom_store_link'):
        g.atom_store_link.task_updated(pre_task, task)

