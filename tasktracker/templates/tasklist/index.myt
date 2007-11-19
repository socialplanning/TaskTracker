          <div>
      <div id="oc-content-main">
        <div class="oc-headingBlock">
          <h1>Task lists</h1>
          <p class="oc-headingContent">Create, manage, and share to-do lists.</p>
        </div>

% if not len(c.tasklists):
          <p class="oc-boxy oc-discreetText">
            There are currently no task lists for this project.
          </p>
% else:

% undone_tasklists = [list for list in c.tasklists if len(list.uncompletedTasks())]
% if len(undone_tasklists):
<div class="oc-boxy">
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
<div class="oc-boxy">
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

%
<!-- starts about -->
  <div>
  <ul class="oc-smallText oc-plainList">

<li>Create a <b>task list</b> for each of your project's goals.</li>
<li>Within a task list, create <b>tasks</b> and assign them <b>priorities</b>.  </li>
<li>Drag-and-drop to divide tasks into <b>sub-tasks</b>.</li>

<li>Choose specific task list<b> managers</b> from your project's team members.

<li><b>Assign</b> tasks, with or without deadlines, to members of your project.</li>
<li>Tasks can be given different <b>priority levels</b> and sorted or filtered accordingly</li>
<li><b>Check off</b> tasks as you finish them or track them with <b>custom statuses</b>.	</li>
<li><b>Claim</b> or <b>steal</b> a task if you see something that needs to get done.
	</li>
</ul>
</div> <!-- end about -->
        
      </div><!-- oc-content-main -->
      
      
      
      <div id="oc-content-sidebar">
        <div>

% if h.has_permission('tasklist', 'show_create'): 
<% h.link_to ('Add a new task list', h.url_for(action='show_create'), class_="oc-banana") %>
%
    	</div>

<div class="oc-boxy">    
<h3>About Task Tracker</h3> 
<p>Task Tracker makes it easy to share tasks and get stuff done. It's still in development,
but just because we are not finished doesn't mean you don't already need it. If
you love it, hate it, need more or fewer features then <a href="mailto:help@openplans.org">let us know</a>!</p>
<p>
Track your progress, steal tasks and experience a tailored to-do-list experience. </p>
<!-- end features -->
</div>
    
      </div>
    </div>
<hr class="oc-clearElement" />