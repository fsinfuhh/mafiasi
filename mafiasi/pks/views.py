import gpgme

from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from mafiasi.pks.forms import ImportForm
from mafiasi.pks.models import PGPKey

@login_required
def my_keys(request):
    keys = [key.get_keyobj()
            for key in PGPKey.objects.filter(user=request.user)]
    return TemplateResponse(request, 'pks/my_keys.html', {
        'keys': keys
    })

@login_required
def upload_keys(request):
    if request.method == 'POST':
        form = ImportForm(request.POST)
        if form.is_valid():
            for fingerprint in form.imported_keys:
                PGPKey.objects.get_or_create(fingerprint=fingerprint,
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
    PGPKey.objects.filter(fingerprint__in=fingerprints,
                          user=request.user).delete()
    return redirect('pks_my_keys')

def all_keys(request):
    ctx = gpgme.Context()
    keys = ctx.keylist()
    
    return TemplateResponse(request, 'pks/all_keys.html', {
        'keys': keys
    })
