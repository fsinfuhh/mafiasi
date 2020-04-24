import urllib.request, urllib.parse, urllib.error
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings


def autocomplete(request):
    search_term = request.GET.get('search', '')
    if settings.DEBUG:
        request_data = urllib.parse.urlencode({
            'format': 'json',
            'action': 'opensearch',
            'search': search_term.encode('utf-8')
        })
        request_url = '{0}?{1}'.format(settings.WIKI_URL + 'api.php',
                                       request_data)
        result = urllib.request.urlopen(request_url).read()
    else:
        result = [
            search_term,
            ["Please configure your webserver to proxy requests"]
        ]
        result = json.dumps(result)
    return HttpResponse(result, content_type='application/x-json')


def redirect_to_wiki(request, search):
    return HttpResponseRedirect(f'https://wiki.mafiasi.de/{search}')
