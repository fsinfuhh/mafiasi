from StringIO import StringIO
from urllib import quote

import gpgme

from django.template.response import TemplateResponse
from django.shortcuts import redirect, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse, HttpResponseNotFound,
        HttpResponseBadRequest)
from django.conf import settings

from mafiasi.pks.forms import ImportForm
from mafiasi.pks.models import AssignedKey

def index(request):
    return redirect('pks_search')

@login_required
def my_keys(request):
    keys = [key.get_keyobj()
            for key in AssignedKey.objects.filter(user=request.user)]
    return TemplateResponse(request, 'pks/my_keys.html', {
        'keys': keys
    })

@login_required
def upload_keys(request):
    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            for fingerprint in form.imported_keys:
                AssignedKey.objects.get_or_create(fingerprint=fingerprint,
                                                  user=request.user)
            return redirect('pks_my_keys')
    else:
        form = ImportForm()

    return TemplateResponse(request, 'pks/upload_keys.html', {
        'form': form
    })

@login_required
@require_POST
def unassign_keys(request):
    fingerprints = request.POST.getlist('fingerprint')
    AssignedKey.objects.filter(fingerprint__in=fingerprints,
                               user=request.user).delete()
    return redirect('pks_my_keys')

def all_keys(request):
    ctx = gpgme.Context()
    keys = ctx.keylist()
    
    return TemplateResponse(request, 'pks/all_keys.html', {
        'keys': keys
    })

def graph(request):
    return TemplateResponse(request, 'pks/graph.html')

def show_key(request, keyid, raw=False):
    if raw:
        return _hkp_op_get(request, keyid, None)

    ctx = gpgme.Context()
    ctx.armor = True

    try:
        key = ctx.get_key(keyid)
    except gpgme.GpgmeError:
        raise Http404
    
    keydata = StringIO()
    ctx.export(keyid.encode('utf-8'), keydata)

    return TemplateResponse(request, 'pks/show_key.html', {
        'keyid': keyid,
        'key': key,
        'keydata': keydata.getvalue()
    })

def search(request):
    return TemplateResponse(request, 'pks/search.html', {
        'hkp_url': settings.HKP_URL
    })

@csrf_exempt
def hkp_add_key(request):
    try:
        keytext = request.POST['keytext']
    except KeyError:
        return HttpResponseBadRequest("Missing keytext parameter.")
    
    ctx = gpgme.Context()
    result = ctx.import_(StringIO(keytext.encode('utf-8')))

    return HttpResponse('OK. {0} keys imported.'.format(result.imported),
                        mimetype='text/plain')

def hkp_lookup(request):
    op = request.GET.get('op', '')
    options = request.GET.get('options', None)
    search = request.GET.get('search', '')
    
    if op not in ('get', 'index'):
        return HttpResponse('Operation not implemented.',
                            status=501,
                            mimetype='text/plain')

    if not search:
        return HttpResponseBadRequest('Please provide a search term.',
                                      mimetype='text/plain')

    if op == 'get':
        return _hkp_op_get(request, search, options)
    elif op == 'index':
        return _hkp_op_index(request, search, options)
        

def _hkp_op_get(request, search, options):
    ctx = gpgme.Context()
    ctx.armor = True
    
    resp = HttpResponse(mimetype='text/plain')
    ctx.export(search.encode('utf-8'), resp)
    
    if not resp.content:
        return HttpResponseNotFound('No such key: ' + search,
                                    mimetype='text/plain')
    return resp

def _hkp_op_index(request, search, options):
    ctx = gpgme.Context()
    ctx.keylist_mode = gpgme.KEYLIST_MODE_SIGS
    key_list = list(ctx.keylist(search.encode('utf-8')))
    
    if options == 'mr':
        return _hkp_op_index_mr(key_list)
    else:
        return TemplateResponse(request, 'pks/search_result.html', {
            'search_term': search,
            'key_list': key_list
        })

def _hkp_op_index_human(key_list):
    return 

def _hkp_op_index_mr(key_list):
    resp = HttpResponse(mimetype='text/plain')
    resp.write('info:1:{0}\n'.format(len(key_list)))
    
    key_tpl = 'pub:{keyid}:{algo}:{keylen}:{created}:{expires}:{flags}\n'
    uid_tpl = 'uid:{uid}:{created}:{expires}:{flags}\n'
    for key in key_list:
        try:
            subkey = key.subkeys[0]
        except IndexError:
            continue
        resp.write(key_tpl.format(keyid=subkey.fpr,
                                  algo=subkey.pubkey_algo,
                                  keylen=subkey.length,
                                  created=subkey.timestamp,
                                  expires=subkey.expires,
                                  flags=_format_flags(subkey)))

        for uid in key.uids:
            comment = u'({0}) '.format(uid.comment) if uid.comment else ''
            uid_str = u'{0} {1}<{2}>'.format(uid.name, comment, uid.email)
            uid_str = quote(uid_str.encode('utf-8'), '<>@()/ ')
            created = _get_uid_created(uid, subkey.keyid)
            # The standard allows to leave out expirydate
            resp.write(uid_tpl.format(uid=uid_str, created=created, expires='',
                                      flags='r' if uid.revoked else ''))
    return resp

def _format_flags(subkey):
    if subkey.revoked and subkey.expired:
        return 're'
    elif subkey.revoked:
        return 'r'
    elif subkey.expired:
        return 'e'
    else:
        return ''

def _get_uid_created(uid, own_keyid):
    selfsigs = [sig for sig in uid.signatures if sig.keyid == own_keyid]
    if not selfsigs:
        return ''
    return min(sig.timestamp for sig in selfsigs)
