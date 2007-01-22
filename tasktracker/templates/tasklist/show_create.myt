<h1>Create New List</h1>

<% h.secure_form(h.url(action='create'), method='post') %>

<& _form.myt &>

</form>

<script>
if ($('custom_status').checked) {
    $('statuses').show();
}
</script>
