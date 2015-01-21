from django.conf.urls.defaults import *

"""

-- Jacob Menick
-- March 2014 

Just gettin' started here buildin' the new elections app :)

"""

# idenitifer refers to the election's id
urlpatterns = patterns(
    'webapps.elections.views',
    (r'^vote/(?P<identifier>\d{1,10})/$','vote'),
    (r'^vote/check-username/$','check_username'),
#    (r'^re_vote/$','re_vote'),

    (r'^submit_vote/(?P<identifier>\d{1,10})/$','submit_vote'),
    (r'^re_submit_vote/$','re_submit_vote'),
    (r'^admin/$', 'admin_index'),
    (r'^admin/create/$', 'create_election'),
    (r'^admin/delete/(?P<identifier>\d{1,10})/$','delete_election'),
    (r'^admin/deleted/$', 'deleted'),
    (r'^admin/thanks/$', 'thanks'),
    (r'^$', 'index'),

    #(r'^admin/(?P<identifier>/d{1,10})/candidate_manager/$','candidate_manager'),
    #(r'^create/$','create_election'),
    #(r'^edit/(?P<identifier>/d{1,10})/$','edit_election'),
    #(r'^results/(?P<identifier>/d{1,10})/$','election_results'),
    #(r'^success/$','success'),
    
)
