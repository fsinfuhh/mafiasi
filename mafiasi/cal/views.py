import json
import time
from datetime import datetime
from os.path import basename
from base64 import b64decode

from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from mafiasi.cal.models import DavObject, Calendar

resp_unauthorized = HttpResponse('Unauthorized.',
                                 status=401,
                                 mimetype='text/plain')
resp_unauthorized['WWW-Authenticate'] = 'Basic realm="Mafiasi"'

@login_required
def index(request):
    Calendar.objects.sync(request.user.username)
    return TemplateResponse(request, 'cal/index.html', {
        'calendars': Calendar.objects.filter(username=request.user.username),
        'caldav_display_url': settings.CALDAV_DISPLAY_URL
    })

@login_required
def calendar_data(request):
    try:
        start = datetime.fromtimestamp(int(request.GET['start']))
        end = datetime.fromtimestamp(int(request.GET['end']))
        calendar_paths = request.GET.getlist('calendars[]')
    except (ValueError, KeyError):
        return HttpResponseBadRequest('Invalid or missing start/end/calendars')
    
    events_list = []
    for calendar_path in calendar_paths:
        events_list += _fetch_calendar_data(
            start, end, request.user, calendar_path)

    return HttpResponse(json.dumps({'events': events_list}),
                        mimetype='application/x-json')

def _fetch_calendar_data(start, end, user, calendar_path):
    try:
        username, calendar_name = calendar_path.split('/', 1)
    except ValueError:
        return []
    
    try:
        calendar  = Calendar.objects.get(username=username,
                                         name=calendar_name,
                                         type='ics')
        if not calendar.has_access(user):
            return []
    except Calendar.DoesNotExist:
        return []

    events = calendar.get_events(start, end)
    events_list = []
    for event in events:
        is_allday = not isinstance(event['dtstart'], datetime)
        start = int(time.mktime(event['dtstart'].timetuple()))
        end = int(time.mktime(event['dtend'].timetuple()))
        events_list.append({
            'id': event['uid'],
            'title': event['summary'],
            'allDay': is_allday,
            'start': start,
            'end': end,
            'calendar': calendar_path
        })
    return events_list

@csrf_exempt
def proxy_request(request, username, object_name, object_type, object_path):
    try:
        obj = DavObject.objects.get(username=username,
                                    name=object_name,
                                    type=object_type)
    except DavObject.DoesNotExist:
        obj = None
    
    try:
        auth_username, auth_password = _get_auth(request)    
        auth_user = authenticate(username=auth_username,
                                 password=auth_password)
        if not auth_user:
            raise ValueError('Invalid user/password')
    except (TypeError, ValueError, KeyError, IndexError):
        auth_username, auth_password = None, None
        auth_user = None
        if obj is None or not obj.is_public:
            return resp_unauthorized
    
    read_methods = ('GET', 'HEAD', 'PROPFIND', 'OPTIONS', 'REPORT')
    requires_write = request.method not in read_methods
    
    # Check permissions for non-owners
    if username != auth_username:
        if obj is None or not obj.has_access(auth_user, requires_write):
            raise PermissionDenied()

    url_path = u'/_caldav/{0}/{1}.{2}/{3}'.format(
            username, object_name, object_type, basename(object_path))
    
    resp = HttpResponse('Server should use nginx as frontend proxy.')
    resp['X-Accel-Redirect'] = url_path.encode('utf-8')
    resp['X-Accel-Buffering'] = 'no'
    return resp

@csrf_exempt
def proxy_request_collection(request, username):
    query_access = request.method == 'OPTIONS'
    try:
        auth_username, auth_password = _get_auth(request)
        auth_user = authenticate(username=auth_username,
                                 password=auth_password)
        if not auth_user and not query_access:
            raise ValueError('Invalid user/password')

        if auth_username != username and not query_access:
            raise PermissionDenied()
    except (ValueError, KeyError):
        if not query_access:
            return resp_unauthorized
    
    url_path = u'/_caldav/{0}/'.format(username) 
    resp = HttpResponse('Server should use nginx as frontend proxy.')
    resp['X-Accel-Redirect'] = url_path.encode('utf-8')
    resp['X-Accel-Buffering'] = 'no'
    return resp

def _get_auth(request):
    auth = request.META['HTTP_AUTHORIZATION']
    if not auth.startswith('Basic '):
        raise ValueError('Invalid auth')

    creds = b64decode(auth.split()[1])
    if ':' not in creds:
        raise ValueError('Invalid auth')

    return creds.split(':', 1)
