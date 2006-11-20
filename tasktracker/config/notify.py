from tasktracker.lib import store_notes
from tasktracker.events import connect

def setup_notify(events):
    connect(events, 'Task Created', store_notes.task_created)
    connect(events, 'Task Updated', store_notes.task_updated)


