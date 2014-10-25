import urllib
import urllib2
import json

from django.http import HttpResponse
from django.conf import settings

def autocomplete(request):
    search_term = request.GET.get('search', '')
    if settings.DEBUG:
        request_data = urllib.urlencode({
            'format': 'json',
            'action': 'opensearch',
            'search': search_term.encode('utf-8')
        })
        request_url = '{0}?{1}'.format(settings.WIKI_URL + 'api.php',
                                       request_data)
        result = urllib2.urlopen(request_url).read()
    else:
        result = [
            search_term,
            ["Please configure your webserver to proxy requests"]
        ]
        result = json.dumps(result)
    return HttpResponse(result, content_type='application/x-json')
