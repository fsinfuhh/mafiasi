import django.dispatch

class CollectMail(object):
    pass

collect_mailaddresses = django.dispatch.Signal(providing_args=["addresses"])
