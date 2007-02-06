<%args>
cancel_button = ''
</%args>
<% h.secure_form_remote_tag(url=h.url_for(controller='task', action='create'),
      			     success='return doneAddingTask(request);', failure='failedAddingTask', html=dict(id='add_task_form')) %>

Add task:

<br/><br/>
<input type="hidden" name="task_listID" value="<%c.task_listID%>" />
<input type="hidden" id="add_task_form_parentID" name="parentID" value="<%c.parentID%>" />
<input type="hidden" id="add_task_form_siblingID" name="siblingID" value="0" />

<div id="hideable_title_label" style="display:none;">title</div>
<% h.text_field_r('oldtask', 'title', size=80, tabindex=1) %>

% if c.tasklist.hasFeature('private_tasks'):
<div style="display:inline;">
  <% h.check_box_r('oldtask', 'private', tabindex=3) %> make this task private
</div>
%
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
<input type="submit" name="create" value="go" tabindex=4 />
<% cancel_button %>
</form>
