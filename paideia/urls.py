from django.conf.urls import *

VALID_FACTORS = [
  'student',
]

urlpatterns = patterns(
  'webapps.paideia.views',
  (r'^$', 'index'),
  (r'^alum/?$', 'alum_index'),
  (r'^add/?$', 'add_page'),
  (r'^edit/?$', 'edit_page'),
  (r'^admin/?$', 'admin_page'),
  (r'^search', 'search_page'),
  (r'^register/?$', 'register_class'),
  (r'^edit_class/?$', 'edit_class'),
  (r'^delete$', 'delete_class'),
  (r'^count/?$', 'class_count'),
  (r'^listing/?$', 'listing'),
  (r'^description/?$', 'description'),
  (r'^ajax_form/?$', 'ajax_edit_form'),
)
