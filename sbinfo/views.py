import os, sys

import datetime

from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.views.generic.simple import *
from django.views.generic.list_detail import *
from django.views.generic.create_update import *

from webapps.generic.views import *
from webapps.generic.models import *
from webapps.generic.errors import *
from webapps.sbinfo.models import *

VALID_FACTORS = [
  'student'
]

ADMIN_FACTORS = [
  'appointments'
]

def index(request):
  authenticate(request, VALID_FACTORS)
  
  return render_to_response('sbinfo/index.phtml',context_instance=RequestContext(request))

def sbinfo_submit(request):
  authenticate(request, VALID_FACTORS)
  
  if request.method == 'POST':
    if sbinfoentry_id == '':
      entry = SBInfoEntry()
    else:
      entry = SBInfoEntry.objects.get(id = sbinfoentry_id)
    
    post = request.POST
    
    entry.contact = request.user
    entry.title = post['title']
    entry.message = post['message']
    entry.save()

    template_args = {
      'user' : request.user,
      'entry' : entry,
    }
    
    return render_to_response('sbinfo/submit.phtml',template_args,context_instance=RequestContext(request))

  else:
    entry = SBInfoEntry()
    template_args = {
      'user' : request.user,
      'entry' : entry,
    }

    return render_to_response('sbinfo/submit.phtml',template_args,context_instance=RequestContext(request))

def sbinfo_list(request):
  authenticate(request, VALID_FACTORS)
