<strong><% c.list_name %></strong><br/>

% for tasks in c.results:

  <span class="small"> <% tasks.path %>:</small>
  <table id="tasks" class="task_list" cellspacing="0">
% for atask in tasks:
<& task_item.myt, atask=atask &>
%
  </table>
%


