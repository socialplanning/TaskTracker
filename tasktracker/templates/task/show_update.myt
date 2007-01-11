Update task:<br/>
<form action="<% h.url_for(action='update', id=c.oldtask.id) %>" task_id="<%c.oldtask.id%>" method="post" id="form">

<table>

<tr><td>
<span class="row-heading">Parent:</span></td><td>
<% h.taskDropDown(c.oldtask.id, c.oldtask.task_listID, initial_value = c.oldtask.parentID) %></td></tr>
<& _form.myt &>
</table>

<input type="submit" name="create" value="edit">

</form>
