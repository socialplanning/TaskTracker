<%args>
subtask_link = ''
</%args>
<!-- add a new subtask -->
% if h.has_permission('task', 'create', task_listID=c.tasklist.id):
<span id="create_section" class="create_section">

<span id="show_create">
<% subtask_link %>
</span>

<a name="create_anchor" id="create_anchor"/>
<div id="create" style="display:none;">

% cancel_button = """<input type="submit" onclick="$('create').hide(); $('show_create').show(); return false;" name="cancel" value="cancel" tabindex=5/>"""
<& show_create.myt, cancel_button = cancel_button &>
<!-- <p> <a href="#nevermind" onclick="$('create').hide(); $('show_create').show(); return false;">Nevermind</a> </p> -->
</div>
%
