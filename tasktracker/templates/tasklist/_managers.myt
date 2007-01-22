<% h.editable_list('managers', c.managers, c.administrators) %>

<span class="autocomplete">
  <label for="manager" id="add_manager" class="unfolded">[ + ] add manager</label>
<span id="edit_add_manager" class="folded">

   <input type="hidden" value="" id="managers" name="managers">
   <input autocomplete="off" id="manager" name="manager" size="20" type="text" value="" />
   <input type="submit" name="submit" value="Add" onclick="addItem('list_managers', $('manager').value);$('manager').value=''; return false;"/>
</span>

  <div class="auto_complete" id="manager_auto_complete"></div>
  <script type="text/javascript">new Ajax.Autocompleter('manager', 'manager_auto_complete', 
  '../../../task/auto_complete_for/manager', {})</script>
</span>
