<ul class="xoxo">
% for item in c.tasklists:
  <& item, item=item &>
% #end for
</ul>


<%def item>

<%args>
  item
</%args>

<li>
  <% item.title | h %>

  <dl>
    <dt>created</dt>
    <dd>
      <span class="dtcreated">
        <% h.format_date_long(item.created) | h %>
      </span>
      by <span class="creator">
	<% item.creator | h %>
      </span>
    </dd>
  </dl>
</li>

</%def>
