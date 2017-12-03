import json
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from mafiasi.teaching.forms import CourseForm, TeacherForm

def _error_list():
    pass

@login_required
@require_POST
def api_create_teacher(request):
    form = TeacherForm(request.POST, prefix='teacher')
    if form.is_valid():
        teacher = form.save()
        return HttpResponse(serialize('json', [teacher]),
                            content_type='application/json')
    else:
        return HttpResponse(str(form.errors), status=400)

@login_required
@require_POST
def api_create_course(request):
    form = CourseForm(request.POST, prefix='course')
    if form.is_valid():
        course = form.save()
        return HttpResponse(serialize('json', [course]),
                            content_type='application/json')
    else:
        return HttpResponse(str(form.errors), status=400)
