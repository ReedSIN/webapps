from django.conf.urls.defaults import *

"""
-- Brett Beutell (BB)
-- Jan/Feb 14

TO CHANGE
() Switch to named URLS
() 
"""


urlpatterns = patterns(
    'webapps.wiki.views',
    (r'^$', 'index'),
    (r'^test', 'test'),
    (r'^wiki-apps/create', 'create_wiki_app'),
    (r'^wiki-apps/edit/(?P<identifier>\d{1,10})/$', 'edit_wiki_app'), # Low priority
    (r'^wiki-apps/all', 'display_wiki_apps'),
    (r'^wiki-apps/review/(?P<identifier>\d{1,10})/$', 'review_wiki_app'),
    (r'^(?P<identifier>\d{1,10})/$', 'wiki_home'),
    (r'^edit/(?P<identifier>\d{1,10})/$','edit_wiki'),
    (r'^article/(?P<identifier>\d{1,10})/$', 'wiki_article'),
    (r'^article/edit/(?P<identifier>\d{1,10})/$', 'edit_article'),
    (r'^moderator-dash','moderator_dash'), # Low priority
    (r'^thanks', 'thanks'), # Include template tag of what was just created
    (r'^deleted', 'deleted'), # Include template tage of what was deleted
)
