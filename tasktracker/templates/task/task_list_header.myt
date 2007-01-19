<tr class="column-heading">

<th id="status-heading" class="status-column">&nbsp;</th>
<% h.sortableColumn('status', klass="title-column") %>

% if c.tasklist.hasFeature('deadlines'):
 <% h.sortableColumn('deadline') %>
%

<% h.sortableColumn('priority') %>

<% h.sortableColumn('owner', 'assigned&nbsp;to') %>

<% h.sortableColumn('updated', 'updated') %>

</tr>

<tr class="task-filter-controls">

<td class="taskitem status-column filter-line">&nbsp;</td>
<td class="title-column filter-line"><%  h.columnFilter('status', c.tasklist) %></td>

% if c.tasklist.hasFeature('deadlines'):
<td class="deadline-column filter-line">
    <%  h.columnFilter('deadline') %></td>
%

<td class="priority-column filter-line"><%  h.columnFilter('priority') %></td>
<td class="owner-column filter-line"><%  h.columnFilter('owner', c.tasklist) %></td>
<td class="updated-column filter-line"><%  h.columnFilter('updated') %></td>
</tr>

<tr class="second-line">

<td colspan="6" id="breaking-row">&nbsp;</td>

</tr>
