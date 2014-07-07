import os, sys
import unicodedata

from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist


from webapps.generic.models import *
from webapps.generic.views import *
from webapps.generic.errors import *
from webapps.classifieds.models import Post, Comment, update_daysElapsed, update_scores, update_ranks
import webapps.classifieds.models
from webapps.classifieds.models import Message
from webapps.classifieds.forms import AdForm, CommentForm, MessageForm

"""

-- Jacob Menick
-- January 2014

Okay, so there's alot going on here.  Some of the views are unused. Others could probably be consolidated into one view with a parameter for the type of page (for example, 'display_trade_ads(request)' and 'display_happenin_ads(request)' could probably be consolidated into a generic 'display_ads(request, category') view.  

You could pretty much slice the views into two sections: 

'display/list' views and 'create/edit/delete' views. 

The edit and delete view make use of query strings grabbed from the url in order to determine the 'id' of the Posts and Comments.  If this is foreign, check out the 'Views and URLconfs' Chapter of the Django Book. 

"""

VALID_FACTORS = [
    'student'
]

def index(request):

    authenticate(request, VALID_FACTORS)

    template_args = {
        'user' : request.user
    }

    return render_to_response('classifieds/index.phtml',template_args,context_instance=RequestContext(request))

def display_all_ads(request):

    authenticate(request, VALID_FACTORS)        
    ad_category = "All"
    ads = Post.objects.all().order_by('timestamp')

    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : ad_category
    }
    
    return render_to_response('classifieds/display_ads.phtml', template_args,context_instance=RequestContext(request))

def display_trade_ads(request):

    authenticate(request, VALID_FACTORS)        
    ispm = request.user.is_posts_mod()
    ad_category = "Trade"
    ads = Post.objects.filter(category = ad_category).order_by('-id')
    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : ad_category,
        'ismod': ispm,
    }
    
    return render_to_response('classifieds/display_ads.phtml', template_args,context_instance=RequestContext(request))

def display_missed_connections_ads(request):

    authenticate(request, VALID_FACTORS)        
    
    ad_category = "Missed Connections"
    ads = Post.objects.filter(category = ad_category).order_by('-id')
    ispm = request.user.is_posts_mod()
    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : ad_category,
        'ismod': ispm,
    }
    
    return render_to_response('classifieds/display_mcs.phtml', template_args,context_instance=RequestContext(request))

def display_lostfound_ads(request):

    authenticate(request, VALID_FACTORS)        
    
    ad_category = "Lost & Found"
    ads = Post.objects.filter(category = ad_category).order_by('-id')
    ispm = request.user.is_posts_mod()

    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : ad_category,
        'ismod': ispm,
    }
    
    return render_to_response('classifieds/display_ads.phtml', template_args,context_instance=RequestContext(request))

def display_ramblings_ads(request):

    authenticate(request, VALID_FACTORS)        
    
    ad_category = "Ramblings"
    ads = Post.objects.filter(category = ad_category).order_by('-id')
    ispm = request.user.is_posts_mod()

    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : ad_category,
        'ismod': ispm,
    }
    
    return render_to_response('classifieds/display_ads.phtml', template_args,context_instance=RequestContext(request))

def display_happenin_ads(request):

    authenticate(request, VALID_FACTORS)        
    
    ad_category = "Happenin"
    ads = Post.objects.filter(category = ad_category).order_by('-id')
    ispm = request.user.is_posts_mod()

    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : ad_category,
        'ismod': ispm,
    }
    
    return render_to_response('classifieds/display_ads.phtml', template_args,context_instance=RequestContext(request))

def my_posts(request):

    authenticate(request, VALID_FACTORS)        
    try: 
        ad_creator = request.user
    except:
        raise Http404

    ads = Post.objects.filter(creator = ad_creator).order_by('-id')

    template_args = {
        'user' : request.user,
        'relevant_ads' : ads, 
        'category' : "My Posts",
    }
    
    return render_to_response('classifieds/display_my_ads.phtml', template_args,context_instance=RequestContext(request))

