from django.conf.urls.defaults import *

urlpatterns = patterns(
  'webapps.users.views',
  (r'^$', 'index'),
  (r'^lookup/?$', 'lookup_user'),
  (r'^update/(?P<user_id>\d+)/?', 'update_user'),
  (r'^edit/(?P<user_id>\d+)/?', 'edit_user'),
  (r'^add/?', 'add_users'),
  (r'^signators/?$', 'get_signators'),
  (r'^lazy-signators/?$', 'get_unregistered_signators'),
)
