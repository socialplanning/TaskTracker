<%args>
want_filters=True
</%args>

<tr id="column-heading" class="column-heading">
 <% h.sortableColumn('status', klass="title-column", colspan=2) %>
% columnOrder = h.getColumnOrder(c.permalink)
 <% h.generateMovableColumnHeaders(columnOrder) %>
 <td class="delete-task-column filter-line">&nbsp;</td>
</tr>

% if want_filters:
<tr class="task-filter-controls">
 <td class="title-column filter-line" colspan="2">
  <%  h.columnFilter('status', c.tasklist) %>
 </td>

 <% h.generateMovableColumnFilters(columnOrder) %>

 <td class="delete-task-column filter-line">&nbsp;</td>

</tr>

<tr class="second-line">
 <td colspan="6" id="breaking-row">
  <div id = "sibling_dropzone_0" class="sibling_dropzone">
   <% h.image_tag("as_sibling.png", class_="hidden", id="sibling_dropzone_indicator_0") %>
   &nbsp;
  </div>
  <div id = "child_dropzone_0" class="child_dropzone" />
   &nbsp;
  </div>
  &nbsp;
 </td>
</tr>
%