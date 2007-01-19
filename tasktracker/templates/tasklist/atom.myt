<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

 <title><% c.tasklist.title %></title>
 <link rel="self" href="<% h.url_for (id=c.tasklist.id, qualified = True) %>"/>
 <updated><% h.atomTime(h.taskListUpdated(c.tasklist)) %></updated>
 <id><% h.url_for(controller='tasklist', id=c.tasklist.id, qualified = True) %></id>

% for task in c.tasklist.tasks:
 <entry>
   <title><% task.title %></title>
   <author><name><% task.versions[-1].updatedBy %></name></author>
   <link href="<% h.url_for (controller='task', action='show', id=task.id, qualified = True) %>"/>
   <id><% h.url_for(controller='tasklist', id=task.id, qualified=True) %></id>
   <updated><% h.atomTime(task.updated) %></updated>
   <summary><% h.render_action(task.versions[-1]) %></summary>
 </entry>
%
</feed>
