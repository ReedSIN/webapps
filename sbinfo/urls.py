from django.conf.urls import *

urlpatterns = patterns(
  'webapps.sbinfo.views',
  (r'^/?$','index'),
  (r'^submit/?$','sbinfo_submit'),
  (r'^my_applications/delete/(?P<application_id>\d+)/?$','delete_application'),
  (r'^admin/?$','admin_index'),
  (r'^admin/create/?$','create_position'),
  (r'^admin/edit/(?P<position_id>\d*)/?$','edit_position'),
  (r'^admin/delete/(?P<position_id>\d+)/?$','delete_position'),
  (r'^admin/position-(?P<position_id>\d+)/?$','position_application_list'),
  (r'^admin/position-(?P<position_id>\d+)/app-(?P<application_id>\d+)/?$','position_application_detail'),
)
