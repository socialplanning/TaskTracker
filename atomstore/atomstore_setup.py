import sys
import os
import os.path

from amplee.atompub.store import *
from amplee.atompub.service import *
from amplee.atompub.workspace import *
from amplee.atompub.collection import *
from amplee.handler import MemberType
from amplee.atompub.member import atom
from amplee.storage import dummyfs#, storedejavu, storezodb , storesvn

from bridge import Element, Attribute
from bridge.common import ATOM10_PREFIX, ATOM10_NS 

local_dir = os.path.abspath(os.path.dirname(__file__))

def create_amplee_storage():
    base_storage_path = os.path.join(local_dir, 'store')
    if not os.path.exists(base_storage_path):
        raise Warning, "Please create the following directory first: %s" % base_storage_path
    media_storage = dummyfs.DummyStorageFS(base_storage_path)
    media_storage.create_container('audio')

    #config = {'Connect': "host=localhost dbname=store user=test password=test"}
    #member_storage = storedejavu.DejavuStorage('dejavu.storage.storepypgsql.StorageManagerPgSQL', config)

    return media_storage, media_storage #member_storage, media_storage
                              
def create_amplee_store(storage, media_storage):
    return AtomPubStore(storage, media_storage=media_storage)
    
def create_amplee_service(store):
    return AtomPubService(store)

def create_amplee_task_updates_collection(service):
    accept_media_types = [u'application/atom+xml']
    workspace = AtomPubWorkspace(service, "task updates", title=u"Some task updates")
    collection = AtomPubCollection(workspace, name_or_id="tasks",
                                   title=u"Task Updates", xml_attrs={'base': u"http://localhost:8080"},
                                   base_uri=u"tasks",
                                   base_edit_uri=u"tasks/edit",
                                   accept_media_types=accept_media_types)
    return collection

def setup_amplee_store():
    a_storage, a_media_storage = create_amplee_storage()
    a_store = create_amplee_store(a_storage, a_media_storage)
    a_service = create_amplee_service(a_store)

    b_collection = create_amplee_task_updates_collection(a_service)
    b_collection.reload_members()

    return a_service, {'/tasks': b_collection}

def on_create_cb(member, content):
    # do something here or raise
    # amplee.error.ResourceOperationException
    # to stop the processing
    return member, content

def create_member_types():
    types = {}

    params = {'inline_content': False}
    types['application/atom+xml'] = MemberType('application/xhtml+xml',
                                               atom.AtomMember, params)

    return types
# -*- coding: utf-8 -*-
