from mafiasi.base.models import Mafiasi

def create_mafiasi_account(username, email, first_name, last_name, account=None,
                           yeargroup=None, is_student=False, is_guest=False):
    mafiasi = Mafiasi(username=username)
    if first_name and last_name:
        mafiasi.first_name = first_name
        mafiasi.last_name = last_name
    mafiasi.email = email
    mafiasi.yeargroup = yeargroup

    return mafiasi
