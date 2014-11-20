import django.dispatch

class CollectMail(object):
    pass

class CollectServer(object):
    pass

collect_mailaddresses = django.dispatch.Signal(providing_args=["addresses"])
collect_servers = django.dispatch.Signal(providing_args=["servers"])
