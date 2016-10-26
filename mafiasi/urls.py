from django.conf.urls import include, url
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


import mafiasi.base.urls, mafiasi.registration.urls, mafiasi.dashboard.urls, mafiasi.discourse.urls,\
    mafiasi.mumble.urls, mafiasi.wiki.urls, mafiasi.groups.urls,\
    mafiasi.etherpad.urls, mafiasi.gprot.urls, mafiasi.teaching.urls, mafiasi.mail.urls, mafiasi.mailinglist.urls,\
    mafiasi.guests.urls, mafiasi.owncloud.urls

import django.contrib.auth.views
import django.conf.urls.i18n
import django.contrib.admindocs.urls

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', lambda req: redirect('dashboard_index'), name='home'),
    url(r'^base/', include(mafiasi.base.urls)),
    url(r'^registration/', include(mafiasi.registration.urls)),
    url(r'^dashboard/', include(mafiasi.dashboard.urls)),
    url(r'^discourse/', include(mafiasi.discourse.urls)),
    url(r'^mumble/', include(mafiasi.mumble.urls)),
    url(r'^wiki/', include(mafiasi.wiki.urls)),
    url(r'^groups/', include(mafiasi.groups.urls)),
    url(r'^etherpad/', include(mafiasi.etherpad.urls)),
    url(r'^gprot/', include(mafiasi.gprot.urls)),
    url(r'^teaching/', include(mafiasi.teaching.urls)),
    url(r'^mail/', include(mafiasi.mail.urls)),
    url(r'^mailinglist/', include(mafiasi.mailinglist.urls)),
    url(r'^guests/', include(mafiasi.guests.urls)),
    url(r'^owncloud/', include(mafiasi.owncloud.urls)),

    url(r'^login$', django.contrib.auth.views.login, name='login'),
    url(r'^logout$', django.contrib.auth.views.logout, {
        'next_page': '/'
    }, name='logout'),

    url(r'^i18n/', include(django.conf.urls.i18n)),

    url(r'^admin/doc/', include(django.contrib.admindocs.urls)),
    url(r'^admin/', include(admin.site.urls)),
]

if 'mafiasi.pks' in settings.INSTALLED_APPS:
    import mafiasi.pks.urls
    urlpatterns += [
        url(r'^pks/', include(mafiasi.pks.urls)),
    ]

if 'mafiasi.jabber' in settings.INSTALLED_APPS:
    import mafiasi.jabber.urls
    urlpatterns += [
        url(r'^jabber/', include(mafiasi.jabber.urls)),
    ]

if 'oauth2_provider' in settings.INSTALLED_APPS:
    import oauth2_provider.urls
    urlpatterns += [
        url(r'^oauth/', include(oauth2_provider.urls, namespace='oauth2_provider')),
    ]

if 'mafiasi.mattermost' in settings.INSTALLED_APPS:
    import mafiasi.mattermost.urls
    urlpatterns += [
        url(r'^mattermost/', include(mafiasi.mattermost.urls)),
    ]


if settings.DEBUG:
    urlpatterns += \
        static(r'^media/(?P<path>.*)$', document_root=settings.MEDIA_ROOT) +\
        static(r'^mathjax/(?P<path>.*)$', document_root=settings.MATHJAX_ROOT);
