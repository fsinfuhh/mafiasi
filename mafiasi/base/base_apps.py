from django.apps import AppConfig


class BaseService(AppConfig):
    title = '<title-not-set>'       # translated service title
    description = '<description not set>'       # translated description of this service
    link = '/'      # absolute url where this service is at
    image = '/favicon.ico'      # image resource which can be resolved as static asset
