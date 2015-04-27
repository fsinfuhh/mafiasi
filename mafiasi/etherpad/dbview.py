from __future__ import unicode_literals

import json

from django.db import connections

def get_group_pads(group_names):
    """Get all group pads with timestamp in just 4 database queries.
    
    Example::
       {
           "ExampleGroup": [
               {
                   "name": "ExamplePad",
                   "atext": "This is the content",
                   "timestamp": 1430006749.42
               }, ...
            ], ...
       }
    """
    group_pads = {group_name: [] for group_name in group_names}
    conn = connections['etherpad']
    
    mapper_keys = tuple('mapper2group:{}'.format(name) for name in group_names)
    with conn.cursor() as c:
        c.execute("SELECT key, value FROM store WHERE key IN %s",
                  (mapper_keys, ))
        mapper_result = c.fetchall()

    groups = {}
    for key, value in mapper_result:
        try:
            groups[json.loads(value)] = key.split(':', 1)[1]
        except (ValueError, TypeError, IndexError):
            pass
    if not groups:
        return group_pads
    
    with conn.cursor() as c:
        c.execute("SELECT key, value FROM store WHERE key IN %s",
                  (tuple('group:' + group_id for group_id in groups), ))
        groups_result = c.fetchall()
    if not groups_result:
        return group_pads

    pad_keys = []
    for key, groups_json in groups_result:
        try:
            pads = json.loads(groups_json)['pads']
            if not isinstance(pads, dict):
                raise ValueError('Invalid pad list format')
            for pad in pads:
                pad_keys.append('pad:' + pad)
        except (ValueError, KeyError):
            continue
    if not pad_keys:
        return group_pads

    with conn.cursor() as c:
        c.execute("SELECT key, value FROM store WHERE key IN %s",
                  (tuple(pad_keys), ))
        pads_result = c.fetchall()
    rev2pad = {}
    rev_keys = []
    for key, pad_json in pads_result:
        # format is: pad:group_id$pad_name
        group_id, pad_name = key[4:].split('$', 1)
        try:
            pad = json.loads(pad_json)
        except ValueError:
            continue
        pad['name'] = pad_name
        pad['timestamp'] = 0
        if 'head' not in pad:
            continue
        rev_key = '{}:revs:{}'.format(key, pad['head'])
        rev_keys.append(rev_key)
        rev2pad[rev_key] = pad
        group = groups[group_id]
        group_pads[group].append(pad)

    if rev_keys:
        with conn.cursor() as c:
            c.execute("SELECT key, value FROM store WHERE key IN %s",
                      (tuple(rev_keys), ))
            revisions_result = c.fetchall()

        for key, revision_json in revisions_result:
            try:
                revision = json.loads(revision_json)
                try:
                    timestamp = float(revision['meta']['timestamp']) / 1000
                except TypeError:
                    # timestamp is None
                    timestamp = 0
            except (KeyError, ValueError):
                continue
            rev2pad[key]['timestamp'] = timestamp

    return group_pads
