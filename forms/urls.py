from django.conf.urls import *

urlpatterns = patterns(
  'webapps.forms.views',
  (r'^$','anonymous_form_list'),
  (r'^view/(?P<form_model_id>\d+)/?$','anonymous_form_detail'),
  (r'^my_forms/?$','my_forms'),
  (r'^my_forms/edit/(?P<form_model_id>\d*)/?$','edit_my_form'),
  (r'^my_forms/clear/(?P<form_model_id>\d+)/?$','clear_my_form'),
  (r'^my_forms/delete/(?P<form_model_id>\d+)/?$','delete_my_form'),
  (r'^my_forms/results/(?P<form_model_id>\d+)/?$','result_list'),
  (r'^my_forms/results/\d+/(?P<form_data_id>\d+)/?$','result_detail'),
)
