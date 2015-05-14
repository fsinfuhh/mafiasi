from mafiasi.base.models import Mafiasi

RESULT_LIMIT = 10

def autocomplete_users(term):
    terms = term.strip().split()
    if len(terms) == 0:
        return []

    if len(terms) == 1:
        users_username = list(Mafiasi.objects.filter(
                username__istartswith=terms[0])[:RESULT_LIMIT+1])
        users_first_name = list(Mafiasi.objects.filter(
                first_name__istartswith=terms[0])[:RESULT_LIMIT+1])
        users_last_name = list(Mafiasi.objects.filter(
                last_name__istartswith=terms[0])[:RESULT_LIMIT+1])

        users = []
        dups = set()
        _add_nodup(users, users_username, dups)
        _add_nodup(users, users_first_name, dups)
        _add_nodup(users, users_last_name, dups)
    else:
        users = list(Mafiasi.objects.filter(
                first_name__iexact=terms[0],
                last_name__istartswith=terms[1])[:RESULT_LIMIT+1])
        if len(users) > RESULT_LIMIT:
            users = []

    return users

def _add_nodup(users, special_users, dups):
    if len(special_users) <= RESULT_LIMIT:
        for user in special_users:
            if user.pk in dups:
                continue
            users.append(user)
            dups.add(user.pk)