def display_ad(request, identifier):
    
    authenticate(request, VALID_FACTORS)
    
    ispm = request.user.is_posts_mod()

    try:
        ad = Post.objects.get(id=identifier)
    except: 
        raise Http404 # raise an exception eventually!

    if ad.category == "Missed Connections": 
        return HttpResponseRedirect('/webapps/classifieds/mc/'+str(ad.id)+'/')
    else:
    #because we shouldn't be able to see mc authors by typing in the id!!
        template_args = {
            'ad': ad,
            'request': request,
            'ismod': ispm,
            }
    
        return render_to_response('classifieds/display_ad.phtml', template_args,context_instance=RequestContext(request))

def display_ad2(request, identifier):
    authenticate(request, VALID_FACTORS)
    ispm = request.user.is_posts_mod()
    ad = Post.objects.get(id=identifier)
    if ad.category == "Missed Connections": 
        return HttpResponseRedirect('/webapps/classifieds/mc/'+str(ad.id)+'/')
    else:
    #because we shouldn't be able to see mc authors by typing in the id!!

        if request.method == 'POST':
            form = CommentForm(request.POST)
            parent_ad = Post.objects.get(id=identifier)
            creator = request.META['REMOTE_USER']
            creator = SinUser.objects.get(username=creator)
            if form.is_valid():
                cd = form.cleaned_data
                comment = Comment(text=cd['text'], parent_post = parent_ad, commenter=creator, timestamp = datetime.now().date(), timestamp_time = datetime.now().time(), score=100, upvotes=0, downvotes=0)
                comment.save()
                return HttpResponseRedirect('/webapps/classifieds/post/'+str(parent_ad.id)+'/')
            else:
                form = CommentForm()
                return HttpResponseRedirect('/webapps/classifieds/post/'+str(parent_ad.id)+'/')

        else: 
            form = CommentForm()
            ad = Post.objects.get(id=identifier)
            comments = ad.comments_on_post.all().order_by('id')

            template_args = {
                'ad': ad,
                'request': request,
                'form': form,
                'comments': comments,
                'ismod': ispm,
                }
    
            return render_to_response('classifieds/display_ad2.phtml', template_args,context_instance=RequestContext(request))

def display_mc(request, identifier):
    
    authenticate(request, VALID_FACTORS)

    ad = Post.objects.get(id=identifier)
    sender = request.user
    recipient = ad.creator
    msg_set = ad.message_set
    already_sent_one = msg_set.filter(sender=sender).exists()
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = Message(sender=sender, recipient=recipient, parent_post=ad, body=cd['body'])
            message.save()
            return HttpResponseRedirect('/webapps/classifieds/mc/'+str(identifier)+'/')
        else: 
            return HttpResponseRedirect('/webapps/classifieds/mc/'+str(identifier)+'/')
        
    else: 
        form = MessageForm()
        ad_category = "Missed Connections"
        ispm = request.user.is_posts_mod()
        relevant_messages = ad.message_set.filter(accepted=False,rejected=False)
        not_creator = request.user != ad.creator
        has_requested = ad.message_set.filter(sender=request.user).exists()
        is_accepted = False
        if has_requested:
            user_requests = ad.message_set.filter(sender=request.user)
            for thing in user_requests.all():
                if thing.accepted == True:
                    is_accepted = True

        template_args = {
            'ad': ad,
            'category': ad_category,
            'ismod': ispm,
            'form': form,
            'not_creator': not_creator,
            'relevant_messages': relevant_messages,
            'is_accepted': is_accepted,
            'already_sent': already_sent_one,
        }
    
        return render_to_response('classifieds/display_mc2.phtml', template_args,context_instance=RequestContext(request))

def accept_message(request, identifier):
    message = Message.objects.get(id=identifier)
    ad_id = message.parent_post.id
    message.accepted = True
    message.rejected = False
    message.save()
    return HttpResponseRedirect('/webapps/classifieds/mc/'+str(ad_id)+'/')

def reject_message(request, identifier):
    message = Message.objects.get(id=identifier)
    ad_id = message.parent_post.id
    message.accepted = False
    messag.rejected = True
    message.save()
    return HttpResponseRedirect('/webapps/classifieds/mc/'+str(ad_id)+'/')

