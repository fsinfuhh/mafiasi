import random

from django.utils import translation
from django.utils.timezone import get_current_timezone, localdate, now


class SpecialDayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session["specialDay"] = False
        request.session["specialDayClasses"] = ""

        # get date in current timezone
        n = localdate(now(), get_current_timezone())

        # check if user disabled special day surprises via cookie
        if not request.COOKIES.get("disable-specialday", False):
            # first of april (april fools)
            if n.day == 1 and n.month == 4:
                request.session["specialDay"] = "aprilfools"
                option = random.randint(0, 1)
                if option == 0:
                    request.session["specialDayClasses"] += " first-of-april"
                elif option == 1:
                    translation.activate("en-uwu")
                    request.LANGUAGE_CODE = translation.get_language()

            # winter season
            if n.month == 12 and n.day >= 10:
                request.session["specialDay"] = "winter"
                request.session["specialDayClasses"] += " snowing"

        # call view
        response = self.get_response(request)

        return response
