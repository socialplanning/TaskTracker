class DummyEventServer:
    def send_message(self, *args):
        pass
    def queue(self, name):
        return self

from tasktracker.models import Task, Comment
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
    events.listen(commentCreated, Comment,
                  events.RowCreatedSignal)    


def taskCreated(kwargs, post_funcs):
    post_funcs.append(taskCreatedPost)

def commentCreated(kwargs, post_funcs):
    post_funcs.append(commentCreatedPost)


def taskCreatedPost(task):
    g.queues['create'].send_message(dict(
        url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
        context = h.url_for(controller='tasklist', action='show', id=task.task_listID, qualified=True),
        categories=['projects/' + c.project_name, 'tasktracker'],
        title = task.long_title,
        user = c.username,
        date = datetime_to_string(datetime.now())))

    #if the task is assigned, send a task_assigned
    if task.owner:
        taskUpdated(task, {'owner' : task.owner})

def commentCreatedPost(comment):
    task = comment.task
    g.queues['edit'].send_message(dict(
        url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
        context = h.url_for(controller='tasklist', action='show', id=task.task_listID, qualified=True),
        categories=['projects/' + c.project_name, 'tasktracker'],
        title = task.long_title,
        event_class = [['task_comment', comment.user]],
        user = c.username,
        date = datetime_to_string(datetime.now())))

def taskDeletedPost(task):
    g.queues['delete'].send_message(dict(
        url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
        user = c.username,
        date = datetime_to_string(datetime.now())))


def taskUpdated(task, kwargs):
    if kwargs.get('live') == 0:
        return taskDeletedPost(task)
    
    if len(kwargs) == 1 and 'num_children' in kwargs:
        return #this was just an update caused by children being added

    event_class = []
    relevant_users = []
    if 'owner' in kwargs:
        event_class.append(['task_assigned', kwargs['owner']])
        relevant_users.append(kwargs['owner'])
        
    if task.owner:
        relevant_users.append(task.owner)

    #XXX this is duplicative of the model, but lacking post_funcs, I can't get
    #at the real new task object
    long_title = "%s - %s - %s" % (task.task_list.project.title, task.task_list.title, kwargs['title'] or task.title)
    
    g.queues['edit'].send_message(dict(
        url = h.url_for(controller='task', action='show', id=task.id, qualified=True),
        context = h.url_for(controller='tasklist', action='show', id=task.task_listID, qualified=True),
        categories=['projects/' + c.project_name, 'tasktracker'],
        title = long_title,
        user = c.username,
        date = datetime_to_string(datetime.now()),
        event_class = event_class,
        relevant_users = relevant_users
        ))

