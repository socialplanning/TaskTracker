<div id="tasklists_table" class="oc-widget oc-widget-dataTable">


    <h2 class="oc-dataTable-heading">Tasklists</h2>

  <table class="oc-dataTable" cellpadding="0" cellspacing="0">
    <thead>
      <tr>
        <th scope="col"><a class="oc-columnSortable oc-selected oc-js-actionLink" href="">Title &darr;</a></th>
        <th scope="col"><a class="oc-columnSortable oc-js-actionLink" href="">Uncompleted tasks</a></th>
        <th scope="col"><a class="oc-columnSortable oc-js-actionLink" href="">Created</a></th>
      </tr>
    </thead>
    <tbody>
% for item in c.tasklists:
        <& widget_project_tasklists_row.myt, item=item &>
% #endfor
    </tbody>
  </table>

</div> <!-- end .oc-widget-dataTable -->
