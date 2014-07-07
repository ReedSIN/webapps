from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponse

from webapps.generic.views import *
from webapps.generic.models import Organization
from webapps.generic.models import SinUser

import demjson

VALID_FACTORS = [
  'student'
]

VALID_POST_FIELDS = [
  'name',
  'location',
  'phone_number',
  'email',
  'website',
  'description',
  'meeting_info',
  'annual_events',
  'associated_off_campus_organizations',
  'referral_info',
]

VALID_FIELDS = VALID_POST_FIELDS
VALID_FIELDS.insert(1,'signator')

SAO = ['holmberk', 'websterka', 'duranr', 'mkincaid']

def isSAO(request):
  username = request.META['REMOTE_USER']
  if username in SAO:
    return True
  else:
    return False

def organization_list(request):
  authenticate(request,VALID_FACTORS)

  if "archived" in request.GET and request.GET["archived"] == "true":
  	archived = True
  else:
    archived = False
  

  if isSAO(request):
    if archived:
      orgs = Organization.objects.all().order_by('name').filter(archived = 1)
    else:
	  orgs = Organization.objects.all().order_by('name').filter(archived = 0)
  else:
    orgs = Organization.objects.all().order_by('name')
  
  template_args = {
    'orgs' : orgs,
	'sao' : isSAO(request),
	'archived' : archived
  }
  
  return render_to_response('organizations/organization_list.phtml', template_args, context_instance=RequestContext(request))

def organization_detail(request, org_id):
  authenticate(request,VALID_FACTORS)
  
  template_args = {
    'org' : Organization.objects.get(id = org_id)
  }
  
  return render_to_response('organizations/organization_detail.phtml', template_args, context_instance=RequestContext(request))
  
def escape(s):
  if type(s) != str and type(s) != unicode:
    return '"' + unicode(s).replace('"','') + '"'
  return '"' + s.replace('"','') + '"'

def decamelcase(s):
  r = s[0].capitalize()
  i = 1
  while i < len(s):
    if s[i] == '_':
      r = r + ' '
      r = r + s[i+1].capitalize()
      i = i + 1
    else:
      r = r + s[i]
    i = i + 1
  return r

def csv_list(request):
  authenticate(request,VALID_FACTORS) 
  resultant = ",".join(map(decamelcase,VALID_FIELDS)) + ",public_post_ok\n"

  if isSAO(request):
    orgs = Organization.objects.select_related().order_by('name').filter(archived = 0)
  else:
    orgs = Organization.objects.select_related().order_by('name')

  for o in orgs:
    for f in VALID_FIELDS:
      resultant = resultant + "%s," % (escape(o.__getattribute__(f)))
    resultant = resultant + "%s\n" % (str(str(o.public_post_ok) == '1'))
  resultant = HttpResponse(resultant,mimetype = "text/csv")
  resultant['Content-Disposition'] = 'attachment; filename=organization_list.csv'
  return resultant

def index(request):
  authenticate(request, VALID_FACTORS)
    
  return render_to_response('organizations/index.phtml', context_instance=RequestContext(request))

def my_organizations(request):
  authenticate(request, VALID_FACTORS)
  username = request.META['REMOTE_USER']
  user = SinUser.objects.get(username__exact = username)
  
  organizations = request.user.signator_set.all()

  from webapps.fundingpoll.models import *

  create_alert= False

  # needs error handling
  fp = get_fp()
  if fp.get_status() == 'during_registration':
    during_reg = True
  else:
    during_reg = False
    create_alert = False
    reg_alert = True
    

  # If registration is open, see if the user has unregistered orgs
  # (Or any orgs at all!)
  if (during_reg):
    num_orgs = len(organizations)
    reg_orgs = 0
    fpos = fp.fundingpollorganization_set
    for org in organizations:
      if fpos.filter(organization=org).exists():
        reg_orgs += 1

    create_alert = True if len(organizations) == 0 else False     
    reg_alert = False if num_orgs == reg_orgs else True       

# end if
  template_args = {
    'organizations' : organizations,
    'signator' : user.attended_signator_training,
    'reg_alert': reg_alert,
    'create_alert': create_alert,
  }
  
  return render_to_response('organizations/my_organizations.phtml',template_args, context_instance=RequestContext(request))

def edit_org(request, org_id):
  authenticate(request, VALID_FACTORS)
  username = request.META['REMOTE_USER']
  user = SinUser.objects.get(username__exact = username)

  if org_id != '':
    o = request.user.signator_set.get(id = org_id)
  else:
    if user.attended_signator_training == False:
	  raise Http401
    o = Organization()
    o.name = ""
    o.signator = request.user
    o.location = ""
    o.phone_number = ""
    o.email = request.user.email
    o.website = ""
    o.description = ""
    o.public_post_ok = True
  
  template_args = {
    'user' : request.user,
    'org' : o
  }
  
  return render_to_response('organizations/edit_org.phtml', template_args, context_instance=RequestContext(request))

def delete_org(request, org_id):
  authenticate(request, VALID_FACTORS)
  
  if request.method != "POST":
    raise Http401
  
  organization = request.user.signator_set.get(id = org_id)
  organization.delete()
  
  return HttpResponsePermanentRedirect('/webapps/organizations/my_organizations/')

