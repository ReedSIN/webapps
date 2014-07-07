#!/usr/bin/env python

import os, sys

DJANGO_ROOT = os.path.dirname(os.getcwd())
ROOT = os.path.dirname(DJANGO_ROOT)

sys.path.append(DJANGO_ROOT)
sys.path.append(ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps.settings'

import webapps.sin_email.models as dmodels

digests = dmodels.Digest.objects.all()

for d in digests:
  d.send_digest()
  for m in d.digestmessage_set.all():
    m.delete()
  d.delete()
