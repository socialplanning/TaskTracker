<%args>
atask
is_preview = False
is_flat = False
editable_title = False
</%args>

<& task_item_row.myt, atask = atask, is_preview = is_preview, is_flat = is_flat, editable_title=editable_title &>

</tr>

% if atask.status.done:
<tr id="second_line_<% atask.id %>" class="second-line completed-task">
% else:
<tr id="second_line_<% atask.id %>" class="second-line">
%

<td colspan="7">
% if atask.text:
 <div class="second-line-task-description">
   <% h.htmlize(h.previewText(atask.text, 200)) %>
</div>
%

% taskdepth = (atask.depth() - c.depth) * 1.5 + 2

<div style="padding-left: <% taskdepth %>em;" id = "sibling_dropzone_<% atask.id %>" class="sibling_dropzone">
 <% h.image_tag('as_sibling.png', class_="hidden", id="sibling_dropzone_indicator_%d" % atask.id) %>
 &nbsp;
</div>

<div style="padding-right: <% taskdepth %>em;" id = "child_dropzone_<% atask.id %>" class="child_dropzone">
 &nbsp;
 <% h.image_tag('as_child.png', class_="hidden", id="child_dropzone_indicator_%d" % atask.id) %>
 &nbsp;
</div>

</td>
</tr>