<div class="sbar">

<div id="tt-about">

<h2>About Task Tracker</h2> 


<p>Task Tracker is experimental software that makes it easy to share tasks and get stuff done. This just means that we aren't quite done. It is far enough along to be used, but not as polished as we would like it to be. We figure it is better to put tools out there as early as possible and work on making them better as we go along. Just because we are not done developing it doesn't mean you don't already need it. If you love it, hate it, need more or fewer features then <a href="mailto:help@openplans.org">let us know</a>!</p>

<ul id="tt-features">

<li>Create task lists to organize tasks by project, event, or anything else. You might, for example, make one task list for things that need to get done around the office and another task list for organizing opposition to a proposed law.</li>

<li>Just drag-and-drop to divide tasks into sub-tasks then assign them, with or without deadlines, to other members of your project.</li>

<li>Check off tasks as you finish them or track your progress with priority levels and custom statuses.</li>

<li>Claim or steal a task if you see something that needs to get done.</li>

</ul> <!-- end features -->

</div> <!-- end about -->

<div id="tt-glossary">

<h3>Glossary</h3>

<ul>
<li><b>Task lists</b> are just that: independent groups of related things that need to get done.</li>
<li>Anything that needs to get done is considered a <b>task</b>, regardless of whether or not it is part of larger task.</li>
<li><b>Sub-tasks</b> are tasks that are explicitly part of a larger task.</li>
<li>Managers can <b>assign</b> responsibility for a task to any particular user or leave it unassigned.</li>
<li>Tasks can be given different <b>priority levels</b> and sorted or filtered accordingly.</li>
<li>Instead of using a simple checkbox, managers can opt to create <b>custom statuses</b> (such as draft, reviewed, final, ann approved) to describe the state of tasks on a task list.</li>
<li>Under certain settings you can <b>claim</b> unassigned tasks and assign them to yourself.</li>
<li>Under certain settings you can <b>steal</b> tasks assigned to others and reassign them to yourself.</li>
</ul>

</div><!-- end glossary -->

</div>

<h1 class="documentFirstHeading">All task lists for <% c.project.title %></h1>
<p>Create, manage, and share to-do lists.</p>

% if h.has_permission('tasklist', 'show_create'): 
<div id="add_list">
<% h.link_to ('Create a new list', h.url_for(action='show_create')) %>
</div>
%

% undone_tasklists = [list for list in c.tasklists if len(list.uncompletedTasks())]
% if len(undone_tasklists):
<div id="active-tasklists">
<h2>Active Task Lists</h2>
<ul>
% for list in undone_tasklists:
 <li>
  <a href="<%h.url_for(action='show', id=list.id)%>">
   <% list.title %>
  </a> - <span class="small"><% len(list.uncompletedTasks()) %> uncompleted tasks</span>
 </li>
%
</ul>
</div>
%

% done_tasklists = [list for list in c.tasklists if not len(list.uncompletedTasks())]
% if len(done_tasklists):
<div id="completed-tasklists">
<h2>Completed Task Lists</h2>
<ul>
% for list in done_tasklists:
 <li>
  <a href="<%h.url_for(action='show', id=list.id)%>">
   <% list.title %>
  </a>
 </li>
%
</ul>
</div>
%

<hr class="oc-clearElement" />