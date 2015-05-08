from mafiasi.base.models import Mafiasi

SIMILARTIY_THRESHOLD = 0.3
RESULT_LIMIT = 10

def autocomplete_users(term):
    terms = term.strip().split()
    if len(terms) == 0:
        return []

    table_name = Mafiasi._meta.db_table
    base_query = 'SELECT * FROM {} WHERE '.format(table_name)
    
    if len(terms) == 1:
        cond = ('similarity(username, %s) > %s OR '
                'similarity(first_name, %s) > %s OR '
                'similarity(last_name, %s) > %s')
        params = [term, SIMILARTIY_THRESHOLD,
                  term, SIMILARTIY_THRESHOLD,
                  term, SIMILARTIY_THRESHOLD]
    else:
        # If a user enters two terms, both should match somehow
        cond = ('(similarity(username, %s) > %s AND similarity(first_name, %s) > %s) OR '
                '(similarity(username, %s) > %s AND similarity(last_name, %s) > %s) OR '
                '(similarity(first_name, %s) > %s AND similarity(last_name, %s) > %s)')
        params = [terms[0], SIMILARTIY_THRESHOLD, terms[1], SIMILARTIY_THRESHOLD,
                  terms[0], SIMILARTIY_THRESHOLD, terms[1], SIMILARTIY_THRESHOLD,
                  terms[0], SIMILARTIY_THRESHOLD, terms[1], SIMILARTIY_THRESHOLD]
    
    limit = ' LIMIT %s'
    params.append(RESULT_LIMIT+1)

    sql_query = base_query + cond + limit
    users = list(Mafiasi.objects.raw(sql_query, params))

    # We only want to show results of the users search term restricted
    # the results enough, so that it is more difficult to fetch all users
    if len(users) > RESULT_LIMIT:
        return []
    return users
