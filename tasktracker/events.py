from pylons import g

def connect(events, event, action):
    events.setdefault(event, [])
    events[event].append(action)

def fire(event, **kwargs):
    actions = g.events.get(event)
    if not actions:
        return
    for action in actions:
        action(**kwargs)
