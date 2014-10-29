import json
from StringIO import StringIO
from urllib import quote

import gpgme

from django.template.response import TemplateResponse
from django.shortcuts import redirect, get_object_or_404, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import (HttpResponse, HttpResponseNotFound,
        HttpResponseBadRequest)
from django.conf import settings

from mafiasi.pks.forms import ImportForm
from mafiasi.pks.models import AssignedKey, KeysigningParty, Participant
from mafiasi.pks.graph import build_signature_graph

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
def autocomplete_keys(request):
    term = request.GET.get('term', u'')
    resp = HttpResponse(content_type='text/plain')
    if len(term) < 3:
        json.dump([], resp)
        return resp
    
    ctx = gpgme.Context()
    keys = ctx.keylist(term.encode('utf-8'))
    autocomplete_data = []
    for key in keys:
        try:
            uid = key.uids[0]
            keyid = key.subkeys[0].keyid
            label = u'{}: {} <{}>'.format(keyid, uid.name, uid.email)
            autocomplete_data.append({
                'value': keyid,
                'label': label
            })
        except IndexError:
            continue
    json.dump(autocomplete_data, resp)
    return resp

@login_required
def assign_keyid(request):
    ctx = gpgme.Context()
    try:
        key = ctx.get_key(request.POST.get('keyid', u'').encode('utf-8'))
        fingerprint = key.subkeys[0].fpr
    except gpgme.GpgmeError:
        messages.error(request, _('Could not find the given keyid.'))
        return redirect('pks_my_keys')
    except IndexError:
        messages.error(request, _('Could not find a valid subkey.'))
        return redirect('pks_my_keys')

    _key, created = AssignedKey.objects.get_or_create(fingerprint=fingerprint,
                                                      user=request.user)
    if created:
        messages.success(request, _('Key was successfully assigned to you.'))
    else:
        messages.info(request, _('Key was already assigned to you'))
    return redirect('pks_my_keys')

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

def graph(request, party_pk=None):
    party = None
    graph_name = 'global'
    if party_pk:
        party = get_object_or_404(KeysigningParty, pk=party_pk)
        graph_name = 'party{}'.format(party.pk)
    return TemplateResponse(request, 'pks/graph.html', {
        'graph_name': graph_name,
        'party': party
    })

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

def party_list(request):
    parties = list(KeysigningParty.objects.order_by('-event_date'))

    # Fetch parties the user participates in
    user_party_pks = set()
    if request.user.is_authenticated():
        for participant in Participant.objects.filter(user=request.user):
            user_party_pks.add(participant.party.pk)
    # Mark those parties
    for party in parties:
        party.user_participates = party.pk in user_party_pks

    return TemplateResponse(request, 'pks/party_list.html', {
        'parties': parties
    })

@login_required
def party_participate(request, party_pk):
    party = get_object_or_404(KeysigningParty, pk=party_pk)
    if party.submission_expired():
        messages.error(request, _("Sorry, submission period is over."))
        return redirect('pks_party_list')

    if request.method == 'POST':
        fingerprints = request.POST.getlist('fingerprint')
        keys = AssignedKey.objects.filter(fingerprint__in=fingerprints,
                                          user=request.user)
        
        user = request.user
        try:
            participant = Participant.objects.get(user=user, party=party)
            if not keys:
                participant.delete()
                participant = None
        except Participant.DoesNotExist:
            if keys:
                participant = Participant.objects.create(user=user, party=party)
            else:
                participant = None
        
        if participant:
            participant.keys.clear()
            for key in keys:
                participant.keys.add(key)
        
            messages.success(request,
                    _("Successfully submitted keys to party."))
            return redirect('pks_party_keys', party.pk)
        else:
            messages.success(request,
                    _("Not participating in this keysigning party."))
            return redirect('pks_party_list')
    
    keys = [key.get_keyobj()
            for key in AssignedKey.objects.filter(user=request.user)]
    
    return TemplateResponse(request, 'pks/party_participate.html', {
        'party': party,
        'keys': keys
    })

