from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', index, name='pks_index'),
    url(r'^all_keys$', all_keys, name='pks_all_keys'),
    url(r'^my_keys$', my_keys, name='pks_my_keys'),
    url(r'^autocomplete_keys$', autocomplete_keys,
            name='pks_autocomplete_keys'),
    url(r'^assign_keyid$', assign_keyid, name='pks_assign_keyid'),
    url(r'^upload_keys$', upload_keys, name='pks_upload_keys'),
    url(r'^unassign_keys$', unassign_keys, name='pks_unassign_keys'),
    url(r'^graph$', graph, name='pks_graph'),
    url(r'^key/([A-Fa-f0-9]{16})$', show_key, name='pks_show_key'),
    url(r'^key/([A-Fa-f0-9]{16}).asc$', show_key, {'raw': True},
            name='pks_show_key_raw'),
    url(r'^party/$', party_list, name='pks_party_list'),
    url(r'^party/(\d+)/keys$', party_keys, name='pks_party_keys'),
    url(r'^party/(\d+)/keys.asc$', party_keys_export,
            name='pks_party_keys_export'),
    url(r'^party/(\d+)/participate$', party_participate,
            name='pks_party_participate'),
    url(r'^party/(\d+)/graph$', graph, name='pks_party_graph'),
    url(r'^party/(\d+)/missing$', party_missing_signatures,
            name='pks_party_missing_signatures'),
    url(r'^search$', search, name='pks_search'),
    url(r'^add$', hkp_add_key, name='pks_hkp_add'),
    url(r'^lookup$', hkp_lookup, name='pks_hkp_lookup'),
]
