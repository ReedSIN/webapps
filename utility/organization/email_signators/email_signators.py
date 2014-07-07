## MK 2011/8/3 This is a useful script, so not archiving, but I don't have time to fix it now

#!/usr/bin/env python

import os, sys

def get_root():
  d = os.path.dirname
  return d(d(d(d(os.path.abspath(__file__)))))

DJANGO_ROOT =  get_root()
WORKSPACE_ROOT = os.path.dirname(DJANGO_ROOT)

for d in os.listdir(DJANGO_ROOT):
  sys.path.append(os.path.abspath(d))

sys.path.append(DJANGO_ROOT)
sys.path.append(WORKSPACE_ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps.settings'

from webapps.generic.models import User, Organization
from webapps.fundingpoll.models import FundingPollOrganization
from webapps.generic.views import send_mail

import demjson

email = demjson.decode(sys.stdin.read())

subject = email['subject']
message = email['message']
#target_source = email['target_source']

#if isinstance(target_source,list):
#  targets = target_source
#else:
#  f = open(target_source)
#  data = f.readlines()
#  f.close()  
#  targets = map(lambda u: u.strip(),data)

#def get_user(u):
#  try:
#    return User.objects.get(username = u)
#  except:
#    print u

#signator_list = map(get_user,targets)
#signator_list = [o.organization.signator for o in FundingPollOrganization.objects.all()]
orgs = Organization.objects.all()
o_list = []
for o in orgs:
  if o.fundingpollorganization_set.count() == 0:
    o_list.append(o)

#orgs = Organization.objects.filter(signator = User.objects.get(id = 1))

subject2 = "You are registered in Funding Poll"
message2 = "Oops, you are really in funding poll. My apologies, I by mistake sent an email which was supposed to only go to people who are not on funding poll to all signators. My apologies, dont freak out...\n\nMichael"

for o in orgs:
  if not o in o_list:
    #print o.name
    send_mail(subject2 ,message2 , o.signator.email)
