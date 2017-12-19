

import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

from mafiasi.base.autocomplete import autocomplete_users

def imprint(request):
    return HttpResponseRedirect(settings.IMPRINT_URL)

def data_privacy_statement(request):
    return TemplateResponse(request, 'base/data_privacy_statement.html')

def technical_info(request):
    return TemplateResponse(request, 'base/technical_info.html')

def licenses(request):
    return TemplateResponse(request, 'base/licenses.html')

def problems(request):
    team_email = settings.TEAM_EMAIL
    if not request.user.is_authenticated:
        team_email = team_email.replace('@', ' (AT) ')
    return TemplateResponse(request, 'base/problems.html', {
        'team_email': team_email
    })

@login_required
def autocomplete(request):
    term = request.GET.get('term', '')
    users = autocomplete_users(term)
    result_json = json.dumps({
    "users": [{
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        } for user in users]
    })
    return HttpResponse(result_json, content_type='application/json')
