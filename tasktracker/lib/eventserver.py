class DummyEventServer:
    def send_message(self, *args):
        pass
    def queue(self, name):
        return self

from tasktracker.models import Task
from sqlobject import events
from pylons import c, g, h

def init_events():
    events.listen(taskUpdated, Task,
                  events.RowUpdateSignal)
    events.listen(taskCreated, Task,
                  events.RowCreatedSignal)    

def taskCreated(kwargs, post_funcs):
    post_funcs.append(taskCreatedPost)

def taskCreatedPost(task):
    g.queues['create'].send_message(dict(url=h.url_for(controller='task', action='show', id=task.id, qualified=True), categories=['projects/' + c.project_name, 'tasktracker'], user=c.user))

def taskUpdated(task, kwargs):
    g.queues['edit'].send_message(dict(url=h.url_for(controller='task', action='show', id=task.id, qualified=True), categories=['projects/' + c.project_name, 'tasktracker'], user=c.user))

