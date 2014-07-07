##########################################
# BB (Jan, 2014)
# 
# OVERVIEW
# This script converts a CSV of signators'
# Reed usernames into Django commands that
# update the signator database
#
# USAGE
# Make sure that FinCom's CSV has two cols
#    column1: kerberos, no @
#    column2: first and last name
# Place the file in a folder
# Set the FOLDER_PATH variable
#    use a trailing backslash
# 
#
# ERROR HANDLING
##########################################
# TODO:
#

import csv
from webapps.finance.models import *

SIG_FOLDER_PATH = '/var/django/webapps/utility/forSigSkript/'

def SS_add(sig):
    sig.attended_signator_training = 1
    sig.save()

def SS_run(file_name):
  sig_file = open(SIG_FOLDER_PATH + file_name,"rb")
  # JM - Why "rb" above? 
  reader = csv.reader(sig_file)

  row_count = 0
  fail_count = 0
  suspect_count = 0
  fails = []

  for row in reader:
      if row_count != 0:
          sig_un = row[0].strip()  # Trim whitespace
          sig_un = sig_un.split("@")[0] #in case they put in their full email
          try:
              homie = SinUser.objects.get(username = sig_un)
              SS_add(homie)
          except SinUser.DoesNotExist:
              suspect_count += 1
              try:
                  SinUser.get_ldap_user(username = sig_un)
                  homie = SinUser.objects.get(username = sig_un)
                  SS_add(homie)
              except ldap.NO_SUCH_OBJECT:
                  fails.append([ row[0], row[1] ])
                  fail_count += 1
      row_count += 1

  print 'Skript encountered %d suspect entries. %d were not resolved.' % (suspect_count,fail_count)

  if fail_count == 0:
      print 'Yayyyyyyy. All signators were added!'
  else:
      print 'Here is the list of failures...'
      for fail in fails:
          print 'Username %s with written name %s is a FAILURE' % (fail[0],fail[1]) 
      
