from django.conf.urls import include, url
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


import mafiasi.base.urls, mafiasi.registration.urls, mafiasi.dashboard.urls, \
    mafiasi.mumble.urls, mafiasi.wiki.urls, mafiasi.groups.urls,\
    mafiasi.etherpad.urls, mafiasi.guests.urls, mafiasi.owncloud.urls

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
    url(r'^groups/', include(mafiasi.groups.urls)),
    url(r'^etherpad/', include(mafiasi.etherpad.urls)),
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

if 'mafiasi.mail' in settings.INSTALLED_APPS:
    import mafiasi.mail.urls
    urlpatterns += [
        url(r'^mail/', include(mafiasi.mail.urls)),
    ]

if 'mafiasi.mailinglist' in settings.INSTALLED_APPS:
    import mafiasi.mailinglist.urls
    urlpatterns += [
        url(r'^mailinglist/', include(mafiasi.mailinglist.urls)),
    ]

if 'mafiasi.wiki' in settings.INSTALLED_APPS:
    import mafiasi.wiki.urls
    urlpatterns += [
        url(r'^wiki/', include(mafiasi.wiki.urls)),
    ]

if 'mafiasi.mumble' in settings.INSTALLED_APPS:
    import mafiasi.mumble.urls
    urlpatterns += [
        url(r'^mumble/', include(mafiasi.mumble.urls)),
    ]

if 'mafiasi.discourse' in settings.INSTALLED_APPS:
    import mafiasi.discourse.urls
    urlpatterns += [
        url(r'^discourse/', include(mafiasi.discourse.urls)),
    ]

if 'mafiasi.teaching' in settings.INSTALLED_APPS:
    import mafiasi.teaching.urls
    urlpatterns += [
        url(r'^teaching/', include(mafiasi.teaching.urls)),
    ]

if 'mafiasi.gprot' in settings.INSTALLED_APPS:
    import mafiasi.gprot.urls
    urlpatterns += [
        url(r'^gprot/', include(mafiasi.gprot.urls)),
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
