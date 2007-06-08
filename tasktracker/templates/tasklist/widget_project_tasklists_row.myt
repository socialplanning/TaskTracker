<%args>
item
</%args>

<tr class="oc-liveItem" id=<% item.id %> >
  <td>
    <input type="checkbox" name="batch[]"
           value=<% item.id %> />
  </td>
  <td>
    <div class="oc-liveItem-value">
      <a href=<% h.url_for(controller='tasklist', action='view', id=item.id) %> >
        <% item.title %>
      </a>
    </div>
    
    <div class="oc-liveItem-editForm">
      <input type="text"
             name=<% '%d_title' % item.id %>
	     value=<% item.title %>
             />
      <button type="submit" name="task"
              value= <% '%d_update' % item.id %> >
        Save
      </button>
      or
      <a href="#" class="oc-liveItem_toggle">
        Cancel
      </a>
    </div>
  </td>
  <td>
    FILL IN WITH SOMETHING LIKE SIZE
  </td>
  <td>
    CREATED OR UPDATED DATE
    by
    <a href="#todo_fillin">
      CREATOR OR UPDATOR
    </a>
  </td>
  <td>
    <ul class="oc-actions oc-dataTable-row-actions">
      <li>
        <a class="oc-actionLink"
           href=<% "%s?task=%d_delete" % (h.url_for('modify-contents'), item.id) %> >
          Delete
        </a>
      </li>
    </ul>
  </td>
</tr>
