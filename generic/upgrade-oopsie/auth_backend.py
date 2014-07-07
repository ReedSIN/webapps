# auth_backend.py:

from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured

## integrating MKs old model Backend
## BB
from webapps.generic.models import SinUser
#import ldab  ## BB - might need

def get_response():
  from django.http import HttpResponseForbidden
  from django.template.loader import render_to_string
  return HttpResponseForbidden(render_to_string('errors/http_forbidden.phtml'))

class Http403(Exception):
  _cached_response = None

  def get_response(self):
    if self._cached_response == None:
      self._cached_response = get_response()
    return self._cached_response


class SinUserModelBackend(RemoteUserBackend):
#    def clean_username(self, username):
 #     clean_username=username.split('@')[0]
  #    return clean_username

  create_unknown_user = False

  def authenticate(self, remote_user):

    if not remote_user:
      return
#    UserModel = get_user_model()
#    user = None
    username = self.clean_username(remote_user)
    #raise ImproperlyConfigured('we are using the backend auth' + user.first_name)
    try:
      user=SinUser.objects.get(username=username)
    except SinUser.DoesNotExist:
      try: 
        user=SinUser.get_from_ldap(username=username)
      except ldap.NO_SUCH_OBJECT:
        ImproperlyConfigured('Getting from LDAP Failed')

    return user
    #UserModel = get_user_model()
'''
    try:
      user = SinUser.objects.get(username=username)
    except SinUser.DoesNotExist:
      try:
        user = SinUser.get_ldap_user(username=username)
      except ldap.NO_SUCH_OBJECT:
        return Http403.response
      return user
'''




