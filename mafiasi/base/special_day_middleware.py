from django.utils import translation
from django.utils.timezone import now, localdate, get_current_timezone


class SpecialDayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get date in current timezone
        n = localdate(now(), get_current_timezone())

        # first of april (april fools)
        if n.day == 1 and n.month == 4:
            translation.activate('en-uwu')
            request.LANGUAGE_CODE = translation.get_language()

        # call view
        response = self.get_response(request)

        return response
