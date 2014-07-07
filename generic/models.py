from django.db import models
from django.contrib.auth.models import User, UserManager
from webapps.settings import SERVER_EMAIL
#from webapps.cu_model import SinUser
import ldap, ldap.async

FACTOR_LIST = [
  "admin",
  "senator",
  "finance",
  "appointments",
  "student",
  "fundingpoll",
  "faculty",
  "yearbook",
  "posts_mod",
  "elections",
]

FACTORS = {
  0 : "admin",
  "admin" : 0,
  1 : "senator",
  "senator" : 1,
  2 : "finance",
  "finance" : 2,
  3 : "appointments",
  "appointments" : 3,
  4 : "student",
  "student" : 4,
  5 : "fundingpoll",
  "fundingpoll" : 5,
  6 : "faculty",
  "faculty" : 6,
  7 : "yearbook",
  "yearbook" : 7,
  8 : "posts_mod",
  "posts_mod" : 8,
  9 : "elections",
  "elections" : 9,
}

class SinUser(User):
  ''' User with custom SIN properties and methods. '''
  attended_signator_training = models.BooleanField(default = False)
 
  from django.core import mail

  class Meta:
    ordering = ["last_name"]
  
  @classmethod
  def ldap_lookup_user(cls, username):
    server = "ldap://ldap.reed.edu:389/"
    query = "uid=%s,ou=people,dc=reed,dc=edu" % username
    
    s = ldap.async.List(ldap.initialize(server))
    s.startSearch(query, ldap.SCOPE_SUBTREE, '(objectClass=*)')
    
    try:
      partial = s.processResults()
    except ldap.SIZELIMIT_EXCEEDED: pass
    
    return list(s.allResults)
  
  @classmethod
  def get_ldap_user(cls, username):
    results = SinUser.ldap_lookup_user(username)
    
    u = SinUser()
    
    user_dict = results[0][1][1]
    
#    name = user_dict["cn"][0].split()
    affiliation = user_dict['eduPersonPrimaryAffiliation'][0]
    
    u.username = user_dict["uid"][0]
#    u.first_name = name[0]
#    u.last_name = name[1]
    try:
        u.first_name = user_dict["givenName"][0]
    except KeyError:
        u.first_name = " "
    u.last_name = user_dict["sn"][0]
    u.email = user_dict["mail"][0]
    u.factors = 0
    u.save()
    
    factor_list = []
    if affiliation in FACTORS:
      factor_list.append(affiliation)
# next line - beginning-of-year fix for students still counted as "applicants"
    #if affiliation == "applicant":
    factor_list.append("student")
    u.set_factor_list(factor_list)
    
    u.save()
    return u

  def refresh_from_ldap(self):
    results = SinUser.ldap_lookup_user(self.username)
    user_dict = results[0][1][1]
    affiliation = user_dict['eduPersonPrimaryAffiliation'][0]
    self.username = user_dict["uid"][0]
    self.first_name = user_dict["givenName"][0]
    self.last_name = user_dict["sn"][0]
    try:
    ## will fail on alumni, who do not have the "mail" attribute
      self.email = user_dict["mail"][0]
    except:
      pass
    
    ## they may have originally been created as a non-student (e.g. applicant)
    ## so need to add the student factor if applicable 
    factor_list = []
    if affiliation in FACTORS:
      factor_list.append(affiliation)
    # next line - beginning-of-year fix for students still counted as "applicants"
    #if affiliation == "applicant":
    factor_list.append("student")
    self.add_factors(factor_list)

    self.save()
    return self
  def is_in_ldap(self):
    server = "ldap://ldap.reed.edu:389/"
    query = "uid=%s,ou=people,dc=reed,dc=edu"
    
    s = ldap.async.List(ldap.initialize(server))
    s.startSearch(query, ldap.SCOPE_SUBTREE, '(objectClass=*)')
    
    try:
      partial = s.processResults()
    except ldap.SIZELIMIT_EXCEEDED: pass
    
    results = list(s.allResults)
  
  def get_factor_list(self):
    return map(lambda x: str(x),self.factor_set.all())
  
  def set_factor_list(self, factor_list):
    for f in Factor.objects.all():
      if str(f) in factor_list:
        if not self in f.users.all():
          f.users.add(self)
      else:
        if self in f.users.all():
          f.users.remove(self)

  def add_factors(self,factor_list):
    for f in Factor.objects.all():
      if str(f) in factor_list:
        if not self in f.users.all():
          f.users.add(self)

  def is_admin(self):
    return self.factor_set.filter(name = 'admin') != []

  def is_posts_mod(self):
    post_mod = Factor.objects.get(name="posts_mod")
    if post_mod in self.factor_set.all():
      return True
    else: 
      return False
  
  def get_full_name(self):
    return str(self)
  
  def __unicode__(self):
    return "%s %s" % (self.first_name, self.last_name)
  
  def send_mail(self, subject, message, sender = SERVER_EMAIL):
    # subject, message, to
    self.mail.send_mail(subject, message, sender, [self.email], fail_silently = False)

#  objects = UserManger()

class Factor(models.Model):
  name = models.CharField(max_length = 50)
  users = models.ManyToManyField(SinUser)
  
  def __str__(self):
    return self.name


class Organization(models.Model):
  name = models.CharField(max_length = 100)
  signator = models.ForeignKey(SinUser, related_name = "signator_set")
  
  location = models.CharField(max_length = 100)
  phone_number = models.CharField(max_length = 20)
  email = models.EmailField()
  website = models.CharField(max_length = 200)
  
  description = models.TextField()
  meeting_info = models.TextField()
  annual_events = models.TextField()
  associated_off_campus_organizations = models.TextField()
  
  public_post_ok = models.BooleanField(default = False)
  referral_info = models.TextField()
  
  enabled = models.BooleanField(default = True)
  archived = models.BooleanField(default = False)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
  
  def send_mail_to_signator(self, subject, message):
    self.signator.send_mail(subject, message)
  
  def __str__(self):
    return self.name
  
  disable_subject = """IMPORTANT - %s has been disabled"""
  disable_message = """<html><body><p>Dear %s,</p>
<p>As you may or may not know, the current policy of SIN is to disable all student organizations at the beginning of each semester. This is in order to maintain a fresh record of student organizations and remove student organizations that are no longer active.</p><p>To renew your organization please visit the following link: <a href="%s">%s</a></p></body></html>"""
  reenable_url = "http://sin.reed.edu/webapps/organization-manager/orgs/%i/renew/"
  
  def disable(self):
    self.enabled = False
    self.save()
    
    url = Organization.reenable_url % self.id
    subject = disable_subject % self.name
    message = disable_message % (self.signator.get_full_name(),url,url)
    
    self.send_mail_to_signator(subject,message)
