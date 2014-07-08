import os, sys

import datetime

from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext

# from django.views.generic.simple import *
from django.views.generic.base import *
from django.views.generic.list import *
from django.views.generic.detail import *
# from django.views.generic.create_update import *
from django.views.generic.edit import *

from webapps.generic.views import *
from webapps.generic.models import *
from webapps.generic.errors import *
from webapps.appointments.models import *

VALID_FACTORS = [
  'student'
]

ADMIN_FACTORS = [
  'appointments'
]

def index(request):
  authenticate(request, VALID_FACTORS)
  
  return render_to_response('appointments/index.html',context_instance=RequestContext(request))

def open_position_list(request):
  authenticate(request, VALID_FACTORS)
  
  positions = Position.objects.filter(expires_on__gt = datetime.datetime.now()).order_by('expires_on')
  
  template_args = {
    'object_list' : positions
  }
  
  return render_to_response('appointments/position_list.html',template_args,context_instance=RequestContext(request))

def open_position_detail(request, position_id):
  authenticate(request, VALID_FACTORS)
  
  position = Position.objects.get(id = position_id)
  
  template_args = {
    'object' : position
  }
  
  return render_to_response('appointments/position_detail.html', template_args,context_instance=RequestContext(request))

def admin_index(request):
  authenticate(request, ADMIN_FACTORS)
  
  template_args = {
    'positions' : Position.objects.order_by('-expires_on')
  }
  
  return render_to_response('appointments/admin_index.html',template_args,context_instance=RequestContext(request))

def create_position(request):
  authenticate(request, ADMIN_FACTORS)

  template_args = {
    'user' : request.user
  }
  
  return render_to_response('appointments/create_position.html',template_args,context_instance=RequestContext(request))

def submit_new_position(request,position_id):
  authenticate(request, ADMIN_FACTORS)

  if request.method == 'POST':
    querystr = request.POST
    
    if position_id == '':
      p = Position()
      s = True
    else:
      p = Position.objects.get(id = position_id)
    
    p.name = querystr['name']
    p.contact = request.user
    p.description = querystr['description']
    date_list = querystr['expires_on'].split('-')
    
    ex_month = int(date_list[0])
    ex_day = int(date_list[1])
    ex_year = int(date_list[2])
    
    p.expires_on = datetime.datetime(month = ex_month,
                                     day = ex_day,
                                     year = ex_year)
    p.save()
  else:
    p = Position.objects.get(id = position_id)

  template_args = {
    'user' : request.user,
    'position' : p,
    'success' : s
   }
  return render_to_response('appointments/edit_position.html',template_args,context_instance=RequestContext(request))

def edit_position(request,position_id):
  authenticate(request, ADMIN_FACTORS)
  
  if request.method == 'POST':
    querystr = request.POST
    
    if position_id == '':
      p = Position()
    else:
      p = Position.objects.get(id = position_id)
    
    p.name = querystr['name']
    p.contact = request.user
    p.description = querystr['description']
    date_list = querystr['expires_on'].split('-')
    
    ex_month = int(date_list[0])
    ex_day = int(date_list[1])
    ex_year = int(date_list[2])
    
    p.expires_on = datetime.datetime(month = ex_month,
                                     day = ex_day,
                                     year = ex_year)
    p.save()
  else:
    p = Position.objects.get(id = position_id)
  
  template_args = {
    'user' : request.user,
    'position' : p
  }
  
  return render_to_response('appointments/edit_position.html',template_args,context_instance=RequestContext(request))

def delete_position(request, position_id):
  authenticate(request, ADMIN_FACTORS)
  
  p = Position.objects.get(id = position_id)
  apps = p.application_set.all()
  
  for a in apps:
    a.delete()
  p.delete()
  
  return HttpResponsePermanentRedirect('/webapps/appointments/admin/')

def position_application_list(request, position_id):
  authenticate(request, ADMIN_FACTORS)
  
  position = Position.objects.get(id = position_id)
  
  template_args = {
    'position' : position,
    'applications' : position.application_set.all()
  }
  
  return render_to_response('appointments/position_application_list.html',template_args,context_instance=RequestContext(request))

def position_application_detail(request, position_id, application_id):
  authenticate(request, ADMIN_FACTORS)
  
  app = Application.objects.get(id = application_id, position__id = position_id)
  
  template_args = {
    'app' : app
  }
  
  return render_to_response('appointments/position_application_detail.html',template_args,context_instance=RequestContext(request))

def create_application(request, position_id):
  authenticate(request, VALID_FACTORS)
  
  p = Position.objects.get(id = position_id)

  template_args = {
    'user' : request.user,
    'position' : p
  }
  
  return render_to_response('appointments/edit_application.html',template_args,context_instance=RequestContext(request))

def edit_application(request, application_id):
  authenticate(request, VALID_FACTORS)
  
  if request.method == 'POST':
    if application_id == '':
      a = Application()
    else:
      a = Application.objects.get(id = application_id)
    
    post = request.POST
    
    a.applicant = request.user
    a.position = Position.objects.get(id = post['position_id'])
    a.major = post['major']
    a.preferred_pron = post['preferred_pron']
    year = YEAR_DICT[post['year']]
    a.year = year
    a.address = post['address']
    a.phone = post['phone']
    a.email = post['email']
    a.schedule_conflicts = post['schedule_conflicts']
    a.other_reed_positions = post['other_reed_positions']
    a.other_employment = post['other_employment']
    a.experience = post['experience']
    a.motivation = post['motivation']
    a.special_skills = post['special_skills']
    a.appeal = post['appeal']
    a.save()

    template_args = {
      'user' : request.user,
      'app' : a,
      'year' : a.year,
    }
    
    return render_to_response('appointments/confirm_application.html',template_args,context_instance=RequestContext(request))
  
  elif application_id != '':
    a = Application.objects.get(id = application_id)
    template_args = {
      'user' : request.user,
      'app' : a,
      'year' : a.year,
    }
    
    return render_to_response('appointments/edit_application.html',template_args,context_instance=RequestContext(request))

  else:
    applications = request.user.application_set.all()
    
    template_args = {
      'my_apps' : applications
    }
    
    return render_to_response('appointments/my_application_list.html',template_args,context_instance=RequestContext(request))

def my_application_list(request):
  authenticate(request, VALID_FACTORS)
  
  applications = request.user.application_set.all()
  
  template_args = {
    'my_apps' : applications
  }
  
  return render_to_response('appointments/my_application_list.html',template_args,context_instance=RequestContext(request))

def delete_application(request, application_id):
  authenticate(request, VALID_FACTORS)
  
  application = request.user.application_set.filter(id = application_id)
  
  if len(application) == 0:
    return HttpResponse403()
  application = application[0]
  
  application.delete()
  
  return HttpResponsePermanentRedirect('/webapps/appointments/my_applications/')