def save_org(request, org_id):
  authenticate(request, VALID_FACTORS)
  
  if request.method != "POST":
    raise Http401
  
  post_dict = request.POST
  
  name = post_dict['name']
  
  def org_with_name_exists_redirect(n):
    try:
      Organization.objects.get(name = n)
      template_args = {
        'title' : 'Error!',
        'message' : "An organization with the name `%s` already exists. Please choose another name." % n,
        'redirect' : '/webapps/organization-manager/my_organizations/'
        }
      return render_to_response('generic/alert-redirect.phtml',template_args, context_instance=RequestContext(request))
    except Organization.DoesNotExist:
      return None
  
  if (org_id != ''):
    try:
      organization = request.user.signator_set.get(id = org_id)
    except Organization.DoesNotExist:
      test = org_with_name_exists_redirect(name)
      if test != None:
        return test
      organization = Organization()
  else:
    test = org_with_name_exists_redirect(name)
    if test != None:
      return test
    organization = Organization()
  
  organization.signator = request.user
  
  for n in post_dict:
    if n in VALID_POST_FIELDS:
      organization.__setattr__(n,post_dict[n])
  organization.public_post_ok = ('on' == post_dict.get('public_post_ok','off'))
  
  organization.save()
  
  return HttpResponsePermanentRedirect('/webapps/organizations/my_organizations/')

def renew_organization(request, org_id):
  authenticate(request, VALID_FACTORS)
  
  o = Organization.objects.get(id = org_id, signator = request.user)
  
  o.enabled = True
  o.save()
  
  template_args = {
    'title' : 'Success!',
    'message' : 'You have successfully renewed organization ``%s``.' % o.name,
    'redirect' : '/webapps/organization-manager/my_organizations/'
  }
  
  return render_to_response('generic/alert-redirect.phtml',template_args, context_instance=RequestContext(request))

def clean_orgs(request):
  authenticate(request, ['admin'])

  r = ""

  orgs = Organization.objects.all().order_by('modified_on')[0:154]
  delorgs = []

  for o in orgs:

    signator = SinUser.objects.get(id=o.signator_id)
    if signator.attended_signator_training == True:
      continue

    delorgs = delorgs + [o]

  r = r + str(delorgs)

#  for o in delorgs:
#    o.delete()

#  for o in orgs:
#    signator = User.objects.get(id=o.signator_id)
#    if signator.attended_signator_training == True:
#      r = r + o.name + "\n"

  return HttpResponse(r, mimetype="text/plain")

def archive_org(request):
  if not isSAO(request):
    return HttpResponse("-1", mimetype = "text/plain")

  oid = request.GET['oid']
  status = request.GET['status']
  if status == "true":
  	status = True;
  else:
    status = False;

  o = Organization.objects.get(id = oid)
  o.archived = status
  o.save()

  return HttpResponse(oid, mimetype = "text/plain")

def change_signator_get(request, org_id):
  authenticate(request, VALID_FACTORS)
  
  o = Organization.objects.get(id = org_id, signator = request.user)
  
  template_args = {
    'o' : o
  }
  
  return render_to_response('organizations/change_signator.phtml',template_args, context_instance=RequestContext(request))

def change_signator_post(request, org_id, new_signator_username):
  authenticate(request, VALID_FACTORS)
  
  u2 = SinUser.objects.get(username = new_signator_username)
  
  o = Organization.objects.get(id = org_id, signator = request.user)
  o.signator = u2
  o.email = u2.email
  o.save()
  
  template_args = {
    'title' : 'Success!',
    'message' : 'The Signator of organization ``%s`` was successfully changed from ``%s`` to ``%s``' % (o.name,request.user.get_full_name(),u2.get_full_name()),
    'redirect' : '/webapps/organization-manager/my_organizations/'
  }
  
  return render_to_response('generic/alert-redirect.phtml',template_args, context_instance=RequestContext(request))

def ajax_show_all(request):
  authenticate(request, VALID_FACTORS)
  
  if request.method != 'GET':
    raise Http401()
  
  query = request.GET
  
  s = query.get('start')
  e = query.get('end')
  
  if s == None:
    s = 0
  else:
    s = int(s)
  
  if e == None:
    # Could just get largest id and use that instead
    e = Organization.objects.count()
  else:
    e = int(e)
  
  def serialize(o):
    return {
      'id' : o.id,
      'name' : o.name,
      'signator' : str(o.signator),
      'email' : o.email
      }
  
  orgs = [serialize(o) for o in Organization.objects.all()[s:e]]
  
  return HttpResponse(demjson.encode(orgs),mimetype = 'text/javascript')

def ajax_organization_details(request, org_id):
  authenticate(request, VALID_FACTORS)
  
  o = Organization.objects.get(id = org_id)
  resultant = demjson.encode({
        'id' : o.id,
        'name' : o.name,
        'signator' : str(o.signator),
        'signator_sin_id' : o.signator.id,
        'location' : o.location,
        'email' : o.email,
        'phone_number' : o.phone_number,
        'website' : o.website,
        'description' : o.description,
        'meeting_info' : o.meeting_info,
        'annual_events' : o.annual_events,
        'partner_orgs' : o.associated_off_campus_organizations,
        })
  
  return HttpResponse(resultant, mimetype = 'text/javascript')

def ajax_my_organizations(request):
  authenticate(request, VALID_FACTORS)
  
  orgs = request.user.signator_set.all()
  
  resultant = []
  
  for o in orgs:
    resultant.append({
        'name' : o.name,
        'id' : o.id,
        'signator' : str(request.user),
        'email' : o.email,
        'location' : o.location,
        'phone_number' : o.phone_number,
        'website' : o.website,
        'description' : o.description
        })
  
  return HttpResponse(demjson.encode(resultant),mimetype = "text/javascript")
