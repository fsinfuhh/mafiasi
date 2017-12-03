# -*- coding: utf-8 -*-
import json
import time
import magic
from datetime import date

from fuzzywuzzy import fuzz
from PyPDF2 import PdfFileReader, PdfFileWriter
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.core.mail import send_mail
from smtplib import SMTPException
from django.utils.translation import ugettext as _
from django.utils.crypto import constant_time_compare
from raven.contrib.django.raven_compat.models import client
from django.middleware.csrf import get_token as get_csrf_token

from mafiasi.teaching.models import Course, insert_autocomplete_courses
from mafiasi.teaching.forms import TeacherForm, CourseForm
from mafiasi.gprot.forms import \
        GProtBasicForm, GProtCreateForm, GProtSearchForm
from mafiasi.gprot.models import Attachment, GProt, Notification, Reminder
from mafiasi.gprot.sanitize import clean_html

@login_required
def index(request):
    is_query = False
    gprots = []
    if request.method == 'POST':
        form = GProtSearchForm(request.POST)
        if form.is_valid():
            is_query = True
            examiners, courses = form.cleaned_data['search']
        
            gprots = GProt.objects.select_related() \
                .filter(published=True) \
                .order_by('-exam_date')
            if courses:
                gprots = gprots.filter(course__in=courses)
            for teacher in examiners:
                gprots = [g for g in gprots if teacher in g.examiners.all()]
    else:
        form = GProtSearchForm()

    return render(request, 'gprot/index.html', {
        'gprots': gprots,
        'is_query': is_query,
        'form': form,
    })

@login_required
def create_gprot(request):
    if request.method == 'POST':
        form = GProtCreateForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            examiners = form.cleaned_data['examiner']
            exam_date = form.cleaned_data['exam_date']
            is_pdf = {'pdf': True,
                      'html': False}[form.cleaned_data['type']]

            gprot = GProt.objects.create(course=course,
                                         exam_date=exam_date,
                                         is_pdf=is_pdf,
                                         content='',
                                         author=request.user)
            gprot.examiners = examiners
            gprot.save()
            return redirect('gprot_edit', gprot.pk)
    else:
        form = GProtCreateForm()

    teacher_form = TeacherForm(prefix='teacher')
    course_form = CourseForm(prefix='course')
    user_has_gprots = GProt.objects.filter(author=request.user).exists()
    return render(request, 'gprot/create.html', {
        'form': form,
        'teacher_form': teacher_form,
        'course_form': course_form,
        'user_has_no_gprots': not user_has_gprots,
    })

@login_required
def view_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    if gprot.published or gprot.author == request.user:
        return render(request, 'gprot/view.html', {
            'gprot': gprot,
        })
    else:
        raise Http404

@login_required
def list_own_gprots(request):
    gprots = (GProt.objects.select_related().filter(author=request.user)
            .order_by('-exam_date'))
    return render(request, 'gprot/list_own.html', {
        'gprots': gprots
    })


