class DummyEventServer:
    def send_message(self, *args):
        pass
    def queue(self, name):
        return self

from tasktracker.models import Task
from sqlobject import events
from pylons import c, g
import tasktracker.lib.helpers as h
from cabochonclient import datetime_to_string
from datetime import datetime

def init_events():
    events.listen(taskUpdated, Task,
                  events.RowUpdateSignal)
    events.listen(taskCreated, Task,
                  events.RowCreatedSignal)    

def taskCreated(kwargs, post_funcs):
    post_funcs.append(taskCreatedPost)

def taskCreatedPost(task):
    g.queues['create'].send_message(dict(
        url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
        context = h.url_for(controller='tasklist', action='show', id=task.task_listID, qualified=True),
        categories=['projects/' + c.project_name, 'tasktracker'],
        name = task.title,
        user = c.username,
        date = datetime_to_string(datetime.now())))

def taskUpdated(task, kwargs):
    if len(kwargs) == 1 and 'num_children' in kwargs:
        return #this was just an update caused by children being added

    event_class = []
    relevant_users = []
    if 'owner' in kwargs:
        event_class.append(['task_assigned', kwargs['owner']])
        relevant_users.append(kwargs['owner'])
        
    if task.owner:
        relevant_users.append(task.owner)


    g.queues['edit'].send_message(dict(
        url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
        context = h.url_for(controller='tasklist', action='show', id=task.task_listID, qualified=True),
        categories=['projects/' + c.project_name, 'tasktracker'],
        name = task.title,        
        user = c.username,
        date = datetime_to_string(datetime.now()),
        event_class = event_class,
        relevant_users = relevant_users
        ))

