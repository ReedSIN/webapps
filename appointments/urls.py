from django.conf.urls.defaults import *

urlpatterns = patterns(
  'webapps.appointments.views',
  (r'^$','index'),
  (r'^open_positions/?$','open_position_list'),
  (r'^open_positions/(?P<position_id>\d+)/?$','open_position_detail'),
  (r'^my_applications/?$','my_application_list'),
  (r'^my_applications/create/(?P<position_id>\d+)/?$','create_application'),
  (r'^my_applications/edit/(?P<application_id>\d*)/?$','edit_application'),
  (r'^my_applications/delete/(?P<application_id>\d+)/?$','delete_application'),
  (r'^admin/?$','admin_index'),
  (r'^admin/create/?$','create_position'),
  (r'^admin/create/(P<position_id>\d*)/?$','submit_new_position'),
  (r'^admin/edit/(?P<position_id>\d*)/?$','edit_position'),
  (r'^admin/delete/(?P<position_id>\d+)/?$','delete_position'),
  (r'^admin/position-(?P<position_id>\d+)/?$','position_application_list'),
  (r'^admin/position-(?P<position_id>\d+)/app-(?P<application_id>\d+)/?$','position_application_detail'),
  (r'^admin/submit/(?P<position_id>\d*)/?$','submit_new_position'),
  (r'^admin/edit/(?P<position_id>\d*)/?$','edit_position'),
)