@login_required
def edit_metadata(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    if request.method == 'POST':
        form = GProtBasicForm(request.POST)
        if form.is_valid():
            gprot.course = form.cleaned_data['course']
            gprot.examiners = form.cleaned_data['examiner']
            gprot.exam_date = form.cleaned_data['exam_date']
            gprot.save()
            return redirect('gprot_edit', gprot.pk)
    else:
        form = GProtBasicForm({
            'course': [gprot.course.pk],
            'examiner': [examiner.pk for examiner in gprot.examiners.all()],
            'exam_date': gprot.exam_date.strftime('%Y-%m-%d'),
        })

    teacher_form = TeacherForm(prefix='teacher')
    course_form = CourseForm(prefix='course')
    return render(request, 'gprot/edit_metadata.html', {
        'gprot': gprot,
        'form': form,
        'teacher_form': teacher_form,
        'course_form': course_form,
    })

def _clean_pdf_metadata(gprot):
    assert gprot.is_pdf

    title = "GProt: {} / {}".format(
        gprot.course.get_full_name(),
        gprot.exam_date.strftime("%Y-%m-%d"),
    )
    writer = PdfFileWriter()

    # Django file fields aren't context managers :/
    gprot.content_pdf.open('r')
    reader = PdfFileReader(gprot.content_pdf)
    for i in range(reader.getNumPages()):
        writer.addPage(reader.getPage(i))
    gprot.content_pdf.close()

    writer.addMetadata({
        '/Title': title,
    })

    gprot.content_pdf.open('r+')
    writer.write(gprot.content_pdf)
    gprot.content_pdf.close()

@login_required
def edit_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    if gprot.author != request.user:
        raise PermissionDenied('You are not the owner')

    error = ''
    if request.method == 'POST':
        if gprot.is_pdf:
            if 'file' in request.FILES:
                upload = request.FILES['file']
                if upload.size > settings.GPROT_PDF_MAX_SIZE * 1000000:
                    error = _('Only files up to {0} MB are allowed.').format(
                        settings.GPROT_PDF_MAX_SIZE)
                if magic.from_buffer(upload.read(1024), mime=True) \
                                                        != 'application/pdf':
                    error = _('Only PDF files are allowed.')
            else:
                error = _('Please select a file to upload.')

            if not error:
                if gprot.content_pdf:
                    gprot.content_pdf.delete()
                gprot.content_pdf = upload
                gprot.save()
                _clean_pdf_metadata(gprot)

        else:
            content = request.POST.get('content', '')
            gprot.content = clean_html(content)
            gprot.save()

        if not error:
            if 'publish' in request.POST:
                return redirect('gprot_publish', gprot.pk)
            else:
                return redirect('gprot_view', gprot.pk)

    return render(request, 'gprot/edit.html', {
        'gprot': gprot,
        'error': error,
        'attachment_csrf_token': get_csrf_token(request)
    })

@login_required
def delete_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)

    if request.method == 'POST':
        if gprot.author != request.user:
            raise PermissionDenied('You are not the owner')
        if gprot.published:
            raise PermissionDenied(
                'Published memory minutes cannot be deleted')

        if gprot.is_pdf and gprot.content_pdf:
            gprot.content_pdf.delete()
        else:
            attachments = Attachment.objects.filter(gprot=gprot_pk)
            for attachment in attachments:
                attachment.file.delete()
                attachment.delete()
        gprot.delete()
        return redirect('gprot_list_own')

    return render(request, 'gprot/delete.html', {
        'gprot': gprot
    })

@login_required
def forget_owner(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)

    if request.method == 'POST':
        if gprot.author != request.user:
            raise PermissionDenied('You are not the owner')
        if not gprot.published:
            raise PermissionDenied('Unpublished gprots cannot be disowned')

        gprot.author = None
        gprot.save()

        return redirect('gprot_view', gprot_pk)

    return render(request, 'gprot/forget.html', {
        'gprot': gprot
    })

@csrf_exempt
@login_required
@require_POST
def create_attachment(request, gprot_pk):
    response_str = "<script type='text/javascript'>window.parent.CKEDITOR.tools.callFunction({0}, '{1}', '{2}');</script>"

    gprot = get_object_or_404(GProt, pk=gprot_pk)
    func_num = request.GET.get('CKEditorFuncNum', '')
    if not func_num.isdigit():
        raise HttpResponseBadRequest('Invalid CKEditorFuncNum')

    error = None

    # HACK: manual CSRF verification because CKEditor does not
    # support custom POST parameters for image uploads.
    csrf_cookie = request.COOKIES.get(settings.CSRF_COOKIE_NAME)
    csrf_token = request.GET.get('csrf_token')
    if not (csrf_cookie and csrf_token
            and constant_time_compare(csrf_cookie, csrf_token)):
        raise PermissionDenied('CSRF verification failed.')

    if 'upload' in request.FILES:
        upload = request.FILES['upload']

        if upload.size > settings.GPROT_IMAGE_MAX_SIZE * 1000000:
            error = _('Only files up to {0} MB are allowed.').format(
                settings.GPROT_IMAGE_MAX_SIZE)

        mime_type = magic.from_buffer(upload.read(1024), mime=True)
        if not mime_type in ('image/png', 'image/jpeg', 'image/gif'):
            error = _('Only PNG, JPEG and GIF files are allowed.')
    else:
        error = _('Please select a file to upload.')

    if error:
        return HttpResponse(
            response_str.format(func_num, '', error.encode('utf8')),
            status=400)
    else:
        attachment = Attachment(gprot=gprot, mime_type=mime_type)
        attachment.save() # saved here to set the primary key
        attachment.file = upload
        attachment.save()
        return HttpResponse(
                    response_str.format(func_num, attachment.file.url, ''))

