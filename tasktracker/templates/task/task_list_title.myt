<h1 style="display:inline"> <% c.tasklist.title %> </h1>

<span class="small">(<span id="num_uncompleted"><% len(c.tasklist.uncompletedTasks()) %></span>
% if len(c.tasklist.uncompletedTasks()) == 1:
task
% else:
tasks
%
left)</span>
<br />
% if c.tasklist.text:
<% c.tasklist.text %>
%
