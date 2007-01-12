% if c.task.private:
 <% h.secure_link_to_remote('make this task public',
    dict(url=h.url_for(controller='task', action='update_private', id=c.task.id, private='false'),
         complete="change_description_updated(%s, 'Privacy');" % c.task.id,
	 update=dict(success='private'))) %> |
% else:
<% h.secure_link_to_remote('make this task private', 
   dict(url=h.url_for(controller='task', action='update_private', id=c.task.id, private='true'),
        complete="change_description_updated(%s, 'Privacy');" % c.task.id,
	update=dict(success='private'))) %> |
%

