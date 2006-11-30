
function setupEditableList(field, list_id) {
    var the_list = $(list_id);
    the_list.field = field;
    //    Sortable.create(the_list_id);
}

function updateItem(list) {
    //update the form variable
    list = $(list);
    var items = list.getElementsByTagName('li')
    var s = '';

    for (i = 0; i < items.length; ++i) {
        s += getItemName(items[i]);
	s += ',';
    }

    list.field.value = s;
}

function deleteItem(list, item_name) {
    $(item_name).parentNode.remove();
    updateItem(list);
}

function getItemName(item_li) {
    return item_li.getElementsByTagName('span')[0].childNodes[0].nodeValue;
}

function addItem(list, item) {

    item = item.replace(/[^A-Za-z0-9 ]/g, '');

    if (item.length < 1) {
        return;
    }

    //prevent duplication

    var item_list = $(list);
    var items = item_list.getElementsByTagName('li');

    for (i = 0; i < items.length; ++i) {

        if (getItemName(items[i]) == item) {
            return;
        }
    } 
    //add the html element

    var item_name = 'item_' + items.length;
    var del = "deleteItem('" + list + "', '" + item_name + "');";
    var check = Builder.node('span', {'id' : item_name, 'onclick' : del}, ' [ - ]');
    var li = Builder.node('li', [Builder.node('span', item), check]);

    var last_item = item_list.firstChild;
    while (last_item.nextSibling) {
	last_item = last_item.nextSibling;
    }
    item_list.insertBefore(li, last_item);

    updateItem(list);

    //    Sortable.destroy(the_list_id);
    //    Sortable.create(the_list_id);
}
