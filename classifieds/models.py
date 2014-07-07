from django.db import models
# from django.forms import ModelForm
from django.contrib.auth.models import User
from webapps.generic.models import SinUser
import datetime

"""OVERVIEW
JM
January 2014

There are two models in the classifieds app. The first is a "Post", and the second is a "Comment". 
A "Comment" is exactly what it sounds like, and the "Post" class is for the various categories of classified ads on the site: 
'Missed Connections', 'Trade', 'Lost & Found', 'Things Happenin', and 'Ramblings'. 

The three 'update' methods for "Post" update the respective attributes of "Post" objects because I couldn't figure out how to make fields dynamic in mysql.  

"""

class Post(models.Model):
    """ model for a 'post' or classifieds submission of some sort."""
    
    title = models.CharField(max_length = 50, unique=True)
    text = models.CharField(max_length = 2000)
    creator = models.ForeignKey(SinUser, related_name = "post_set")
    timestamp = models.DateField() # prob handle this in forms
    timestamp_time = models.TimeField(null=True)
    daysElapsed = models.IntegerField()
    upvotes = models.IntegerField()
    downvotes = models.IntegerField()
    score = models.IntegerField()
    rank = models.IntegerField(unique=False)
    category = models.CharField(max_length = 40) #maybe there is some sort of factor-like field in MySQL?
    sub_category = models.CharField(max_length = 45) #ditto above
    creator_email = models.EmailField(blank=True)
    creator_phone = models.CharField(max_length=10, blank=True)
#    replies_yn = models.BooleanField()
#    requesters = models.ManyToManyField(SinUser, related_name ="request_set")
#    rejected = models.ManyToManyField(SinUser, related_name ="rejected_set")
#    accepted = models.ManyToManyField(SinUser, related_name="accepted_set")

    def __unicode__(self):
        return self.title

#    def is_correct(self,guess):
#        if guess == self.security_answer:
#            return True
#        else:
#            return False

def update_daysElapsed():
    today = datetime.date.today()
    posts = Post.objects.all()
    for post in posts:
        post.daysElapsed = (today - post.timestamp).days
        post.save()

def update_scores():
    posts = Post.objects.all()
    for post in posts: 
        post.score = 100 + post.upvotes - post.downvotes - post.daysElapsed
        post.save()    #Should this have parentheses? - BB #Yes! Good catch. - JM


def update_ranks():
    posts = list(Post.objects.filter(category="Missed Connections").order_by('score','-id')) 
    for i in range(len(posts)-1):
        posts[i].rank = i+1
        posts[i].save()

    #Using update on a queryset might be more efficient per Django Docs - BB
    
    

class Comment(models.Model):
    """ model for a comment on a post. """

    text = models.CharField(max_length = 1000)
    parent_post = models.ForeignKey(Post, related_name = "comments_on_post")
    commenter = models.ForeignKey(SinUser, related_name = "user_comment_set")
    timestamp = models.DateField()
    timestamp_time = models.TimeField(null=True)
    score = models.IntegerField(null=True)
    upvotes = models.IntegerField(null=True)
    downvotes = models.IntegerField(null=True)
    """ Maybe won't include up/downvotes in the comment system
    because Reedies can be harsh animals
    and we can't fix hurt feelers here at SIN. """

class Message(models.Model):
    """ Called 'message' becuase 'request' is taken by....'the internet.'"""

    sender = models.ForeignKey(SinUser, related_name="cl_sent_messages")
    recipient = models.ForeignKey(SinUser, related_name="cl_rec_messages")
    parent_post = models.ForeignKey(Post, related_name="message_set")
    body = models.CharField(max_length = 300, null=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
   

"""
*** has_requested method

post = Post.objects.get(id= identifier)
person = request.user

has_requested = post.meesage_set.filter(sender= person).exists()

""" 
    
