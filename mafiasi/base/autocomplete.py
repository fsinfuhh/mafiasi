from __future__ import unicode_literals

from mafiasi.base.models import Mafiasi

RESULT_LIMIT = 5
MIN_LENGTH = 3

def autocomplete_users(term):
    """Autocomplete users.
    
    If we have only one term, we search the fields username (full),
    username (without year prefix), first_name and last_name. For two
    terms we assume it is first_name, last_name. The first term must
    always be MIN_LENGTH long.

    For queries returning more than RESULT_LIMIT entries, entries are
    ignored. Sometimes this results in strange results, but makes
    crawling the database harder.
    """
    terms = term.strip().lower().split()
    if len(terms) == 0:
        return []

    if len(terms[0]) < MIN_LENGTH:
        return []

    if len(terms) == 1:
        users = []
        dups = set()
        _add_nodup('username', terms[0], users, dups)
        _add_nodup("regexp_replace(username, '^([0-9]+|x)', '')", terms[0], users, dups)
        _add_nodup('lower(first_name)', terms[0], users, dups)
        _add_nodup('lower(last_name)', term[0], users, dups)
        
        # Always make sure we "autocomplete" a complete match for username
        try:
            exact_user = Mafiasi.objects.get(username=terms[0])
            if exact_user.pk not in dups:
                users.append(exact_user)
        except Mafiasi.DoesNotExist:
            pass

    else:
        query = ('SELECT * FROM base_mafiasi '
                 'WHERE lower(first_name) LIKE %s AND lower(last_name) LIKE %s '
                 'LIMIT %s')
        params = (terms[0] + '%', terms[1] + '%', RESULT_LIMIT + 1)
        users = list(Mafiasi.objects.raw(query, params=params))
        if len(users) > RESULT_LIMIT:
            users = []

    users.sort(key=_sort_key)
    return users

def _add_nodup(expr, term, users, dups):
    query = 'SELECT * FROM base_mafiasi WHERE {} LIKE %s LIMIT %s'.format(expr)
    params = (term + '%', RESULT_LIMIT + 1)
    special_users = list(Mafiasi.objects.raw(query, params=params))
    
    if len(special_users) <= RESULT_LIMIT:
        for user in special_users:
            if user.pk in dups:
                continue
            users.append(user)
            dups.add(user.pk)

def _sort_key(user):
    return (user.first_name, user.last_name, user.username)
