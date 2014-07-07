from django.conf.urls.defaults import *

VALID_FACTORS = [
  'student',
]

# this should be refactored to make it restful

urlpatterns = patterns(
  'webapps.organizations.views',
  (r'^$', 'index'),
  (r'^my_organizations/?$','my_organizations'),
  (r'^my_organizations/edit/(?P<org_id>\d*)/?$', 'edit_org'),
  (r'^my_organizations/save/(?P<org_id>\d*)/?$', 'save_org'),
  (r'^my_organizations/delete/(?P<org_id>\d+)/?$', 'delete_org'),
  (r'^organization_list/?$','organization_list'),
  (r'^organization_detail/(?P<org_id>\d+)/?$', 'organization_detail'),
  (r'^organization_list/as_csv/?$','csv_list'),
  (r'^renew_organization/(?P<org_id>\d+)/?$', 'renew_organization'),
  
  (r'^orgs/(?P<org_id>\d+)/edit/?$', 'edit_org'),
  (r'^orgs/(?P<org_id>(?:\d+)|(?:new))/save/?$', 'save_org'),
  (r'^orgs/(?P<org_id>\d+)/delete/?$', 'delete_org'),
  (r'^orgs/(?P<org_id>\d+)/detail/?$', 'organization_detail'),
  (r'^orgs/(?P<org_id>\d+)/renew/?$', 'renew_organization'),
  (r'^orgs/(?P<org_id>\d+)/change-signator/?$', 'change_signator_get'),
  (r'^orgs/(?P<org_id>\d+)/change-signator/(?P<new_signator_username>\w+)/?$', 'change_signator_post'),
  (r'^orgs/signator/(?P<signator_id>\d+)/?$','my_organizations'),
  (r'^orgs/html-list/?$', 'organization_list'),
  (r'^orgs/csv-list/?$', 'csv_list'),
  (r'^orgs/archive$', 'archive_org'),
  (r'^my-organizations/?$','my_organizations'),
  
  (r'^ajax/orgs/all/?$','ajax_show_all'),
  (r'^ajax/orgs/my_orgs/?$','ajax_my_organizations'),
  (r'^ajax/orgs/new/?$','ajax_organization_new'),
  (r'^ajax/orgs/(?P<org_id>\d+)/?$','ajax_organization_details'),
  (r'^ajax/orgs/(?P<org_id>\d+)/save/?$','ajax_organization_save'),
  (r'^ajax/orgs/(?P<org_id>\d+)/delete/?$','ajax_organization_delete'),
  (r'^ajax/orgs/(?P<org_id>\d+)/change-signator/(?P<new_signator_username>\w+)/?$','ajax_organization_change_signator'),
  (r'^clean$', 'clean_orgs')
)
