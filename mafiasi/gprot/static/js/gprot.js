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
            var itemDiv = $('<div class="search-item"></div>').text(item['label']);
            var itemInput = $('<input type="hidden">').attr({
                'name': item['what'] + 's',
                'value': item['pk']
            });
            itemDiv.append('<span>X</span>').click((function(item) {
                return function(ev, ui) {
                    removeSearchItem(item);
                }
            })(item));
            itemList.append(itemDiv).append(itemInput);
        }
        itemList.show();
    }
    
    var aTypes = [{'type': 'course', 'label_key': 'name'},
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

GProt.initCreate = function(autocompleteCourses, autocompleteExaminer, course, examiner) {
    function genericSelectItem(itemType, item) {
        $('#' + itemType + '-input').hide();
        var itemDiv = $('<div class="search-item"></div>').text(item['label']);
        itemDiv.append($('<span>X</span>').click(function() {
            $('#' + itemType + '-item').empty().hide();
            $('#' + itemType + '-input').show();
        }));
        itemDiv.append($('<input type="hidden">').attr({
            'name': itemType,
            'value': item['objData']['pk']
        }));
        $('#' + itemType + '-item').append(itemDiv).show();

    }

    var aTypeCourses = [{'type': 'course', 'label_key': 'name'}];
    $('#course-input').autocomplete({
        'source': getAutocompleteCb(function(term, fn) { fn(autocompleteCourses); }, aTypeCourses),
        'autoFocus': true,
        'select': function(event, ui) {
            genericSelectItem('course', ui.item);
        }
    }); 
    var aTypeCourses = [{'type': 'teacher', 'label_key': 'full_name'}];
    $('#examiner-input').autocomplete({
        'source': getAutocompleteCb(function(term, fn) { fn(autocompleteExaminer); }, aTypeCourses),
        'autoFocus': true,
        'select': function(event, ui) {
            genericSelectItem('examiner', ui.item);
        }
    });
    
    if (course !== null) {
        genericSelectItem('course', course);
    }
    if (examiner !== null) {
        genericSelectItem('examiner', examiner);
    }

    $('#exam-date-input').datepicker({
        'firstDay': 1,
        'dateFormat': 'yy-mm-dd'
    });
}
