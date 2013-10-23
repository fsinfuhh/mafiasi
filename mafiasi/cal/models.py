import random
from datetime import date, datetime, time

import pytz
import caldav
from caldav import dav
from vobject.icalendar import RecurringComponent

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

TYPE_CHOICES = (
    ('ics', _('Calendar')),
    ('vcf', _('Contact list'))
)

COLORS = ['eeffaa', 'ffeeaa', 'ffddaa', 'ffccaa', 'ffaaaa', 'ffaacc', 'ffaaee',
          'eeaaff', 'aaffff', 'aaddff', 'aaffff', 'aaffdd', 'aaffaa', 'ddffaa',
          'ffffaa']

class CalendarManager(models.Manager):
    def sync(self, username):
        url = u'{0}{1}/'.format(settings.CALDAV_BASE_URL, username)
        url = url.encode('utf-8')
        client = caldav.DAVClient(url)
        principal = caldav.Principal(client, url)
        calendars = principal.calendars()
        cal_objs = []
        for calendar in calendars:
            path = calendar.url.path
            try:
                _user, name = path.strip('/').split('/')[-2:]
                if name.endswith('.ics'):
                    name = name[:-4]
            except ValueError:
                continue
            try:
                cal_obj = Calendar.objects.get(username=username,
                                               name=name,
                                               type='ics')
                created = False
            except DavObject.DoesNotExist:
                cal_obj = Calendar(username=username, name=name, type='ics')
                created = True

            props = calendar.get_properties([dav.DisplayName()])
            try:
                display_name = props[dav.DisplayName().tag]
            except KeyError:
                display_name = name

            if display_name.endswith('.ics'):
                display_name = display_name[:-4]

            if cal_obj.display_name != display_name or created:
                cal_obj.display_name = display_name
                cal_obj.save()

            if created:
                User = get_user_model()
                try:
                    user = User.objects.get(username=username)
                    random_color = random.choice(COLORS)
                    ShownCalendar.objects.create(user=user,
                                                 calendar=cal_obj,
                                                 display_name=display_name,
                                                 color=random_color)
                except User.DoesNotExist:
                    pass
            cal_objs.append(cal_obj)

class DavObject(models.Model):
    username = models.CharField(max_length=120)
    name = models.CharField(max_length=120)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    is_public = models.BooleanField(default=False)
    display_name = models.CharField(max_length=120)

    class Meta:
        unique_together = ('username', 'name', 'type')

    def __unicode__(self):
        return u'{0}/{1}.{2}'.format(self.username, self.name, self.type)

    def has_access(self, user, write=False):
        if user is not None and self.username == user.username:
            return True
        if not write and self.is_public:
            return True
        q = DavObjectPermission.objects.filter(user=user, object=self)
        if write:
            q = q.filter(can_write=True)
        return q.count() >= 1

class Calendar(DavObject):
    class Meta:
        proxy = True

    objects = CalendarManager()
    
    def get_caldav_url(self):
        return u'{0}{1}/{2}.ics/'.format(settings.CALDAV_BASE_URL,
                                         self.username,
                                         self.name).encode('utf-8')

    def get_caldav_display_url(self):
        return u'{0}{1}/{2}.ics/'.format(settings.CALDAV_DISPLAY_URL,
                                         self.username,
                                         self.name).encode('utf-8')

    def get_events(self, start, end=None):
        event_list = []
            
        # Date range should be datetime objects ...
        if isinstance(start, date):
            zero_time = time(0, 0, 0, 0, tzinfo=pytz.UTC)
            start = datetime.combine(start, zero_time)
        if isinstance(end, date):
            max_time = time(23, 59, 59, 999999, tzinfo=pytz.UTC)
            end = datetime.combine(end, max_time)

        # ... and those datetime objects should be timezone aware
        if start.tzinfo is None:
            start = datetime.astimezone(pytz.UTC)
        if end.tzinfo is None:
            end = datetime.astimezone(pytz.UTC)

        calendar_url = self.get_caldav_url()
        client = caldav.DAVClient(calendar_url)
        calendar = caldav.Calendar(client, calendar_url)
        for vcal in calendar.date_search(start, end):
            for comp in vcal.instance.components():
                # RecurringComponent might be misleading, but vobject
                # returns all events as RecurringComponent objects
                if isinstance(comp, RecurringComponent):
                    self._handle_event_component(start, end, comp, event_list)
        return event_list
    
    def _handle_event_component(self, start, end, comp, event_list):
        event = {
            'uid': comp.uid.value,
            'summary': comp.summary.value,
            'dtstart': comp.dtstart.value,
            'dtend': comp.dtend.value,
            'location': None,
            'description': None
        }
        try:
            event['location'] = comp.location.value
        except AttributeError:
            pass
        try:
            event['description'] = comp.description.value
        except AttributeError:
            pass
        
        # If we have no recurrence rules, we can just add the
        # event and continue with the next
        recurr_rruleset = comp.getrruleset(True)
        if recurr_rruleset is None:
            event_list.append(event)
        else:
            self._handle_event_recurrence(
                    start, end, comp, recurr_rruleset, event, event_list)

    def _handle_event_recurrence(self, start, end, comp, recurr_rruleset,
                                 event_tpl, event_list):
        is_allday = not isinstance(comp.dtstart.value, datetime)
        recurr_start = start
        recurr_end = start if end is None else end
        # All-day-events need timezone-naive objects for recurrence
        # because date objects are per definition timezone-naive
        if is_allday:
            recurr_start = recurr_start.replace(tzinfo=None)
            recurr_end = recurr_end.replace(tzinfo=None)
        
        recurrs = recurr_rruleset.between(recurr_start, recurr_end)
        duration = comp.dtend.value - comp.dtstart.value
        for event_start in recurrs:
            # Recurrence rules will only return datetime -- convert
            # it back to date object on all-day events
            if is_allday:
                event_start = event_start.date()
            event = event_tpl.copy()
            event['dtstart'] = event_start
            event['dtend'] = event_start + duration
            event_list.append(event)

class DavObjectPermission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    object = models.ForeignKey(DavObject)
    can_write = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'object')

    def __unicode__(self):
        mode = 'RW' if self.can_write else 'R'
        return u'{0} on {1} ({2})'.format(self.user, self.object, mode)

class ShownCalendar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    calendar = models.ForeignKey(Calendar)
    display_name = models.CharField(max_length=120)
    color = models.CharField(max_length=6)

    class Meta:
        unique_together = ('user', 'calendar')

    def __unicode__(self):
        return u'{0}: {1} [{2}]'.format(self.user, self.calendar, self.color)
