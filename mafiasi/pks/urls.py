from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.pks.views',
    url(r'^$', 'index', name='pks_index'),
    url(r'^all_keys$', 'all_keys', name='pks_all_keys'),
    url(r'^my_keys$', 'my_keys', name='pks_my_keys'),
    url(r'^upload_keys$', 'upload_keys', name='pks_upload_keys'),
    url(r'^unassign_keys$', 'unassign_keys', name='pks_unassign_keys'),
    url(r'^graph$', 'graph', name='pks_graph'),
    url(r'^key/([A-Fa-f0-9]{16})$', 'show_key', name='pks_show_key'),
    url(r'^key/([A-Fa-f0-9]{16}).asc$', 'show_key', {'raw': True},
            name='pks_show_key_raw'),
    url(r'^add$', 'hkp_add_key', name='pks_hkp_add'),
    url(r'^lookup$', 'hkp_lookup', name='pks_hkp_lookup'),
)
