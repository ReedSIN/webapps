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
from webapps.fundingpoll.models import FundingPollOrganization, get_fp, get_top_40
from webapps.generic.views import send_mail

import demjson

class Mailer(object):
  def __init__(self):
    asdf
  def send_to_all_users(self, subject, message):
    for u in User.objects.all():
      u.send_mail(subject, message)
  def send_to_students(self, subject, message):
    raise Exception("Not implemented")
  def send_to_all_signators(self, subject, message):
    for o in Organization.objects.select_related().all():
      o.send_mail_to_signator(subject, message)
  def send_to_registered_fundingpoll_signators(self, subject, message):
    fp = get_fp()
    for forg in fp.fundingpollorganization_set.select_related().all():
      forg.organization.send_mail_to_signator(subject, message)
  def send_to_unregistered_fundingpoll_signators(self, subject, message):
    orgs = Organization.objects.select_related().all()
    org_list = []
    for o in orgs:
      if orgs.fundingpollorganization_set
  def send_to_top40(self, subject, message):
    forgs = get_top_40()
    for o in forgs:
      forgs.organization.send_mail_to_signator(subject, message)
