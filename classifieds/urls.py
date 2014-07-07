from django.conf.urls.defaults import *
# from django.webapps.classifieds.views import index, display_ads

"""

-- Jacob Menick
-- January 2014

Only thing to note here is that we may want to use named URLS in the future so that if we want to change a URL name (for instance, the url for missed connections is 'we_almost_boned'), we don't have to run around to all the hyperlinks and change their hrefs.  


"""

urlpatterns = patterns(
    'webapps.classifieds.views', #thanks to this line of code, we don't have to import views
    (r'^$', 'index'),
    (r'^all', 'display_all_ads'),
    (r'^trade', 'display_trade_ads'),
    (r'^we_almost_boned', 'display_missed_connections_ads'),
    (r'^lost_found', 'display_lostfound_ads'),
    (r'^ramblings', 'display_ramblings_ads'),
    (r'^happenin', 'display_happenin_ads'),
    (r'^post/(?P<identifier>\d{1,10})/$', 'display_ad2'),
    (r'^mc/(?P<identifier>\d{1,10})/$', 'display_mc'),
    (r'^accept/(?P<identifier>\d{1,10})/$', 'accept_message'),
    (r'^reject/(?P<identifier>\d{1,10})/$', 'reject_message'),
    (r'^new', 'create_ad'),
    (r'^my_posts', 'my_posts'),
    (r'^edit/(?P<identifier>\d{1,10})/$', 'edit_ad'),
    (r'^delete/(?P<identifier>\d{1,10})/$', 'delete_ad'),
    (r'^cdelete/(?P<identifier>\d{1,10})/$', 'delete_comment'),
    (r'^thanks', 'thanks'),
    (r'^deleted', 'deleted'),
    (r'^cdeleted', 'cdeleted'),
   #(r'^dat_post/(?P<identifier>\d{1,10})/$', 'display_ad2'), 
# above url testing implementation of comments. 
)