def ad_mockup(request):

    authenticate(request, VALID_FACTORS)

    template_args = {
        'user' : request.user
    }

    return render_to_response('classifieds/ad_mockup.phtml',template_args,context_instance=RequestContext(request)) 

def create_ad(request):
    
    authenticate(request, VALID_FACTORS)

    if request.method == 'POST':
        form = AdForm(request.POST)
        creator = request.META['REMOTE_USER']
        ad_creator = request.user
        if form.is_valid():
            cd = form.cleaned_data
            num_ads = len(list(Post.objects.all()))
            update_ranks()
            ad = Post(title=cd['title'],text = cd['text'],category = cd['category'], creator_email = cd['email'], creator_phone = cd['phone'], sub_category = 'foo', creator=ad_creator, timestamp = datetime.today().date(), daysElapsed = 0, upvotes = 0, downvotes = 0, score = 100, rank = num_ads+1)
            ad.save()
            update_daysElapsed()
            update_scores()
            update_ranks()
            return HttpResponseRedirect('/webapps/classifieds/thanks/')
        else:
            return render_to_response('classifieds/new_ad_form.phtml', {'form': form,'category':'New Post'},context_instance=RequestContext(request))
    else:
        form = AdForm()
        
    return render_to_response('classifieds/new_ad_form.phtml', {'form': form,'category':'New Post'},context_instance=RequestContext(request))


def edit_ad(request, identifier):

    authenticate(request, VALID_FACTORS)

    ad = Post.objects.get(id=identifier)
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            ad.category = cd['category']
            ad.title = cd['title']
            ad.text = cd['text']
            ad.timestamp = datetime.today().date()
            ad.daysElapsed = 0;
            ad.creator_email = cd['email']
            ad.creator_phone = cd['phone']
            ad.save()
            update_daysElapsed()
            update_scores()
            return HttpResponseRedirect('/webapps/classifieds/thanks/')
        else:
            return render_to_response('classifieds/edit_ad_form.phtml', {'form': form},context_instance=RequestContext(request))
    else:
        form = AdForm(
            initial={'title': ad.title, 'text': ad.text, 'category': ad.category, 'sub_category': ad.sub_category, 'email': ad.creator_email, 'phone': ad.creator_phone}
        )
    return render_to_response('classifieds/edit_ad_form.phtml', {'form': form},context_instance=RequestContext(request))

def delete_ad(request, identifier):

    authenticate(request, VALID_FACTORS)
    ispm = request.user.is_posts_mod()

    ad = Post.objects.get(id=identifier)
    if (request.user == ad.creator or ispm):
        ad.delete()
        update_daysElapsed()
        update_scores()
        return HttpResponseRedirect('/webapps/classifieds/deleted/')
    else: 
        return HttpResponseRedirect('/webapps/classifieds/')

def delete_comment(request, identifier):

    authenticate(request, VALID_FACTORS)

    comment = Comment.objects.get(id=identifier)
    if (request.user == comment.commenter or ispm):
        comment.delete()
        return HttpResponseRedirect('/webapps/classifieds/cdeleted/')
    else: 
        return HttpResponseRedirect('/webapps/classifieds/')

def thanks(request):

    authenticate(request, VALID_FACTORS)

    return render_to_response('classifieds/new_post_thanks.phtml',context_instance=RequestContext(request))

def deleted(request):

    authenticate(request, VALID_FACTORS)

    return render_to_response('classifieds/deleted.phtml',context_instance=RequestContext(request))

def cdeleted(request):

    authenticate(request, VALID_FACTORS)

    return render_to_response('classifieds/cdeleted.phtml',context_instance=RequestContext(request))

def upvote(request, identifier):
    ad = Post.objects.get(id=identifier)
    ad.upvotes +=1
    ad.save()
    return HttpResponseRedirect('/webapps/classifieds/')

def downvote(request, identifier):
    ad = Post.objects.get(id=identifier)
    ad.downvotes +=1
    ad.save()
    return HttpResponseRedirect('/webapps/classifieds/')
