from django.conf.urls import include, url
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.apps import apps

import importlib

import django.contrib.auth.views
import django.conf.urls.i18n
import django.contrib.admindocs.urls

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', lambda req: redirect('dashboard_index'), name='home'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login', ),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    url(r'^i18n/', include(django.conf.urls.i18n)),

    url(r'^admin/doc/', include(django.contrib.admindocs.urls)),
    url(r'^admin/', admin.site.urls),
]

for app in apps.get_app_configs():
    if app.name.startswith('mafiasi.'):
        try:
            urls = importlib.import_module(f'{app.name}.urls', '')
            include_at_top = getattr(urls, 'include_at_top', False)
            if include_at_top:
                urlpatterns.append(url('', include(urls), name=app.name))
            else:
                urlpatterns.append(url(f'{app.verbose_name.lower()}/', include(urls), name=app.name))
        except ImportError as e:
            pass


if settings.DEBUG:
    urlpatterns += \
        static(r'^media/(?P<path>.*)$', document_root=settings.MEDIA_ROOT) +\
        static(r'^mathjax/(?P<path>.*)$', document_root=settings.MATHJAX_ROOT)


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    return render(request, '500.html', status=500)
