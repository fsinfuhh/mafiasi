from django.conf.urls import path, re_path

from .views import *

urlpatterns = [
    path('', index, name='pks_index'),
    path('all_keys', all_keys, name='pks_all_keys'),
    path('my_keys', my_keys, name='pks_my_keys'),
    path('autocomplete_keys', autocomplete_keys,
            name='pks_autocomplete_keys'),
    path('assign_keyid', assign_keyid, name='pks_assign_keyid'),
    path('upload_keys', upload_keys, name='pks_upload_keys'),
    path('unassign_keys', unassign_keys, name='pks_unassign_keys'),
    path('graph', graph, name='pks_graph'),
    re_path(r'^key/([A-Fa-f0-9]{16})$', show_key, name='pks_show_key'),
    re_path(r'^key/([A-Fa-f0-9]{16}).asc$', show_key, {'raw': True},
            name='pks_show_key_raw'),
    path('party/', party_list, name='pks_party_list'),
    re_path(r'^party/(\d+)/keys$', party_keys, name='pks_party_keys'),
    re_path(r'^party/(\d+)/keys.asc$', party_keys_export,
            name='pks_party_keys_export'),
    re_path(r'^party/(\d+)/participate$', party_participate,
            name='pks_party_participate'),
    re_path(r'^party/(\d+)/graph$', graph, name='pks_party_graph'),
    re_path(r'^party/(\d+)/missing$', party_missing_signatures,
            name='pks_party_missing_signatures'),
    path('search', search, name='pks_search'),
    path('add', hkp_add_key, name='pks_hkp_add'),
    path('lookup', hkp_lookup, name='pks_hkp_lookup'),
]
