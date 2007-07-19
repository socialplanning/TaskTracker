<tr><td>
<input type="hidden" name="task_listID" value="<% c.task_listID %>" />
<label class="row-heading" for="title">Title:</label></td>
<td><% h.text_field_r('oldtask', 'title') %></td></tr>

<tr><td><label class="row-heading" for="text">Description:</label></td>
<td><% h.text_area_r('oldtask', 'text', rows=10, cols=80) %>
</td></tr>

<tr><td><label class="row-heading" for="deadline">Deadline:</label></td>
<td>
<% h.datebocks_field('oldtask', 'deadline', attributes={'id':'deadline'}) %>
<!-- <span tal:condition="python: c.oldtask and c.oldtask.deadline" tal:replace="structure python: h.text_field('deadline.time', value=c.oldtask.deadline.strftime('%H:%M:%S'))%>
<span tal:condition="python: not c.oldtask or not c.oldtask.deadline" tal:replace="structure python: h.text_field('deadline.time', value='')" /><br/> -->
<span class="small"> hh:mm:ss</span>
</td></tr>

<tr><td><label class="row-heading" for="priority">Priority:</label></td>
<td><% h.select('priority', h.options_for_select((('None', 'None'), ('High','High'), ('Medium','Medium'), ('Low','Low')), h.get_value('oldtask', 'priority', 'None')))%></td>
</tr>

% if c.owner:
<tr><td><span class="row-heading">Assigned to:</span></td>
<td><% c.owner %></td>
</tr>
%

<tr><td>
<div class="row-heading"> 
% if c.owner:
Reassign task to:
% else:
Assign task to:
%
</div>
</td><td>
<span class="autocomplete">
<input autocomplete="off" id="owner" name="owner" size="30" type="text" value="" />
<div class="auto_complete" id="owner_auto_complete"></div>
<script type="text/javascript">new Ajax.Autocompleter('owner', 'owner_auto_complete', 
'../../../task/auto_complete_for/owner/', {})</script>
</span></td></tr>
