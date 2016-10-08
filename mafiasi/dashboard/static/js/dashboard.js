$(function() {
    $('#dashboard .service').equalizeHeights();
    $('#wiki_search').autocomplete({
        'source': function(req, resp_function) {
            console.log(req);
            var search_data = {
                'format': 'json',
                'action': 'opensearch',
                'search': req.term
            };
            $.get('/wiki/autocomplete', search_data, function(resp_data) {
                resp_function(resp_data[1]);
            }, 'json');
        }
    });

    // Initialize sortable
    $('.dashboard-service').sortable({ 
        connectWith: '.dashboard-service',
        revert: true,
        opacity: 0.7
    }).disableSelection();
})
