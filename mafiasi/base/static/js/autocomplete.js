/*
 * Return a callback that can be used with jQuery autocomplete.
 * 
 * @param {Function} autocompleteDataCb(fn): Callback that calls fn with autocomplete data
 * @param {Array} autocompleteTypes -- List of objects {'type': type, 'label_key': label_key}
 * 
 * Autocomplete data is an objects with the following structure:
 * {
 *     'some_type': {
 *         pk1: { 'label_key': ..., 'value_key': ..., other object data }
 *         pk2: { ... }
 *         ...
 *     },
 *     'tokens': [
 *        {'pk': some_pk, 'type': some_type, 'token': compared_term}
 *        ...
 *     ]
 * }
 *
 * If value_key is undefined or null, the value will be empty.
 */
function getAutocompleteCb(autocompleteDataCb, autocompleteTypes) {
    function doAutocomplete(autocompleteData, request, response) {
        var responseData = [];
        var responseSet = {};
        var term = request.term.toLowerCase();
        var tokens = autocompleteData['tokens'];
        for (var i = 0; i < tokens.length; ++i) {
            var tokenObj = tokens[i];
            var token = tokenObj['token'];
            var appendResponse = true;
            for (var j = 0; j < term.length && j < token.length; ++j) {
                if (term.charAt(j) != token.charAt(j)) {
                    appendResponse = false;
                    break;
                }
            }

            var key = tokenObj['type'] + '_' + tokenObj['pk'];
            if (!appendResponse || responseSet[key]) {
                continue;
            }

            for (var j = 0; j < autocompleteTypes.length; ++j) {
                var autocompleteType = autocompleteTypes[j];
                if (tokenObj['type'] != autocompleteType['type']) {
                    continue;
                }
                
                var objType = autocompleteType['type'];
                var obj = autocompleteData[objType][tokenObj['pk']];
                
                var valueKey = autocompleteType['value_key'];
                var value = '';
                if (typeof(autocompleteTypes['value_key']) === 'string') {
                    value = obj[valueKey];
                }
                
                responseSet[key] = true; 
                responseData.push({
                    'label': obj[autocompleteType['label_key']],
                    'value': value,
                    'objData': obj,
                    'objType': objType
                });
            }
        }
        response(responseData);
    }
    
    return function(request, response) {
        autocompleteDataCb(request.term, function(autocompleteData) {
            doAutocomplete(autocompleteData, request, response);
        });
    }
}
