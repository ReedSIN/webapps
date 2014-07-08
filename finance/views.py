import os, sys

import re, demjson

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.core.paginator import Paginator
from django.core import serializers
from django.core.exceptions import MultipleObjectsReturned
from django.utils.datastructures import MultiValueDictKeyError
from django.template import RequestContext

from webapps.generic.views import *
from webapps.generic.models import Organization
from webapps.generic.errors import Http400, Http401, Http403
from webapps.finance.models import Budget, BudgetItem

import demjson

# Order is important. Authenticate returns whatever matches first
VALID_FACTORS = [
  'finance',
  'student',
  'senator',
]

ADMIN_FACTORS = [
  'finance',
  'senator',
]

def is_admin_factor(factor):
  return factor in ADMIN_FACTORS

def index(request):
  factor = authenticate(request, VALID_FACTORS)
  
  return render_to_response('finance/index.html',context_instance=RequestContext(request))

def view_all_budgets(request):
  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)
  
  template_args = {
    'admin' : admin,
    'budgets' : Budget.objects.select_related().order_by('-created_on').filter(approved = 0)
  }
  
  return render_to_response('finance/budget-list.html',template_args,context_instance=RequestContext(request))

def json_approved_budgets(request):
  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)

  if request.method != 'GET':
    raise Http400()
  
  num_per_page = int(request.GET.get('num',20))
  budgets = Budget.objects.select_related().order_by('-created_on').filter(approved = 1)
  paginator = Paginator(budgets, num_per_page)
  page_num = int(request.GET.get('page',1))
  if page_num == -1:
    page = paginator.page(paginator.num_pages)
  else:
    page = paginator.page(page_num)
  
  object_list = page.object_list
  resultant = []
  for b in object_list:
    resultant.append({
        'id' : b.id,
        'signator' : unicode(b.organization.signator),
        'organization' : unicode(b.organization.name),
        'requested' : unicode("$%.2f" % b.requested),
        'allocated' : unicode("$%.2f" % b.allocated),
        'created' : unicode(b.created_on.strftime("%d-%m-%Y")),
        'modified' : unicode(b.modified_on.strftime("%d-%m-%Y"))
        })
  
  return HttpResponse(demjson.encode(resultant), mimetype="text/javascript")

def json_unapproved_budgets(request):
  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)

  if request.method != 'GET':
    raise Http400()
  
  num_per_page = int(request.GET.get('num',20))
  budgets = Budget.objects.select_related().order_by('-created_on').filter(approved = 0)
  paginator = Paginator(budgets, num_per_page)
  page_num = int(request.GET.get('page',1))
  if page_num == -1:
    page = paginator.page(paginator.num_pages)
  else:
    page = paginator.page(page_num)
  
  return HttpResponse(serializers.serialize('json',page.object_list), mimetype="text/javascript")


def view_approved_budgets(request):
  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)
  
  if request.method != 'GET':
    raise Http400()
  
  #num_per_page = int(request.GET.get('num',20))
  budgets = Budget.objects.select_related().order_by('-created_on').filter(approved = 1)
  #paginator = Paginator(budgets, num_per_page)
  #page_num = int(request.GET.get('page',1))
  #if page_num == -1:
  #  page = paginator.page(paginator.num_pages)
  #else:
  #  page = paginator.page(page_num)
  
  template_args = {
    'admin' : admin,
    'budgets' : budgets,
    #'count' : num_per_page,
  }
  
  return render_to_response('finance/approved-budget-list.html',template_args,context_instance=RequestContext(request))

def view_one_budget(request, budget_id):
  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)
  
  budget = Budget.objects.select_related().get(id = budget_id)
  items = budget.budgetitem_set.all()
  
  template_args = {
    'admin': admin,
    'budget' : budget,
    'items' : items
  }
  
  return render_to_response('finance/budget-detail.html', template_args,context_instance=RequestContext(request))

