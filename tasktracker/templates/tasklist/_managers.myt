<% h.editable_list('managers', c.managers, [c.username]) %>

% available_users = sorted([user for user in c.usermapper.project_member_names() if user not in c.managers and user != c.username], key=str.lower)

<input type="hidden" value="<% ",".join(c.administrators + c.managers) %>" id="managers" name="managers">

% if available_users:
<label for="manager" id="add_manager" class="unfolded">[ + ] add manager</label>
<span id="edit_add_manager" class="folded">
  <% h.select('manager', h.options_for_select(available_users)) %>
  <input type="submit" name="submit" value="Add"
         onclick="addItem('list_managers', $('manager').value);$('manager').value=''; return false;"/>
</span>
% #endif
