from django.db import connection

# How to generate lock_id:
# 1) int(hashlib.sha256('somestr').hexdigest()[:8], 16) - (1 << 31)
# 2) If already used in some application, increase by 1

class AdvisoryLock(object):
    def __init__(self, lock_id, object_id):
        self.lock_id = lock_id
        self.object_id = object_id

    def __enter__(self):
        c = connection.cursor()
        c.execute('SELECT pg_advisory_lock(%s, %s);',
                  (self.lock_id, self.object_id))

    def __exit__(self, exc_type, exc_value, exc_traceback):
        c = connection.cursor()
        c.execute('SELECT pg_advisory_unlock(%s, %s);',
                  (self.lock_id, self.object_id))
        return False
