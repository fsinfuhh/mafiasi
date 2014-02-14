import json
import time
from datetime import date

from nameparser import HumanName
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from mafiasi.teaching.models import (Course, Teacher,
        insert_autocomplete_courses, insert_autocomplete_teachers)
from mafiasi.gprot.models import GProt
from mafiasi.gprot.sanitize import clean_html

@login_required
def index(request):
    autocomplete_json = {'tokens': []}
    insert_autocomplete_courses(autocomplete_json)
    insert_autocomplete_teachers(autocomplete_json)

    search_json = []
    gprots = []
    if request.method == 'POST':
        course_pks = request.POST.getlist('courses')
        courses = list(Course.objects.filter(pk__in=course_pks))
        for course in courses:
            search_json.append({
                'what': 'course',
                'pk': course.pk,
                'label': course.name
            })
        
        teacher_pks = request.POST.getlist('teachers')
        teachers = list(Teacher.objects.filter(pk__in=teacher_pks))
        for teacher in teachers:
            search_json.append({
                'what': 'teacher',
                'pk': teacher.pk,
                'label': teacher.get_full_name()
            })

        gprots = GProt.objects.select_related()
        if courses:
            gprots = gprots.filter(course__pk__in=course_pks)
        if teachers:
            gprots = gprots.filter(examiner__pk__in=teacher_pks)


    return render(request, 'gprot/index.html', {
        'autocomplete_json': json.dumps(autocomplete_json),
        'search_json': json.dumps(search_json),
        'gprots': gprots
    })

@login_required
def create_gprot(request):
    autocomplete_courses = {'tokens': []}
    insert_autocomplete_courses(autocomplete_courses)
    autocomplete_examiners = {'tokens': []}
    insert_autocomplete_teachers(autocomplete_examiners)
    
    errors = {}
    course = None
    examiner = None
    exam_date = None
    course_name = ''
    examiner_name = ''
    exam_date_str = ''
    if request.method == 'POST':
        if 'course' in request.POST and request.POST['course'].isdigit():
            course = get_object_or_404(Course, pk=request.POST['course'])
        else:
            course_name = request.POST.get('course_name', '').strip()
            if not course_name:
                errors['course_name'] = True
            course = Course(name=course_name, short_name='')
        if 'examiner' in request.POST and request.POST['examiner'].isdigit():
            examiner = get_object_or_404(Teacher, pk=request.POST['examiner'])
        else:
            examiner_name = HumanName(request.POST.get('examiner_name', ''))
            if examiner_name.middle:
                first_name = u'{0} {1}'.format(examiner_name.first,
                                               examiner_name.middle)
            else:
                first_name = examiner_name.first
            last_name = examiner_name.last

            if not last_name:
                examiner = None
                errors['examiner_name'] = True
            else:
                examiner = Teacher(first_name=first_name, last_name=last_name,
                                   title=examiner_name.title)
        exam_date_str = request.POST.get('exam_date', '')
        try:
            exam_date_t = time.strptime(exam_date_str, '%Y-%m-%d')
            exam_date = date(exam_date_t.tm_year, exam_date_t.tm_mon,
                                 exam_date_t.tm_mday)
        except ValueError:
            errors['exam_date'] = True
        
        if not errors:
            if not course.pk:
                course.save()
            if not examiner.pk:
                examiner.save()
            gprot = GProt.objects.create(course=course,
                                         examiner=examiner,
                                         exam_date=exam_date,
                                         content='',
                                         author=request.user)
            return redirect('gprot_edit', gprot.pk)

    if course and course.pk:
        course_js = json.dumps({
            'label': course.name,
            'objData': {'pk': course.pk}
        })
    else:
        course_js = 'null'

    if examiner and examiner.pk:
        examiner_js = json.dumps({
            'label': examiner.get_full_name(),
            'objData': {'pk': examiner.pk}
        })
    else:
        examiner_js = 'null'

    return render(request, 'gprot/create.html', {
        'errors': errors,
        'course_name': course_name,
        'examiner_name': examiner_name,
        'exam_date_str': exam_date_str,
        'course_js': course_js,
        'examiner_js': examiner_js,
        'autocomplete_course_json': json.dumps(autocomplete_courses),
        'autocomplete_examiner_json': json.dumps(autocomplete_examiners)
    })

@login_required
def view_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    return render(request, 'gprot/view.html', {
        'gprot': gprot,
    })

@login_required
def list_own_gprots(request):
    gprots = (GProt.objects.select_related().filter(author=request.user)
            .order_by('-exam_date'))
    return render(request, 'gprot/list_own.html', {
        'gprots': gprots
    })

@login_required
def edit_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    if gprot.author != request.user:
        raise PermissionDenied('You are not the owner')
     
    if request.method == 'POST':
        content = request.POST.get('content', '')
        gprot.content = clean_html(content)
        gprot.save()
        if 'publish' in request.POST:
            return redirect('gprot_publish', gprot.pk)
        else:
            return redirect('gprot_edit', gprot.pk)
    return render(request, 'gprot/edit.html', {
        'gprot': gprot,
    })

@login_required
def publish_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    if gprot.author != request.user:
        raise PermissionDenied('You are not the owner')

    if request.method == 'POST' and 'authorship' in request.POST:
        if request.POST['authorship'] == 'purge':
            gprot.author = None
        gprot.published = True
        gprot.save()
        return redirect('gprot_view', gprot.pk)
     
    return render(request, 'gprot/publish.html', {
        'gprot': gprot
    })
