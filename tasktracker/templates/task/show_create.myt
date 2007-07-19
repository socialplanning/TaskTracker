<%args>
cancel_button = ''
</%args>
<% h.secure_form_remote_tag(url=h.url_for(controller='task', action='create_ajax'),
      			     success='return doneAddingTask(request);', failure='failedAddingTask(request)', html=dict(id='add_task_form')) %>

<h2>Add task</h2>

<div id="error" style="color:#f00;">

</div>

<br/>
<input type="hidden" name="task_listID" value="<%c.task_listID%>" />
<input type="hidden" id="add_task_form_parentID" name="parentID" value="<%c.parentID%>" />
<input type="hidden" id="add_task_form_siblingID" name="siblingID" value="0" />

<div id="hideable_title_label" style="display:none;">title</div>
<% h.text_field_r('oldtask', 'title', size=50, tabindex=1, maxlength=255) %>

<p>
<div id="hideable_add_description">
<a id="show_description" href="#nevermind" class="small">
Add description</a><br/><br/>
</div>

<div id="description_field" style="display:none;">
<div id="hideable_description_label">description</div>
<% h.text_area_r('oldtask', 'text', rows=5, cols=80, tabindex=2, autocomplete='off') %>
<br/>
<a href="#nevermind" id="hide_description"
   onclick="$('description_field').hide(); $('hideable_add_description').show();">Hide description</a><br/><br/>
</div>

<p>
<input type="submit" name="create" value="add" tabindex=4 />
<% cancel_button %>
</form>
