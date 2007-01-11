<%args>
pre_footer
</%args>
<hr />
<br />

<% pre_footer %>
% if h.has_permission('tasklist', 'update', id=c.tasklist.id):
<% h.link_to("Edit list settings", h.url_for(controller='tasklist', action='show_update', id=c.tasklist.id)) %>
|
%

<% h.link_to('Back to list of lists', h.url_for(controller='tasklist', action='index')) %>


