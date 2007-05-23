<%args>
  item
</%args>
<%python scope="init">
  children = item.liveChildren()
</%python>

<li>
  <% item.title | h %>
  <dl>
% if item.text:
    <dt>description</dt>
    <dd><% item.text | h %></dd>
% #end if

    <dt>created</dt>
    <dd>
      <span class="dtcreated">
        <% h.format_date_long(item.created) | h %>
      </span>
      by <span class="creator">
        <% item.creator | h %>
      </span>
    </dd>

% if item.updated != item.created:
    <dt>updated</dt>
    <dd>
      <span class="dtupdated">
        <% h.format_date_long(item.updated) | h %>
      </span>
    </dd>
% #end if

% if item.owner:
    <dt>owner</dt>
    <dd><% item.owner | h %></dd>
% #end if

% if item.status:
    <dt>status</dt>
    <dd><% item.status.name | h %></dd>
% #end if

% if item.deadline:
    <dt>deadline</dt>
    <dd>
      <span class="dtdeadline">
        <% h.format_date_long(item.deadline) | h %>
      </span>
    </dd>
% #end if

% if item.priority:
    <dt>priority</dt>
    <dd><% item.priority | h %></dd>
% #end if


  </dl>
% if children:
  <ol>
%   for subitem in children:
    <& export_item.myt, item=subitem &>
%   #end for
  </ol>
% #end if
</li>
