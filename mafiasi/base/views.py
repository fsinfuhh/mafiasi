from django.conf import settings
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

def imprint(request):
    return HttpResponseRedirect(settings.IMPRINT_URL)

def technical_info(request):
    return TemplateResponse(request, 'base/technical_info.html')

def problems(request):
    team_email = settings.TEAM_EMAIL
    if not request.user.is_authenticated():
        team_email = team_email.replace(u'@', u' (AT) ')
    return TemplateResponse(request, 'base/problems.html', {
        'team_email': team_email
    })
