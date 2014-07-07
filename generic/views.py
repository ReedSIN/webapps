import sys, os
import ldap, ldap.async

from django.core import mail
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
#from django.views.generic.list_detail import object_list, object_detail
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponsePermanentRedirect, HttpResponse

from webapps.generic.errors import Http401
from webapps.generic.models import SinUser
from webapps.generic.models import FACTORS
from webapps.settings import SERVER_EMAIL, MANAGERS


def send_mail(subject, message, to):
  if isinstance(to,list):
    for email in to:
      mail.send_mail(subject, message, SERVER_EMAIL, [email], fail_silently = False)
  else:
    mail.send_mail(subject, message, SERVER_EMAIL, [to], fail_silently = False)

def send_admin_mail(subject,message):
  for m in MANAGERS:
    mail.send_mail(subject,message,SERVER_EMAIL, [m[1]], fail_silently = False)

def get_user(request):
  name = request.META.get('REMOTE_USER','')
  
  try:
    user = SinUser.objects.get(username = name)
  except SinUser.DoesNotExist:
    user = SinUser.get_ldap_user(username = name)
  except Exception:
    raise Http401('Something went wrong getting the user')
  return user

def ajax_user(request):
  return HttpResponse(request.META.get('REMOTE_USER',''))


def authenticate(request, valid_factors):
  
  ## weird commented out stuff is BB
  # i.e., testing from the accidental upgrade
  #raise ImproperlyConfigured(get_user(request))


## make sure they have any factors from LDAP they should have
  user = get_user(request).refresh_from_ldap()
#  raise ImproperlyConfigured(user.first_name + ' we are in views.py')
  factor_set = map(lambda x: str(x),user.factor_set.all())
  
  for f in valid_factors:
    if f in factor_set:
      return f
  raise Http401(valid_factors)

def reverse_dictionary(d):
  new_dict = {}
  for x in d:
    new_dict[d[x]] = x
  return new_dict

def logout(request):
  if request.method != 'GET':
    raise Http404
  else:
    forward_url = request.GET.get('forward_url','https://weblogin.reed.edu/cgi-bin/logout?http://sin.reed.edu')
    response = HttpResponsePermanentRedirect(forward_url)
    response.delete_cookie(key = 'cosign-sin')
    return response

def redirect_home(request):
    forward_url = '/'
    response = HttpResponsePermanentRedirect(forward_url)
    return response

def four01(request):
    VALID_FACTORS = ['NoSuchFactor']
    authenticate(request,VALID_FACTORS)
    return "Something bad happened - you shouldn't be able to see this page"

def five00(request):
    raise Http500
