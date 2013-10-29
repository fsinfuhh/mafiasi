from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.ksp.views',
    url(r'^$', 'index', name='ksp_index'),
    url(r'^plain/all$', 'plain_all', name='ksp_plain_all'),
    url(r'^list_keys$', 'list_keys', name='ksp_list_keys'),
    url(r'^list_keys/(?P<ksp>\w+)$', 'list_keys', name='ksp_list_keys_party'),
    url(r'^show_graph$', 'show_graph', name='ksp_show_graph'),
    url(r'^add_key$', 'add_key_form', name='ksp_add_key_form'),
    url(r'^lookup$', 'hkp_lookup', name='ksp_hkp_lookup'),
    url(r'^add$', 'hkp_add_key', name='ksp_add_key'),
)
