import importlib

import django.conf.urls.i18n
import django.contrib.admindocs.urls
import django.contrib.auth.views
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path("", lambda req: redirect("dashboard_index"), name="home"),
    path(
        "login/",
        auth_views.LoginView.as_view(),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),
    path("i18n/", include(django.conf.urls.i18n)),
    path("admin/doc/", include(django.contrib.admindocs.urls)),
    path("admin/", admin.site.urls),
]


if "oauth2_provider" in settings.INSTALLED_APPS:
    import oauth2_provider.urls

    urlpatterns += [
        path("oauth/", include(oauth2_provider.urls, namespace="oauth2_provider")),
    ]


for app in apps.get_app_configs():
    if app.name.startswith("mafiasi."):
        try:
            urls = importlib.import_module(f"{app.name}.urls", "")
            include_at_top = getattr(urls, "include_at_top", False)
            if include_at_top:
                urlpatterns.append(path("", include(urls), name=app.name))
            else:
                prefix = app.name.split(".")[-1]
                urlpatterns.append(path(f"{prefix}/", include(urls), name=app.name))
        except ImportError as e:
            pass


if settings.DEBUG:
    urlpatterns += static(r"^media/(?P<path>.*)$", document_root=settings.MEDIA_ROOT) + static(
        r"^mathjax/(?P<path>.*)$", document_root=settings.MATHJAX_ROOT
    )


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    return render(request, "500.html", status=500)


def handler404(request, exception):
    try:
        apps.get_app_config("wiki")
        path = str(request.path).replace("/", "", 1)
        if "/" in path:
            return HttpResponse("Page not found", status=404)

        from mafiasi.wiki.views import redirect_to_wiki

        return redirect_to_wiki(request, path)

    except LookupError as e:
        return HttpResponse("Page not found", status=404)
