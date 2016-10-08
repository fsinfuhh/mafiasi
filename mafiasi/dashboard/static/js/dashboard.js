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

    /**
     * Save the current order of the dashboard services in localStorage.
     */
    function saveServicesOrder() {
        if (typeof(localStorage) === undefined) {
            return;
        }

        var services = [];
        $('.dashboard-service').each(function(key, elem) {
            services.push($(elem).data('servicetitle'));
        });

        localStorage.setItem('dashboard-services-order', JSON.stringify(services));
    }

    // Initialize sortable
    $('#dashboard-services-container').sortable({ 
        connectWith: '.dashboard-service',
        revert: true,
        opacity: 0.7,
        update: saveServicesOrder
    }).disableSelection();
})
