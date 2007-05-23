<h1>Task List <% c.task_list.title | h %></h1>

<p>
  Created on <span class="dtcreated">
  <% h.format_date_long(c.task_list.created) | h %>
  </span>
</p>

<!-- FIXME: should export custom status and features -->

% if c.task_list.text:
  <p><% c.task_list.text | h %></p>
% #end if

<ol class="xoxo">
% for item in c.tasks:
  <& item, item=item &>
% #end for
</ol>


<%def item>

<%args>
  item
</%args>
<%python scope="init">
  children = item.liveChildren()
  comments = item.comments
</%python>

<li>
% if item.status.done:
  <del><% item.title | h %></del>
% else:
  <% item.title | h %>
% #end if

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

% if comments:
    <dt>comments</dt>
    <dd>
      <ul class="comment">
%   for comment in comments:
        <li>
          <blockquote class="text">
            <% comment.text | h %>
          </blockquote>
          &em; <span class="commenter"><% comment.user | h %>
          <span class="dtcreated">
            <% h.format_date_long(comment.date) | h %>
          </span>
        </li>
%   #end for
      </ul>
    </dd>
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

</%def>