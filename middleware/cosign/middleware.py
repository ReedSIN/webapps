from webapps.generic.models import SinUser

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
  
def get_user(request):
  name = request.META.get('REMOTE_USER','')
  try:
    user = SinUser.objects.get(username = name)
  except SinUser.DoesNotExist:
    user = SinUser.get_ldap_user(username = name)
  return user

class LazyUser(object):
  def __get__(self, request, obj_type=None):
    if not hasattr(request, '_cached_user'):
      request._cached_user = get_user(request)
    return request._cached_user

class CosignAuthenticationMiddleware(object):
  def process_request(self, request):
    try:
      request.__class__.user = LazyUser()
    except Http403:
      return Http403.response
    return None
