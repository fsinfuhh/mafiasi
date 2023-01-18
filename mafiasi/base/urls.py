from django.urls import path

from .views import (
    autocomplete,
    data_privacy_statement,
    imprint,
    licenses,
    problems,
    technical_info,
)

urlpatterns = [
    path("imprint", imprint, name="base_imprint"),
    path("technical_info", technical_info, name="base_technical_info"),
    path("data_privacy_statement", data_privacy_statement, name="base_data_privacy_statement"),
    path("licenses", licenses, name="base_licenses"),
    path("problems", problems, name="base_problems"),
    path("autocomplete", autocomplete, name="base_autocomplete"),
]
