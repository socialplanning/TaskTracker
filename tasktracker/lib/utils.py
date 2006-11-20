import threading
from decorator import decorator

def threaded():
    def call(proc, *args, **kwargs):
        thread = threading.Thread (target=proc, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return decorator(call)
