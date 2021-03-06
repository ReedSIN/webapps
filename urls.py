from django.conf.urls.defaults import *
from django.contrib import admin ## MK
admin.autodiscover() ## MK

handler500 = 'webapps.generic.errors.server_error'

from webapps.generic.views import logout, ajax_user, four01, five00, redirect_home



urlpatterns = patterns(
  '',
  (r'^webapps/$', include('webapps.home.urls')),
  (r'^webapps/home/?', include('webapps.home.urls')),
  (r'^webapps/wiki/?', include('webapps.wiki.urls')),
  (r'^webapps/votw/?', include('webapps.VotW.urls')),
  (r'^webapps/classifieds/?', include('webapps.classifieds.urls')),  # JM (1/4/14)
  (r'^webapps/elections/?', include('webapps.elections.urls')), 
  (r'^webapps/sbinfo/?', include('webapps.sbinfo.urls')),
  (r'^webapps/finance/?', include('webapps.finance.urls')),
  (r'^webapps/appointments/?', include('webapps.appointments.urls')),
  (r'^webapps/fundingpoll/?', include('webapps.fundingpoll.urls')),
  (r'^webapps/users/?', include('webapps.users.urls')),
  (r'^webapps/organization-manager/?', include('webapps.organizations.urls')),
  (r'^webapps/organizations/?', include('webapps.organizations.urls')),
  (r'^webapps/forms/?', include('webapps.forms.urls')),
  (r'^webapps/paideia/?', include('webapps.paideia.urls')),
  (r'^webapps/ajax/user/?', ajax_user),
  (r'^webapps/logout/?', logout),
  (r'^webapps/401/?', four01),
  (r'^webapps/500/?', five00),
  (r'^webapps/admin/', include(admin.site.urls)), ## MK 
)
