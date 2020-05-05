from django.conf.urls import include, url
from django.http import HttpResponse
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
    url(r'^login', auth_views.LoginView.as_view(), name='login', ),
    url(r'^logout', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    url(r'^i18n/', include(django.conf.urls.i18n)),

    url(r'^admin/doc/', include(django.contrib.admindocs.urls)),
    url(r'^admin/', admin.site.urls),
]


if 'oauth2_provider' in settings.INSTALLED_APPS:
    import oauth2_provider.urls
    urlpatterns += [
        url(r'^oauth/', include(oauth2_provider.urls, namespace='oauth2_provider')),
    ]


for app in apps.get_app_configs():
    if app.name.startswith('mafiasi.'):
        try:
            urls = importlib.import_module(f'{app.name}.urls', '')
            include_at_top = getattr(urls, 'include_at_top', False)
            if include_at_top:
                urlpatterns.append(url('', include(urls), name=app.name))
                print(f'including {app.verbose_name.lower()} urls at root')
            else:
                prefix = app.name.split('.')[-1]
                urlpatterns.append(url(f'{prefix}/', include(urls), name=app.name))
                print(f'including {app.verbose_name} urls under /{prefix}/')
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


def handler404(request, exception):
    try:
        apps.get_app_config('wiki')
        path = str(request.path).replace('/', '', 1)
        if '/' in path:
            return HttpResponse('Page not found')

        from mafiasi.wiki.views import redirect_to_wiki
        return redirect_to_wiki(request, path)

    except LookupError as e:
        return HttpResponse('Page not found')
