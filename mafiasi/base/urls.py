from django.conf.urls import url

from .views import imprint, data_privacy_statement, technical_info, licenses, problems, autocomplete

include_at_top = True

urlpatterns = [
    url(r'^imprint$', imprint, name='base_imprint'),
    url(r'^technical_info$', technical_info, name='base_technical_info'),
    url(r'^data_privacy_statement$', data_privacy_statement, name='base_data_privacy_statement'),
    url(r'^licenses$', licenses, name='base_licenses'),
    url(r'^problems$', problems, name='base_problems'),
    url(r'^autocomplete$', autocomplete, name='base_autocomplete'),
]
