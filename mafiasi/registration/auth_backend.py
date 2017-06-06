from mafiasi.base.models import Mafiasi


class EmailOrUsernameModelBackend(object):
    def authenticate(self, username=None, password=None):
        if '@' in username:
            kwargs = {'real_email': username}
        else:
            kwargs = {'username': username}
        try:
            user = Mafiasi.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except Mafiasi.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Mafiasi.objects.get(pk=user_id)
        except Mafiasi.DoesNotExist:
            return None
