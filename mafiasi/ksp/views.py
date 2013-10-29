from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.conf import settings
#from mafiasi.ksp.models import Ksp, KspParticipants, Key
from mafiasi.ksp.GPG import GPG
from mafiasi.ksp.GPGFingerprintParser import GPGFingerprintParser
from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

import re
from django.contrib.auth.decorators import login_required

from django.utils import timezone

extractNumberOfImportedKeys = re.compile('imported: (\d*)')

extractId = re.compile('^.*/(........) .*$')

def get_gpg():
    return GPG(homedir='/var/tmp/keyring', args = ['--armor', '--display-charset', 'utf-8'])

"""
def index(request):
    try:
        ksp = Ksp.objects.filter(date__gte=timezone.now()
                                  ).order_by('-date')[0]
    except:
        ksp = None
    return TemplateResponse(request, 'ksp/index.html', {
        'next_ksp': ksp,
        'ksp_participants': KspParticipants.objects.filter(ksp=ksp)
    })"""
def index(request):
    return TemplateResponse(request, 'ksp/index.html', {
        'next_ksp': None,
        'ksp_participants': None
    })
"""
def plain_all(request):
    return TemplateResponse(request, 'ksp/plain.html', {
        'keys': Key.objects.all()
     })"""

def list_keys(request, party=None):
    gpg = get_gpg()
    stdout, stderr = gpg.list_keys('--fingerprint')
    print stdout.split('\n'), stderr
    data = None
    keys = []
    #if party:
    #   keys =
    next_fp = False # remember if the next line is the fingerprint
    for line in stdout.split('\n'):
        line = unicode(line, 'utf-8')
        if line.startswith("pub"):
            if data:
                keys.append(data)
            data = {"uids": []}
            data['info'] = line[5:]
            next_fp = True
            data['id'] = extractId.search(data['info']).group(1)
            continue
        if next_fp:
            data['fingerprint'] = line[line.find('=') + 2:]
            next_fp = False
            continue
        if line.startswith("uid"):
            data['uids'].append(line[3:].lstrip())
            continue
    if data:
        keys.append(data)
    print keys
    if request.type == 'html':
    return TemplateResponse(request, 'ksp/list_keys.html', {
        'keys': keys
    })
    #elif request.type == 'plain':
    #   return ' '.join([k['id'] for k in keys])
    #else:
    #    return 'st00p1d user'

def show_graph(request):
    return TemplateResponse(request, 'ksp/show_graph.html')


@csrf_exempt
def hkp_add_key(request):
    keytext = request.REQUEST['keytext']
    if keytext is None:
        return("No key, no cookies!")
    gpg = get_gpg()
    stdout, stderr = gpg.Import(input = keytext.encode('utf-8'))
    result = unicode(stderr, 'utf-8') # waiting for python3...
    numberOfImportedKeys = extractNumberOfImportedKeys.search(result)
    if result.find("not changed") > -1:
        message = "Your key is already in the keyring for this key-signing-party"
    elif numberOfImportedKeys and int(numberOfImportedKeys.group(1)) > 0:
        message = "Your %s succesfully added to the keyring for this key-signing-party" % ('keys were' if int(numberOfImportedKeys.group(1)) > 1 else 'key was')
    else:
        message = "Something went wrong : -("
    return TemplateResponse(request, 'ksp/add_key.html', {
        'message' : message,
        'log' : result
    })

@login_required
def add_key_form(request):
    return TemplateResponse(request, 'ksp/add_key_form.html')

def hkp_lookup(request,):
    op = request.GET.get('op', None)
    options = request.GET.get('options', None)
    search = request.GET.get('search', "")

    gpg = get_gpg()
    if op is None:
        return HttpResponse("Error handling request: Please use operations 'get' or 'index'.", status=400)
    if not search.strip():
        return HttpResponse("Error handling request: No keys Found.", status = 400)

    # sanitize input to avoid parameter injection
    search = search.lstrip('-')

    if op == "get":
        message = gpg.export(search)
    elif op == "index":
        keys = []
        def handler(key):
            date = datetime.strptime(key["created"], '%Y-%m-%d').strftime('%s')
            keys.append("pub:%s:%i:%i:%s::" % (key["id"], key["type_int"], key["length"], date))
            for uid in key["uids"]:
                keys.append("uid:%s:::" % uid)
        message, err = gpg.list_keys("--with-colons", search)
        GPGFingerprintParser(handler).parse(message)
        count = len(keys)
        message = "info:1:%i\n%s" % (count, "\n".join(keys))
    else:
        return HttpResponse("Error handling request: Please use operations 'get' or 'index'.", status=400)

    if options == 'mr':
        return HttpResponse(message)
    else:
        return TemplateResponse(request, 'ksp/hkp_query_result.html', {
            'result': message
        })
