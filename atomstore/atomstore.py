from wsgiref.simple_server import make_server
import selector

from atomstore_setup import setup_amplee_store, create_member_types
from amplee.handler.store.wsgi import Service, Store

def setup_store():
    a_service, collections = setup_amplee_store()
    types = create_member_types()
    
    s = selector.Selector()
    service = Service(a_service)
    s.add('/', GET=service.get_service)
    
    a_store = Store(collections['/tasks'], member_types=types)
    s.add('/tasks[/]', POST=a_store.create_member, GET=a_store.get_collection,
          HEAD=a_store.head_collection)
    s.add('/tasks/{rid:any}', GET=a_store.get_member, PUT=a_store.update_member,
          DELETE=a_store.delete_member, HEAD=a_store.head_member)
        
    return s

if __name__ == '__main__':
    s = setup_store()
    
    httpd = make_server('localhost', 8080, s)
    print "HTTP Serving HTTP on http://localhost:8080/"
    httpd.serve_forever()
