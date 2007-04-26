<%args>
want_description=True
</%args>

<h1> <% c.tasklist.title %> </h1>

% if want_description and c.tasklist.text:
<div id="task-list-description"><% c.tasklist.text %></div>
%