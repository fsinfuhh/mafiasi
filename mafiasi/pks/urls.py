from django.conf.urls import patterns, url

urlpatterns = patterns('mafiasi.pks.views',
    url(r'^all_keys$', 'all_keys', name='pks_all_keys'),
    url(r'^my_keys$', 'my_keys', name='pks_my_keys'),
    url(r'^upload_keys$', 'upload_keys', name='pks_upload_keys'),
    url(r'^unassign_keys$', 'unassign_keys', name='pks_unassign_keys'),
)
