from creole import creole2html

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.safestring import mark_safe

class News(models.Model):
    title = models.CharField(max_length=120)
    teaser = models.TextField()
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    frontpage = models.BooleanField(db_index=True, default=False)
    published = models.BooleanField(default=False)

    class Meta(object):
        verbose_name = 'news'
        verbose_name_plural = 'news'
    
    def __unicode__(self):
        return '{0}: {1}'.format(self.created_at, self.title)

    def render_teaser(self):
        return mark_safe(creole2html(self.teaser, method='xhtml'))
    
    def render_text(self):
        return mark_safe(creole2html(self.text, method='xhtml'))

class Panel(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()
    position = models.IntegerField()
    shown = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    def render_content(self):
        return mark_safe(creole2html(self.content, method='xhtml'))