@login_required
def party_keys(request, party_pk):
    party = get_object_or_404(KeysigningParty, pk=party_pk)
    
    participants_qs = party.participants.select_related().order_by(
            'user__first_name')
    participants = []
    for participant in participants_qs:
        participants.append({
            'user': participant.user,
            'keys': [key.get_keyobj() for key in participant.keys.all()]
        })

    return TemplateResponse(request, 'pks/party_keys.html', {
        'party': party,
        'participants': participants
    })

@login_required
def party_keys_export(request, party_pk):    
    party = get_object_or_404(KeysigningParty, pk=party_pk)

    ctx = gpgme.Context()
    ctx.armor = True
    resp = HttpResponse(content_type='text/plain')
    for participant in party.participants.select_related():
        for key in participant.keys.all():
            ctx.export(key.fingerprint.encode('utf-8'), resp)
    return resp

@login_required
def party_missing_signatures(request, party_pk):
    party = get_object_or_404(KeysigningParty, pk=party_pk)
    
    # Select all participating keys and partition them into own and others
    all_keys = {}
    own_keys = {}
    other_keys = {}
    for participant in party.participants.select_related():
        for key in participant.keys.all():
            key_obj = key.get_keyobj()
            try:
                keyid = key_obj.subkeys[0].keyid
            except IndexError:
                continue
            
            key.keyid = keyid
            key.key_obj = key_obj
            all_keys[keyid] = key
            
            if participant.user == request.user:
                own_keys[keyid] = key
            else:
                other_keys[keyid] = key

    # signature_graph: signed_keyid -> []signer_keyid
    keylist = [key.key_obj for key in all_keys.itervalues()]
    signature_graph = build_signature_graph(keylist)

    # Collect keyids which the user still has to sign
    missing_my_sigs = {}
    for signed_keyid, signer_keyids in signature_graph.iteritems():
        if signed_keyid in own_keys:
            continue
        for own_key in own_keys.itervalues():
            if own_key.keyid in signer_keyids:
                continue
            other_key = other_keys[signed_keyid]
            _fill_missing_sigs(missing_my_sigs, own_key, other_key)
    
    # Collect keyids of other users which still have to sign the users keys
    missing_other_sigs = {}
    for other_key in other_keys.itervalues():
        for own_key in own_keys.itervalues():
            if other_key.keyid not in signature_graph[own_key.keyid]:
                _fill_missing_sigs(missing_other_sigs, own_key, other_key)
    
    sig_key = lambda sig: sig['user'].get_full_name()
    missing_my_sigs = sorted(missing_my_sigs.itervalues(), key=sig_key)
    missing_other_sigs = sorted(missing_other_sigs.itervalues(), key=sig_key)
    return TemplateResponse(request, 'pks/party_missing_signatures.html', {
        'party': party,
        'missing_my_sigs': missing_my_sigs,
        'missing_other_sigs': missing_other_sigs
    })

def _fill_missing_sigs(missing_sigs, own_key, other_key):
        other_user = other_key.user
        if other_user.pk not in missing_sigs:
            missing_sigs[other_user.pk] = {
                'user': other_user,
                'keys': []
            }
        missing_sigs[other_user.pk]['keys'].append({
            'own': own_key,
            'other': other_key,
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
                        content_type='text/plain')

def hkp_lookup(request):
    op = request.GET.get('op', '')
    options = request.GET.get('options', None)
    search = request.GET.get('search', '')
    
    if op not in ('get', 'index'):
        return HttpResponse('Operation not implemented.',
                            status=501,
                            content_type='text/plain')

    if not search:
        return HttpResponseBadRequest('Please provide a search term.',
                                      content_type='text/plain')

    if op == 'get':
        return _hkp_op_get(request, search, options)
    elif op == 'index':
        return _hkp_op_index(request, search, options)
        

def _hkp_op_get(request, search, options):
    ctx = gpgme.Context()
    ctx.armor = True
    
    resp = HttpResponse(content_type='text/plain')
    ctx.export(search.encode('utf-8'), resp)
    
    if not resp.content:
        return HttpResponseNotFound('No such key: ' + search,
                                    content_type='text/plain')
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
    resp = HttpResponse(content_type='text/plain')
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
