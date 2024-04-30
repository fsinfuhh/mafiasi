import random

from django.utils import translation
from django.utils.timezone import get_current_timezone, localdate, now


class SpecialDayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.session["specialDay"] = False
        request.session["specialFeatureClasses"] = ""
        request.session["specialFeatureDisabled"] = False
        feature = ""

        # check if user wants to persist feature for this session (or reset it)
        if request.GET.get("persistSpecialFeatureForThisSession", "undefined") == "true":
            request.session["specialFeaturePersist"] = True
        elif request.GET.get("persistSpecialFeatureForThisSession", "undefined") == "false":
            request.session["specialFeaturePersist"] = False

        # reset feature if persist is not true
        if not request.session.get("specialFeaturePersist", False):
            request.session["specialFeature"] = False

        # get date in current timezone
        n = localdate(now(), get_current_timezone())

        # check if user disabled special day surprises via cookie
        if request.COOKIES.get("disable-special", False):
            request.session["specialFeatureDisabled"] = True

        # check if user enabled feature manually via GET parameter
        elif request.GET.get("specialFeature", False):
            feature = request.GET.get("specialFeature", False)

        # check if feature is already set (if persisted and not reset above)
        elif request.session["specialFeature"]:
            feature = request.session["specialFeature"]

        else:
            # check if it's a special day

            # first of april (april fools)
            if n.day == 1 and n.month == 4:
                request.session["specialDay"] = "April Fools"
                option = random.randint(0, 2)
                if option == 0:
                    feature = "upsideDown"
                elif option == 1:
                    feature = "uwu"
                elif option == 2:
                    feature = "mafiasiPurple"
            # winter season
            if n.month == 12 and n.day >= 10:
                feature = "winter"
            # may day (tag der arbeit)
            if n.month == 5 and n.day == 1:
                feature = "mayDay"

        # make sure session hold the current feature
        request.session["specialFeature"] = feature

        # handle feature
        if feature == "upsideDown":
            request.session["specialFeatureClasses"] += " first-of-april"
        elif feature == "uwu":
            translation.activate("en-uwu")
            request.LANGUAGE_CODE = translation.get_language()
        elif feature == "mafiasiPurple":
            pass
        elif feature == "winter":
            pass

        # call view
        response = self.get_response(request)

        return response
