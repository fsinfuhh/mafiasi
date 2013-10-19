from base64 import b64decode

from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from mafiasi.cal.models import DavObject

def index(request):
    return TemplateResponse(request, 'cal/index.html', {
        'caldav_base_url': settings.CALDAV_BASE_URL
    })

@csrf_exempt
def proxy_calendar(request, username, calendar_name):
    return _proxy_request(request, username, calendar_name, 'ics')

@csrf_exempt
def proxy_contactlist(request, username, contactlist_name, auth):
    return _proxy_request(request, username, contactlist_name, 'vcf')

def _proxy_request(request, username, object_name, object_type):
    try:
        obj = DavObject.objects.get(username=username,
                                    name=object_name,
                                    type=object_type)
    except DavObject.DoesNotExist:
        obj = None
    
    try:
        auth = request.META['HTTP_AUTHORIZATION']
        if not auth.startswith('Basic '):
            raise ValueError('Invalid auth')

        creds = b64decode(auth.split()[1])
        auth_username, auth_password = creds.split(':', 1)
        
        auth_user = authenticate(username=auth_username,
                                 password=auth_password)
        if not auth_user:
            raise ValueError('Invalid user/password')
    except (TypeError, ValueError, KeyError, IndexError):
        if obj is None or not obj.is_public:
            resp = HttpResponse('', status=401)
            resp['WWW-Authenticate'] = 'Basic realm="Mafiasi"'
            return resp
    
    # Check permissions for non-owners
    if username != auth_username:
        requires_write = request.method not in ('GET', 'HEAD', 'PROPFIND')
        if obj is None or not obj.has_access(auth_user, requires_write):
            raise PermissionDenied()

    url_path = u'/caldav/{0}/{1}.{2}'.format(username, object_name, type)
    
    resp = HttpResponse('Server should use nginx as frontend proxy.')
    resp['X-Accel-Redirect'] = url_path
    resp['X-Accel-Buffering'] = 'no'
    return resp
