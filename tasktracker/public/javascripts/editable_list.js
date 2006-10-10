var the_list_id;
var the_list;

function setupEditableList(list_id) {
    the_list_id = list_id;
    the_list = $(the_list_id);
    Sortable.create(the_list_id);
}

function updateItem() {
    //update the form variable
    var item_list = the_list;
    var items = item_list.getElementsByTagName('li')
    var s = '';

    for (i = 0; i < items.length; ++i) {
        s += getItemName(items[i]);
	s += ',';
    }

    $('items').value = s;
}

function deleteItem(item_name) {
    $(item_name).parentNode.remove();
    updateItem();
}

function getItemName(item_li) {
    return item_li.getElementsByTagName('span')[0].childNodes[0].nodeValue;
}

function addItem(item) {
    item = item.replace(/[^A-Za-z0-9 ]/g, '');

    if (item.length < 1) {
        return;
    }

    item = item.toLowerCase();

    //prevent duplication

    var item_list = the_list;
    var items = item_list.getElementsByTagName('li');

    for (i = 0; i < items.length; ++i) {

        if (getItemName(items[i]) == item) {
            return;
        }
    } 
    //add the html element

    var item_name = 'item_' + items.length;
    var del = 'deleteItem(\'' + item_name + '\');';
    var check = Builder.node('input', {'id' : item_name, 'type' : 'checkbox', 'onclick' : del});
    var li = Builder.node('li', [check, Builder.node('span', item)]);

    done = $('done');
    item_list.insertBefore(li, done);

    updateItem();

    Sortable.destroy(the_list_id);
    Sortable.create(the_list_id);
}
