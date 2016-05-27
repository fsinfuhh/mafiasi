from django.conf.urls import url

from .views import autocomplete

urlpatterns = [
    url(r'^autocomplete$', autocomplete, name='wiki_autocomplete'),
]
