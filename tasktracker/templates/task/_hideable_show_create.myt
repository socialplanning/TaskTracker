<%args>
subtask_link = ''
</%args>

<!-- add a new subtask -->
% if h.has_permission('task', 'create', task_listID=c.tasklist.id):
<div id="create_section" class="create_section">

 <div id="show_create">
  <% subtask_link %>
 </div>

 <a name="create_anchor" id="create_anchor"></a>
 <div id="create" class="hidden">

% cancel_button = """<input type="submit" onclick="addClass($('create'), 'hidden'); $('show_create').show(); return false;" name="cancel" value="cancel" tabindex=5/>"""
  <& show_create.myt, cancel_button = cancel_button &>

 </div>

</div>
%
