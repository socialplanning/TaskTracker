<div class="oc-widget oc-widget-dataTable">
  <div class="oc-heading">
    <h3>Tasklists</h3>
    <!--<p class="oc-heading-context">What do you want your project to be named?</p>-->
  </div>
  <div class="oc-searchresults-nresults">
    1-20 of 55
  </div>
  
  <form class="oc-liveForm" action="<% h.url_for('modify-contents') %>">
    <input type="hidden" name="item_type" value="tasklists" />
    <table class="oc-dataTable" cellpadding="0" cellspacing="0">
      <thead>
        <tr>
          <th class="oc-dataTable-checkBoxColumn"><input type="checkbox" class="oc-checkAll" /></th>
          <th scope="col"><a class="oc-columnSortable oc-selected" href="">Title &darr;</a></th>
          <th scope="col"><a class="oc-columnSortable" href="">Size</a></th>
          <th scope="col"><a class="oc-columnSortable" href="">Created</a></th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
% for item in c.tasklists:
        <& widget_project_tasklists_row.myt, item=item &>
% #endfor
      </tbody>
    </table>
    
    <ul class="oc-actions oc-dataTable-actions">
      <li>
        <button type="submit" name="task" value="batch_delete" class="oc-button" >Delete</button>
      </li>
    </ul>
  </form>
</div> <!-- end .oc-widget-dataTable -->
