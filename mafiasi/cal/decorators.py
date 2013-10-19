import base64
from functools import update_wrapper
from collections import namedtuple

from django.http import HttpResponse

_auth_tuple = namedtuple('Auth', 'username', 'password')

def annotate_auth(view):
    def _wrapper(request, *args, **kwargs):
        try:
            auth = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth.startswith('Basic '):
                raise ValueError('Invalid auth')

            creds = base64.b64decode(auth.split()[1])
            username, password = creds.split(':', 1)
        except (TypeError, ValueError, KeyError, IndexError):
            resp = HttpResponse('', status=401)
            resp['WWW-Authenticate'] = 'Basic realm="Mafiasi"'
            return resp

        kwargs['auth'] = _auth_tuple(username, password)
        return view(request, *args, **kwargs)

    return update_wrapper(_wrapper, view)
