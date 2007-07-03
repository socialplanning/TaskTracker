<div class="oc-widget oc-widget-dataTable">

  <div class="oc-heading">
    <h3>Tasklists</h3>
  </div>
  
  <table class="oc-dataTable" cellpadding="0" cellspacing="0">
    <thead>
      <tr>
        <th scope="col"><a class="oc-columnSortable oc-selected" href="">Title &darr;</a></th>
        <th scope="col"><a class="oc-columnSortable" href="">Uncompleted tasks</a></th>
        <th scope="col"><a class="oc-columnSortable" href="">Created</a></th>
      </tr>
    </thead>
    <tbody>
% for item in c.tasklists:
        <& widget_project_tasklists_row.myt, item=item &>
% #endfor
    </tbody>
  </table>

</div> <!-- end .oc-widget-dataTable -->
