GProt = {};
GProt.initSearch = function(autocompleteData, search) {
    function removeSearchItem(item) {
        for (var i = 0; i < search.length; ++i) {
            if (search[i]['what'] == item['what'] && search[i]['pk'] == item['pk']) {
                search.splice(i, 1);
                break;
            }
        }
        renderSearch();
    }
    function renderSearch() {
        var itemList = $('#search-items');
        itemList.hide().empty()
        if (search.length == 0) {
            return;
        }
        for (var i = 0; i < search.length; ++i) {
            var item = search[i];
            var itemDiv = $('<div class="btn-group search-item"><div class="btn btn-default btn-sm">' + item['label'] + '</div></div>');
            var itemInput = $('<input type="hidden">').attr({
                'name': item['what'] + 's',
                'value': item['pk']
            });
            itemDiv.append('<div class="btn btn-default btn-sm"><span class="glyphicon glyphicon-remove"></span></div>').click(
                (function(item) {
                    return function(ev, ui) {
                        removeSearchItem(item);
                }
            })(item));
            itemList.append(itemDiv).append(itemInput);
        }
        itemList.show();
    }
    
    var aTypes = [{'type': 'course', 'label_key': 'full_name'},
                  {'type': 'teacher', 'label_key': 'full_name'}];
    $('#search').autocomplete({
        'source': getAutocompleteCb(function(term, fn) { fn(autocompleteData); }, aTypes),
        'autoFocus': true,
        'select': function(event, ui) {
            search.push({
                'what': ui.item['objType'],
                'pk': ui.item['objData']['pk'],
                'label': ui.item['label']
            });
            renderSearch();
        }
    });
    renderSearch();
}

function favorite(action){
    let url = window.location.href
    $.ajax({
        type: 'POST',
        url: '/gprot/favorite/',
        headers: {'X-CSRFTOKEN': readCookie('csrftoken')},
        dataType: 'text',
        data: {'action': action, 'url': url},
        success: function() {
            location.reload();
        },
        error: function(){
            location.reload();
        }
    });
}

/** from https://stackoverflow.com/a/1599291 **/
function readCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}
