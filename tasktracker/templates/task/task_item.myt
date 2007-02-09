<%args>
atask
is_preview = False
is_flat = False
editable_title = False
</%args>


<& task_item_row.myt, atask = atask, is_preview = is_preview, is_flat = is_flat, editable_title=editable_title &>

</tr>

% if atask.text:
<tr id="second_line_<% atask.id %>" class="second-line">
<td colspan="7">
 <div style = "clear:both; margin-left: <% (atask.depth() - c.depth) * 15 + 25 %>px; max-width:80em">
   <% h.previewText(atask.text, 400) %><br/>
</div>
</td>
</tr>
%