def create_budget(request):
  factor = authenticate(request, VALID_FACTORS)
  
  if not request.user.attended_signator_training:
    template_args = {
      'title' : 'Error!',
      'message' : 'Error! You can not create a budget since you did not attend signators training. If you would still like to try and submit a budget please contact the current student body treasurers to make special arrangements.',
      'redirect' : '/webapps/finance',
    }
    return render_to_response('generic/alert-redirect.phtml', template_args, context_instance=RequestContext(request))
  
  organizations = request.user.signator_set.all()
  
  if len(organizations) == 0:
    template_args = {
      'title' : 'Error!',
      'message' : 'Error! You can not create a budget unless you register an organization in the organization manager... When you click ok you will be redirected there',
      'redirect' : '/webapps/organizations/my_organizations'
    }
    return render_to_response('generic/alert-redirect.phtml', template_args, context_instance=RequestContext(request))
  
  template_args = {
    'user' : request.user,
    'organizations' : organizations,
  }
  
  return render_to_response('finance/create-budget.html', template_args, context_instance=RequestContext(request))

def my_budgets(request):
  factor = authenticate(request, VALID_FACTORS)
  
  organizations = request.user.signator_set.select_related().all()
  
  unapproved_budgets = []
  approved_budgets = []
  
  for o in organizations:
    unapproved_budgets.extend(o.budget_set.filter(approved = 0))
    approved_budgets.extend(o.budget_set.filter(approved = 1))
  
  template_args = {
    'unapproved_budgets' : unapproved_budgets,
    'approved_budgets' : approved_budgets
  }
  
  return render_to_response('finance/my-budgets-list.html', template_args, context_instance=RequestContext(request))

def edit_my_budget(request, budget_id):
  factor = authenticate(request, VALID_FACTORS)
  
  budget = Budget.objects.get(id = budget_id)
  
  if budget.organization.signator != request.user:
    raise Http400()
  
  items = budget.budgetitem_set.all()
  
  template_args = {
    'user' : request.user,
    'org' : budget.organization, 
    'budget' : budget,
    'items' : items,
  }
  
  return render_to_response('finance/edit-budget.html', template_args, context_instance=RequestContext(request))

def budget_respond_get(request, budget_id):
  factor = authenticate(request, ADMIN_FACTORS)
  
  budget = Budget.objects.get(id = budget_id)
    
  items = budget.budgetitem_set.all()
  
  template_args = {
    'admin' : is_admin_factor(factor),
    'user' : request.user,
    'budget' : budget,
    'items' : items
  }
  
  return render_to_response('finance/budget-response-detail.html', template_args, context_instance=RequestContext(request))

def budget_respond_post(request, budget_id):
  factor = authenticate(request, ADMIN_FACTORS)
  
  if request.method != 'POST':
    raise Http401
  
  budget = Budget.objects.select_related().get(id = budget_id)
  d = request.POST.copy()
  
  budget.response = d['main-response']
  finalize = d['save'] == "Submit Response"
  budget.approved = finalize
  
  del d['main-response']
  
  total_allocated = 0
  total_claimed = 0
  
  for item in budget.budgetitem_set.all():
    id = item.id
    allocated = d['allocation-' + str(id)]
    claimed = d['claimed-' + str(id)]
    response = d['response-' + str(id)]
    item.allocated = allocated
    item.claimed = claimed
    item.response = response
    item.save()
    total_allocated = total_allocated + float(allocated)
    total_claimed = total_claimed + float(claimed)
  
  budget.allocated = str(total_allocated)
  budget.claimed = str(total_claimed)
  budget.save()
  
  url = '/webapps/finance/view_budgets/respond/edit/%s' % budget_id
  
  return HttpResponsePermanentRedirect(url)

def delete_my_budget(request, budget_id):
  factor = authenticate(request, VALID_FACTORS)
  
  if request.method != 'POST':
    raise Http401()
  
  budget = Budget.objects.get(id = budget_id)
  
  if budget.organization.signator != request.user or budget.is_approved():
    raise Http403()
  
  items = budget.budgetitem_set.all()
  for i in items:
    i.delete()
  budget.delete()
  
  return HttpResponsePermanentRedirect('/webapps/finance/my_budgets')  

