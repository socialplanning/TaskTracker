<tr id="column-heading" class="column-heading">

<% h.sortableColumn('status', klass="title-column", colspan=2) %>

% columnOrder = h.getColumnOrder(c.permalink)

<% h.generateMovableColumnHeaders(columnOrder) %>

</tr>

<tr class="task-filter-controls">


<td class="title-column filter-line" colspan="2"><%  h.columnFilter('status', c.tasklist) %></td>

<% h.generateMovableColumnFilters(columnOrder) %>

</tr>

<tr class="second-line">

<td colspan="6" id="breaking-row">
<span style="position: absolute; left: 0px; width: 115px; overflow:hidden;" id = "sibling_dropzone_0">
<img src="/images/as_sibling.png" style="display:none;" id = "sibling_dropzone_indicator_0">
&nbsp;
</span>
<span style="position: absolute; right: 0px; left: 115px;" id = "child_dropzone_0">&nbsp;
</span>
&nbsp;</td>

</tr>
