from django.db import models
from django.contrib.auth.models import User
from webapps.generic.models import SinUser
import datetime

####################################
# Echoing JM # we define categories
#   in posts # to make changes more
#            # flexible 
#################################### -BB

class WikiApp(models.Model):
    """ Application to Create a Wiki """
    name = models.CharField(max_length = 50, unique = True)
    description = models.TextField() # Will be used in initializing the wiki
    justification = models.TextField() # Will be used for review, should include 
                                        # what specifically they want out of their wiki
    is_moderated = models.BooleanField(default=True) # Default: moderated
    moderators = models.CharField(max_length=100) # Have them enter names separated by commas
    has_comments = models.BooleanField(default=True) # Default: allow comments

    applicant = models.ForeignKey(SinUser, related_name = "w_applications")
    email = models.EmailField(max_length=100)

    created_on = models.DateTimeField(auto_now_add = True) # These populate automagically
    modified_on = models.DateTimeField(auto_now = True)    

    approved = models.BooleanField(default=False)

    # Instantiate a wiki 
    def make_wiki(self):
        w = Wiki(name=self.name,description=self.description,is_moderated= self.is_moderated, has_comments=self.has_comments)

        w.moderators.add(applicant)

        w.save()

                                       

class Wiki(models.Model):
    """ Model for an organizational wiki """
    name = models.CharField(max_length = 50, unique = True)
    description = models.TextField() # HTML friendly
    created_on = models.DateTimeField(auto_now_add = True)
    modified_on = models.DateTimeField(auto_now = True)
    
    is_moderated = models.BooleanField(default=True) # Default: allow moderation
    moderators = models.ManyToManyField(SinUser, related_name = "w_mod_privs") # Allows multiple moderators
    has_comments = models.BooleanField(default=True) # Default: allow comments

    style = models.CharField(max_length=50, unique = True)

    def __unicode__(self):
        return self.name

class Article(models.Model):
    """ Model for a Wiki Article """
    wiki = models.ForeignKey(Wiki, related_name = "articles")
    title = models.CharField(max_length = 50, unique = True)
    # Have any "intro" simply be a section pointing to the article

    is_featured = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add = True)
    modified_on = models.DateTimeField(auto_now = True) 



class ArticleSection(models.Model):
    """ Model for Article Sections """
    article = models.ForeignKey(Article, related_name = "sections")
    title = models.CharField(max_length = 50, unique = True)
    body = models.TextField() # HTML friendly
    modified_on = models.DateTimeField(auto_now = True)    


class ArticleFlag(models.Model):
    """ Flagging for possible errors, like Wikipedia """
    flag_type = models.CharField(max_length = 20)
    flagged_on = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length = 20)

    flag_description = models.TextField()
    mod_response = models.TextField() 

    section = models.ForeignKey(ArticleSection, related_name="flags")
    article = models.ForeignKey(Article,related_name = "flags")
    # Automatically add the flag to the article


""" Model for an Article Comment derr"""
""" Any fields that point to a comment Model are prefixed with a' w_'"""
"""
class ArticleComment(models.Model):
    
    text = models.CharField(max_length = 1000)
    parent_article = models.ForeignKey(Article, related_name="comments")
    commenter = models.ForeignKey(SinUser, related_name="w_comments")

    created_on = models.DateTimeField(auto_now_add = True)
    was_edited = models.BooleanField(default=False)

    score = models.IntegerField(null=True)
    upvotes = models.IntegerField(null=True)
    downvotes = models.IntegerField(null=True)

def update_comment_scores():
    komments = ArticleComment.objects.all()
    for komment in komments:
        komment.score = upvotes - downvotes 
        komment.save()
  """     
