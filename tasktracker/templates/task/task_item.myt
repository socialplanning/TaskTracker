<%args>
atask
is_preview = False
is_flat = False
editable_title = False
</%args>

<& task_item_row.myt, atask = atask, is_preview = is_preview, is_flat = is_flat, editable_title=editable_title &>

</tr>

<tr id="second_line_<% atask.id %>" class="second-line">
<td colspan="7">
% if atask.text:
 <div style = "clear:both; margin-left: <% (atask.depth() - c.depth) * 15 + 25 %>px; max-width:80em">
   <% h.previewText(atask.text, 400) %>
</div>
%

<!--
% left = min(100 + 15 * atask.depth(), 115)
<div style="position: absolute; left: 0px; width: <% left %>px; overflow:hidden;" id = "sibling_dropzone_<% atask.id %>">
<img src="/images/as_sibling.png" style="display:none;" id = "sibling_dropzone_indicator_<% atask.id %>">
<img src="/images/as_child.png" style="display:none;" id = "child_dropzone_indicator_<% atask.id %>">&nbsp;
</div>
<div style="position: absolute; right: 0px; left: <% left %>px;" id = "child_dropzone_<% atask.id %>">&nbsp;
</div>
-->
</td>

</tr>
