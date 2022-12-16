import django.dispatch

class CollectMail(object):
    pass

class CollectServer(object):
    pass

collect_mailaddresses = django.dispatch.Signal()
mailaddresses_known = django.dispatch.Signal()
collect_servers = django.dispatch.Signal()
