from django.conf.urls import patterns, include, url
from django.shortcuts import redirect

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', lambda req: redirect('dashboard_index'), name='home'),
    url(r'^base/', include('mafiasi.base.urls')),
    url(r'^registration/', include('mafiasi.registration.urls')),
    url(r'^dashboard/', include('mafiasi.dashboard.urls')),
    url(r'^jabber/', include('mafiasi.jabber.urls')),
    url(r'^mumble/', include('mafiasi.mumble.urls')),
    url(r'^wiki/', include('mafiasi.wiki.urls')),
    url(r'^cal/', include('mafiasi.cal.urls')),
    url(r'^dav/', include('mafiasi.cal.davurls')),
    url(r'^pks/', include('mafiasi.ksp.urls')),

    url(r'^login$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {
        'next_page': '/'
    }, name='logout'),

    (r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
