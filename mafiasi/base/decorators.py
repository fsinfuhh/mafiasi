

import base64
from functools import wraps
import hashlib
import hmac
import time

from django.http import HttpResponse
from django.conf import settings

def require_auth(username, password, realm='Login'):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            try:
                auth = request.META['HTTP_AUTHORIZATION']
                if not auth.startswith('Basic '):
                    raise ValueError('Invalid auth header')

                creds = base64.b64decode(auth.split()[1])
                http_username, http_password = creds.split(':', 1)
                if http_username != username or http_password != password:
                    # Make timing attacks harder by adding some delay
                    data = (http_username + http_password).encode('utf-8')
                    _data_dependent_delay(data)
                    raise ValueError('Invalid login creds')
            except (ValueError, KeyError, IndexError):
                resp = HttpResponse(b'Unauthorized',
                                    status=401,
                                    content_type='text/plain')
                resp['WWW-Authenticate'] = 'Basic realm="{}"'.format(realm)
                return resp
            return view(request, *args, **kwargs)
        return wrapper
    return decorator

def _data_dependent_delay(data, max_sleep=0.02):
    mac = hmac.new(settings.SECRET_KEY, data, hashlib.sha512).digest()
    sleep_time = (ord(mac[0])/255.0)*max_sleep
    time.sleep(sleep_time)