@login_required
def publish_gprot(request, gprot_pk):
    gprot = get_object_or_404(GProt, pk=gprot_pk)
    if gprot.author != request.user:
        raise PermissionDenied('You are not the owner')
    if gprot.is_pdf and not gprot.content_pdf:
        raise PermissionDenied('No document has been uploaded yet')

    if request.method == 'POST' and 'authorship' in request.POST:
        if request.POST['authorship'] == 'purge':
            gprot.author = None
        gprot.published = True
        gprot.save()
        notify_users(gprot, request)
        return redirect('gprot_view', gprot.pk)

    return render(request, 'gprot/publish.html', {
        'gprot': gprot
    })

def send_notification_email(gprot, notification, request):
    url = reverse('mafiasi.gprot.views.view_gprot', args=(gprot.pk,))
    email_content = render_to_string('gprot/notification_email.txt', {
        'notification': notification,
        'url': request.build_absolute_uri(url)
    })
    try:
        send_mail(_('New memory minutes for "%(coursename)s"'
            % {'coursename': gprot.course.name}).encode('utf8'),
                email_content.encode('utf8'),
                None,
                [notification.user.email])
    except SMTPException:
        client.captureException()

def notify_users(gprot, request):
    '''
    Notify users if a GProt matching one of their queries is published.
    '''
    notified_users = []
    for notification in Notification.objects.select_related() \
                        .filter(course_id__exact=gprot.course.pk):
        if notification.user not in notified_users:
            send_notification_email(gprot, notification, request)
            notified_users.append(notification.user)

    for notification in Notification.objects.select_related() \
                        .filter(course_id=None):
        if notification.user not in notified_users and fuzz.partial_ratio(
                        notification.course_query, gprot.course.name) >= 67:
                send_notification_email(gprot, notification, request)
                notified_users.append(notification.user)



@login_required
def notifications(request):
    autocomplete_courses = {'tokens': []}
    insert_autocomplete_courses(autocomplete_courses)

    error = False

    if request.method == 'POST':
        notification = Notification(added_date=date.today(),
                                         user=request.user)
        if 'course' in request.POST:
            course_pk = request.POST['course']
            try:
                course = Course.objects.get(pk=course_pk)
                notification.course = course
            except Course.DoesNotExist:
                error = True
        elif 'course_name' in request.POST:
            notification.course_query = request.POST['course_name']
        else:
            error = True

        if Notification.objects.filter(course=notification.course,
                                       course_query=notification.course_query,
                                       user=notification.user).exists():
            error = True

        if not error:
            notification.save()

    notifications = Notification.objects.select_related() \
        .filter(user=request.user) \
        .order_by('-added_date')

    return render(request, 'gprot/notifications.html', {
        'notifications': notifications,
        'autocomplete_course_json': json.dumps(autocomplete_courses),
        'error': error
    })

@login_required
def delete_notification(request, notification_pk):
    notification = get_object_or_404(Notification, pk=notification_pk)
    if request.user != notification.user:
        raise PermissionDenied('You are not the owner')

    notification.delete()

    return redirect('gprot_notifications')

@login_required
def reminders(request):
    autocomplete_courses = {'tokens': []}
    insert_autocomplete_courses(autocomplete_courses)

    error = False

    if request.method == 'POST':
        reminder = Reminder(user=request.user)

        if 'course' in request.POST and request.POST['course'].isdigit():
            course = get_object_or_404(Course, pk=request.POST['course'])
        elif 'course_name' in request.POST:
            course_name = request.POST.get('course_name', '').strip()
            course = Course(name=course_name, short_name='')
        else:
            course = None

        exam_date_str = request.POST.get('exam_date', '')
        try:
            exam_date_t = time.strptime(exam_date_str, '%Y-%m-%d')
            exam_date = date(exam_date_t.tm_year, exam_date_t.tm_mon,
                                 exam_date_t.tm_mday)

            if Reminder.objects.filter(exam_date=exam_date,
                                       course=course,
                                       user=request.user).exists():
                error = True

        except ValueError:
            error = True

        if not error:
            reminder.exam_date = exam_date
            reminder.course = course
            reminder.save()

    reminders = Reminder.objects.select_related() \
        .filter(user=request.user) \
        .order_by('exam_date')

    return render(request, 'gprot/reminders.html', {
        'reminders': reminders,
        'autocomplete_course_json': json.dumps(autocomplete_courses),
        'error': error
    })

@login_required
def delete_reminder(request, reminder_pk):
    reminder = get_object_or_404(Reminder, pk=reminder_pk)
    if request.user != reminder.user:
        raise PermissionDenied('You are not the owner')

    reminder.delete()

    return redirect('gprot_reminders')
