from django.conf import settings

from mafiasi.base.models import Mafiasi


def create_mafiasi_account(username, email, first_name, last_name, account=None,
                           yeargroup=None, is_student=False, is_guest=False):
    # Sometimes, mail addresses can be given to new students. In that case, reset their email.
    try:
        conflicting_user = Mafiasi.objects.get(real_email=email)
        conflicting_user.real_email = conflicting_user.username + '@' + settings.INVALID_MAIL_DOMAIN
        conflicting_user.save()
    except Mafiasi.DoesNotExist:
        pass

    mafiasi = Mafiasi(username=username)
    if first_name and last_name:
        mafiasi.first_name = first_name
        mafiasi.last_name = last_name
    if settings.MAILCLOAK_DOMAIN:
        mafiasi.email = '{}@{}'.format(username, settings.MAILCLOAK_DOMAIN)
    else:
        mafiasi.email = email
    mafiasi.real_email = email
    mafiasi.yeargroup = yeargroup
    mafiasi.is_guest = is_guest
    if account:
        mafiasi.account = account

    return mafiasi
