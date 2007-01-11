<h1>Create New List</h1>

A task list is a container for tasks.  Task lists are used to organize
tasks by area, or by sub-project.  For example, there might be a task
list for tasks around the office, and another task list for organizing
opposition to a proposed law.

<% h.secure_form(h.url(action='create'), method='post') %>

<& _form.myt &>

</form>

<script>
if ($('custom_status').checked) {
    $('statuses').show();
}
</script>
