from datetime import datetime

from django.db import models

from webapps.generic.models import * 
from webapps.generic.errors import Http400
from webapps.finance.models import Budget, BudgetItem

from webapps.fundingpoll.manager import FundingPollVoteManager

BEFORE_R = "before_registration"
DURING_R = "during_registration"
BEFORE_V = "before_voting"
DURING_V = "during_voting"
BEFORE_B = "before_budgets"
DURING_B = "during_budgets"
END_B = "end_budgets"

class FundingPoll(models.Model):
  start_registration = models.DateTimeField()
  end_registration = models.DateTimeField()
  start_voting = models.DateTimeField()
  end_voting = models.DateTimeField()
  start_budgets = models.DateTimeField()
  end_budgets = models.DateTimeField()
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
  
  def get_status(self):
    today = datetime.today()
    if self.before(today, self.start_registration):
      return BEFORE_R
    elif self.before(today, self.end_registration):
      return DURING_R
    elif self.before(today, self.start_voting):
      return BEFORE_V
    elif self.before(today, self.end_voting):
      return DURING_V
    elif self.before(today, self.start_budgets):
      return BEFORE_B
    elif self.before(today, self.end_budgets):
      return DURING_B
    else:
      return END_B
  
  def before(self, date1, date2):
    fields = [
      'days',
      'seconds',
      'microseconds'
    ]
    t = date2 - date1
    for f in fields:
      if t.__getattribute__(f) < 0:
        return False
    return True

def get_fp():
  return FundingPoll.objects.latest('created_on')

SCALAR_CHOICES = [
  (8, 'Top Six'),
  (2, 'Approve'),
  (0, 'No Opinion'),
  (-1, 'Disapprove'),
  (-4, 'Deep Six')
]

class FundingPollOrganization(models.Model):
  funding_poll = models.ForeignKey(FundingPoll)
  organization = models.ForeignKey(Organization)
  other_signators = models.CharField(max_length = 50)
  comment = models.TextField()
  total_votes = models.IntegerField()
  top_six = models.IntegerField()
  approve = models.IntegerField()
  no_opinion = models.IntegerField()
  disapprove = models.IntegerField()
  deep_six = models.IntegerField()
  
  ordering = models.FloatField(default = 0.0)
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
  
  def save(self, force_insert = False, force_update = False):
    if self.ordering == 0.0:
      import random
      self.ordering = random.random()
    models.Model.save(self, force_insert, force_update)

  def __unicode__(self):
    return u'%s' % (self.organization.name)

# dont forget when you syncdb to make a large unique index
class FundingPollBudget(models.Model):
  signator_user = models.ForeignKey(SinUser)
  # organization should be a one to one field
  organization = models.ForeignKey(FundingPollOrganization)
  description = models.TextField()
  response = models.TextField()
  requested = models.DecimalField(max_digits = 8, decimal_places = 2)
  allocated = models.DecimalField(max_digits = 8, decimal_places = 2)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)

class FundingPollBudgetItem(models.Model):
  name = models.CharField(max_length = 50)
  description = models.TextField()
  response = models.TextField()
  budget = models.ForeignKey(FundingPollBudget)
  requested = models.DecimalField(max_digits = 8, decimal_places = 2)
  allocated = models.DecimalField(max_digits = 8, decimal_places = 2)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)

class FundingPollVote(models.Model):
  objects = FundingPollVoteManager()
  funding_poll = models.ForeignKey(FundingPoll)
  organization = models.ForeignKey(FundingPollOrganization)
  voter = models.ForeignKey(SinUser)
  scalar = models.IntegerField(choices = SCALAR_CHOICES)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)

## MK 1/30/10 stopgap hack to make it easier to manually reg orgs for fp
def manual_reg_org(org_id):
 fp = get_fp()

 org = Organization.objects.get(id = org_id)
 try:
     f_org = fp.fundingpollorganization_set.select_related().get(organization__id = org_id)
 except Exception:
     f_org = FundingPollOrganization(organization = org,
                                     funding_poll = fp,
                                     total_votes = 0,
                                     top_six = 0,
                                     approve = 0,
                                     no_opinion = 0,
                                     disapprove = 0,
                                     deep_six = 0)
     f_org.save()
 return f_org

def is_registered(org_id):
  fp = get_fp()
  org = Organization.objects.get(id = org_id)
  try: 
    f_org = fp.fundingpollorganization_set.select_related().get(organization__id = org_id)
    return True
  except: 
    return False

def fetch_not_registered_orgs(signator):
  """ Returns a queryset of organizations, signated by a given signator, that are not yet registered for the current funding poll.  """
  need_registration = []
  try:
    orgs = signator.signator_set.all()
    for i in orgs:
      if (not is_registered(i.id)):
        need_registration.append(i)
    return need_registration
  except: 
    #RECURSIVELY FIX THIS - Intend to raise exception, but forget syntax ATM
    return []


  
