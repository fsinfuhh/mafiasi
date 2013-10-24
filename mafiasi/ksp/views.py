from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.conf import settings
from mafiasi.ksp.models import Ksp, KspParticipants, Key

from django.utils import timezone

def index(request):
    try:
        ksp = Ksp.objects.filter(date__gte=timezone.now()
                                  ).order_by('-date')[0]
    except:
        ksp = None
    return TemplateResponse(request, 'ksp/index.html', {
        'next_ksp': ksp,
        'next_ksp_date': ksp.date,
        'ksp_participants': KspParticipants.objects.filter(ksp=ksp)
    })

def plain_all(request):
    return TemplateResponse(request, 'ksp/plain.html', {
        'keys': Key.objects.all()
     })
