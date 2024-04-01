import random

from django.utils import translation
from django.utils.timezone import get_current_timezone, localdate, now


class SpecialDayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session["specialDay"] = False
        request.session["specialFeature"] = False
        request.session["specialFeatureClasses"] = ""

        # get date in current timezone
        n = localdate(now(), get_current_timezone())

        # check if user disabled special day surprises via cookie
        if request.COOKIES.get("disable-special", False):
            request.session["specialFeature"] = "DISABLED"
        else:
            # first of april (april fools)
            if n.day == 1 and n.month == 4:
                request.session["specialDay"] = "April Fools"
                option = random.randint(0, 2)
                if option == 0:
                    request.session["specialFeature"] = "upsideDown"
                    request.session["specialFeatureClasses"] += " first-of-april"
                elif option == 1:
                    request.session["specialFeature"] = "uwu"
                    translation.activate("en-uwu")
                    request.LANGUAGE_CODE = translation.get_language()
                elif option == 2:
                    request.session["specialFeature"] = "mafiasiPurple"

            # winter season
            if n.month == 12 and n.day >= 10:
                request.session["specialFeature"] = "winter"

        # call view
        response = self.get_response(request)

        return response
