<b><% c.project.title %>'s lists</b>:

% if [x for x in c.tasklists if x.uncompletedTasks()]:
<ul>
% for list in c.tasklists:
% if list.uncompletedTasks():
<li>
 <a href="<%h.url_for(action='show', id=list.id)%>">
     <% list.title %> 
     </a> - <span class="small"><% len(list.uncompletedTasks()) %> uncompleted 

<% h.plural ('task', list.uncompletedTasks()) %>

</span>
</li>
%
%
</ul>
%

% if [x for x in c.tasklists if not x.uncompletedTasks()]:
<b>Completed lists:</b>
<ul>
% for list in c.tasklists:
% if not list.uncompletedTasks():
<li>
  <% h.link_to(list.title, h.url_for(action='show', id=list.id)) %>
</li>
%
%
</ul>
%

% if h.has_permission('tasklist', 'show_create'): 
<p>
<% h.link_to ('Create a new list', h.url_for(action='show_create')) %>
</p>
%
