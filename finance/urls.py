from django.conf.urls.defaults import *

urlpatterns = patterns(
  'webapps.finance.views',
  (r'^view_budgets/(?P<budget_id>\d+)/?$', 'view_one_budget'),
  (r'^view_budgets/?$', 'view_all_budgets'),
  (r'^view_budgets/respond/edit/(?P<budget_id>\d+)/?$', 'budget_respond_get'),
  (r'^view_budgets/respond/save/(?P<budget_id>\d+)/?$', 'budget_respond_post'),
  (r'^approved_budgets/?$', 'view_approved_budgets'),
  (r'^submit_budget/?$', 'create_budget'),
  (r'^submit_budget/create/?(?P<budget_id>\d*)/?$', 'edit_my_budget_post'),
  (r'^my_budgets/?$', 'my_budgets'),
  (r'^my_budgets/edit/(?P<budget_id>\d+)/?$', 'edit_my_budget'),
  (r'^my_budgets/save/(?P<budget_id>\d+)/?$', 'edit_my_budget_post'),
  (r'^my_budgets/delete/(?P<budget_id>\d+)/?$', 'delete_my_budget'),
  (r'^organization_budgets$', 'budget_search'),
  (r'^$', 'index'),
  (r'^signator', 'add_signator'),
  (r'^api/approved_budgets/?', 'json_approved_budgets'),
  (r'^api/unapproved_budgets/?', 'json_unapproved_budgets')
)
