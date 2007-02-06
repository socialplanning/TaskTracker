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
 <span style = "clear:both; margin-left: <% (atask.depth() - c.depth) * 15 + 25 %>px;">
   <% h.previewText(atask.text, 400) %>
</span>
</td>
</tr>