import demjson

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.db.models import Q

from webapps.generic.models import * 
from webapps.generic.views import *
from webapps.generic.errors import Http400, Http401
from webapps.fundingpoll.models import *
from django.core.exceptions import MultipleObjectsReturned


VALID_FACTORS = [
  'admin'
]

def index(request):
  factor = authenticate(request, VALID_FACTORS)
  
  return render_to_response('users/index.phtml', context_instance=RequestContext(request))

def lookup_user(request):
  factor = authenticate(request, VALID_FACTORS)
  
  if request.method != 'GET':
    raise Http400
  
  get_dict = request.GET
  
  _username = get_dict['username']
  _first_name = get_dict['first_name']
  _last_name = get_dict['last_name']
  _email = get_dict['email']
  
  query = None
  
  if _username != '':
    query = Q(username__regex = _username)
  if _first_name != '':
    if query:
      query = query & Q(first_name__regex = _first_name)
    else:
      query = Q(first_name__regex = _first_name)
  if _last_name != '':
    if query:
      query = query & Q(last_name__regex = _last_name)
    else:
      query = Q(last_name__regex = _last_name)
  if _email != '':
    if query:
      query = query & Q(email__regex = _email)
    else:
      query = Q(email__regex = _email)
  
  if not query:
    raise Http400
  
  def get_user_info(u):
    return {
      'id' : u.id,
      'username' : u.username,
      'first_name' : u.first_name,
      'last_name' : u.last_name,
      'email' : u.email
    }
  
  response_str = demjson.encode(map(get_user_info,list(SinUser.objects.select_related().filter(query))))
  
  return HttpResponse(response_str, mimetype = 'text/javascript')

def edit_user(request, user_id):
  factor = authenticate(request, VALID_FACTORS)
  user = SinUser.objects.select_related().get(id = user_id)
  
  if request.method == 'POST':
    post_dict = request.POST
    
    for f in user.factor_set.all():
      f.users.remove(user)
      f.save()
    
    for fid in post_dict:
      if post_dict[fid] != 'false':
        f = Factor.objects.get(id = fid)
        f.users.add(user)
        f.save()
  
  factor_list = []
  for f in Factor.objects.all():
    has_factor = False
    
    if list(f.users.filter(id = user.id)) != []:
      has_factor = True
    
    factor_list.append({
        'id' : f.id,
        'name' : f.name,
        'has_factor' : has_factor,
        })
  
  template_dict = {
    "user" : user,
    "factors" : factor_list,
  }
  
  return render_to_response("users/edit_user.phtml",template_dict, context_instance=RequestContext(request))

def add_users(request):
  factor = authenticate(request, VALID_FACTORS)

  newuserFile = open("/var/django/webapps/utility/organization/get_username_for_names/StudentOrgs.csv")
  rspns = ""

  for line in newuserFile:
    spl = line.split(' ')
    uid = spl[2].split('@')
    uid = uid[0]
    try:
      user = SinUser.objects.get(username=uid)
    except:
      rspns += spl[0] + " " + spl[1] + "\n"
      continue
    user.attended_signator_training = True
#    user.save()

  return HttpResponse(rspns, mimetype = 'text/plain')

def get_signators(request):
  factor = authenticate(request, VALID_FACTORS)
  signators = SinUser.objects.all().filter(attended_signator_training=True)

  r = ''

  for s in signators:
    email = s.email
    if len(email) == 0:
      email = s.username + "@reed.edu"
    r = r + email + ", "

  return HttpResponse(r, mimetype="text/plain")

def get_unregistered_signators(request):
  factor = authenticate(request, VALID_FACTORS)
  signators = SinUser.objects.all().filter(attended_signator_training=True) 
  notLazy = []
  lazy = []
  reg_orgs = get_fp().fundingpollorganization_set.select_related()
  
  rsp = ''

  for o in reg_orgs:
    unregistered = True
    if o.organization.signator in signators:
      notLazy = notLazy + [o.organization.signator]

  for s in signators:
    if s not in notLazy:
      lazy = lazy + [s]

  for l in lazy:
    email = l.email
    if len(email) == 0:
      email = l.username + "@reed.edu"

    rsp = rsp + email + ", "

  return HttpResponse(rsp, mimetype="text/plain")
