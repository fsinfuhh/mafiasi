import json
import time
from datetime import date

from nameparser import HumanName
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from mafiasi.teaching.models import (Course, Teacher,
        insert_autocomplete_courses, insert_autocomplete_teachers)
from mafiasi.gprot.models import GProt

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
    if request.method == 'POST':
        if 'course' in request.POST:
            course = get_object_or_404(Course, pk=request.POST['course'])
        else:
            course_name = request.POST.get('course_name').strip()
            if not course_name:
                errors['course_name'] = True
            course = Course(name=course_name, short_name='')
        if 'examiner' in request.POST:
            examiner = get_object_or_404(Teacher, pk=request.POST['examiner'])
        else:
            examiner_name = HumanName(request.POST.get('examiner_name'))
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
        try:
            exam_date_str = request.POST.get('exam_date', '')
            exam_date_t = time.strptime(exam_date_str, '%Y-%m-%d')
            exam_date = date(exam_date_t.tm_year, exam_date_t.tm_mon,
                             exam_date_t.tm_mday)
        except ValueError:
            raise
            exam_date = None
            errors['exam_date'] = True
        
        if not errors:
            pass

    return render(request, 'gprot/create.html', {
        'errors': errors,
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
def render_preview(request):
    pass
