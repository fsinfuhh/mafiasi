class JabberRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'jabber':
            return 'jabber'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'jabber':
            return 'jabber'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'jabber' or \
           obj2._meta.app_label == 'jabber':
           return True
        return None

    def allow_migrate(self, db, model):
        if db == 'jabber_db':
            return model._meta.app_label == 'jabber'
        elif model._meta.app_label == 'jabber':
            return False
        return None
