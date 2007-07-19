<%args>
item
</%args>

<tr class="oc-liveItem" id=<% item.id %> >

  <td>
    <div>
      <a href=<% h.url_for(controller='tasklist', action='show', id=item.id) %> >
        <% item.title %>
      </a>
    </div>

  </td>
  <td>
    <% len(item.uncompletedTasks()) %>
  </td>
  <td>
    <% h.prettyDate(item.created) %>
% creator = item.creator
% if creator:
    by
    <a href=<% c.usermapper.member_url(creator) %> >
      <% creator %>
    </a>
% #endif
  </td>

</tr>
