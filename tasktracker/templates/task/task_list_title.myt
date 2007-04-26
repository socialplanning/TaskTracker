<%args>
want_description=True
</%args>

<h1 style="display:inline"> <% c.tasklist.title %> </h1>

<br /><br/>
% if want_description and c.tasklist.text:
<% c.tasklist.text %>
<br/><br/>
%