MONEY_RE = re.compile('^\$?((?:(?:\d+)|(?:\d{1,3}(?:,\d{3})*))(?:\.\d{0,2})?)$')

class InvalidCurrencyFormatException(Exception):
  def __str__(self):
    return "You have inputted an improperly formatted decimal number. Please go back and correct any errors."

def escape_money(input):
  if input == '':
    return '0'
  m = MONEY_RE.match(input)
  if m == None:
    raise InvalidCurrencyFormatException()
  return m.group(1).replace(',','')

def edit_my_budget_post(request, budget_id):
  factor = authenticate(request, VALID_FACTORS)
  
  if request.method != 'POST':
    raise Http401
  
  query = demjson.decode(request.POST['query_string'])
  org = Organization.objects.get(signator = request.user, id = query['organization'])
  
  if budget_id == '':
    budget = Budget()
    budget.organization = org
    budget.description = query['description']
    budget.requested = 0
    budget.allocated = 0
    budget.claimed = 0
    budget.save()
  else:
    budget = org.budget_set.get(id = budget_id)
    budget.description = query['description']
    budget.save()
    current_items = budget.budgetitem_set.all()
    for i in current_items:
      i.delete()
  
  total_requested = 0
  for i in query['budget_items']:
    item = BudgetItem()
    item.budget = budget
    item.name = i['name']
    item.description = i['description']
    requested = escape_money(i['requested'])
    item.requested = requested
    item.allocated = 0
    item.claimed = 0
    total_requested = total_requested + float(requested)
    item.save()
  budget.requested = str(total_requested)
  budget.save()
  
  return HttpResponsePermanentRedirect('/webapps/finance/my_budgets')
  
def budget_search(request):
  if request.method != 'GET':
    raise Http400

  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)
  try:
    orgName = request.GET['org']
  except MultiValueDictKeyError:
    return render_to_response('finance/organization-budgets.html',context_instance=RequestContext(request))
  
  if orgName == 'Organization Name' or orgName == '':
    return render_to_response('finance/organization-budgets.html',context_instance=RequestContext(request))

  try:
    org = Organization.objects.get(name__icontains=orgName)
  except MultipleObjectsReturned:
    orgs = Organization.objects.select_related().order_by('name').filter(name__icontains=orgName)
    template_args = {
      "searchTerm" : orgName,
      "orgs" : orgs
    }
    return render_to_response('finance/organization-disambig.html', template_args,context_instance=RequestContext(request))
  except Organization.DoesNotExist:
    orgs = []
    
    template_args = {
      'searchTerm' : orgName
    }
    return render_to_response('finance/organization-budgets.html', template_args,context_instance=RequestContext(request))

  budgets = Budget.objects.select_related().order_by('-created_on').filter(organization = org)

  template_args = {
  	'admin' : admin,
    'budgets' : budgets,
    'organization' : org
  }

  return  render_to_response('finance/organization-budgets.html', template_args,context_instance=RequestContext(request))

def add_signator(request):
  authenticate(request, ADMIN_FACTORS)
  factor = authenticate(request, VALID_FACTORS)
  admin = is_admin_factor(factor)
## MK 9/1/10
  currentSignators = SinUser.objects.filter(attended_signator_training = 1);
  if not admin:
    return HttpResponseRedirect('/webapps/finance')

  try:
    uid = request.POST['uid']
  except MultiValueDictKeyError:
    return render_to_response('finance/signator.html',{"currentSignators":currentSignators},context_instance=RequestContext(request))

  try:
    student = SinUser.objects.get(username__iexact=uid)
    student.attended_signator_training = True
    student.save()
    result = "<span class=\"okay\">" + student.first_name + " " + student.last_name + " is now a signator!</span>"
  except:
    result = "<span class=\"error\">No student with username \"" + uid + "\" was found in the system.</span>"


  template_args = {
    "result" : result,
    "currentSignators" : currentSignators 
 }

  return render_to_response('finance/signator.html', template_args,context_instance=RequestContext(request))
