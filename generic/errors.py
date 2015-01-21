from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.template.loader import render_to_string
from urllib2 import urlopen, Request, URLError
import sys

class Http400(Exception):
  def __str__(self):
    return "Bad Request"
class Http403(Exception):
  def __str__(self):
    kats = Request("http://placekitten.com/")
    try:
      dawgs = urlopen(kats)
      kittehs = dawgs.read()
      kittehs = kittehs[559:1000]
    except URLError, e:
      kittehs = "There should be a character-cat here. Instead, we got an error: " + str(e)
    return "Meow what are you getting at?<br>You don't have purrmission to be here!<br><br>" + kittehs
class Http401(Exception): pass
class HttpResponse403(HttpResponseForbidden):
  def __init__(self):
    HttpResponseForbidden.__init__(self)#,msg="You don't have permission to access the requested object.")
    # Hopefully this doesn't break the error
    self.write(render_to_string('errors/http_forbidden.phtml'))
    self.write("You don't have permission to access the requested object.")
  #return render_to_response('errors/http_forbidden.phtml', {'msg': msg}, context_instance=RequestContext(request))

class HttpResponse400(HttpResponseBadRequest):
  def __init__(self):
    HttpResponseBadRequest.__init__(self)
    self.write('<p>Bad Request. Please check your query and try again.</p>')

def server_error(request):
    template_name = 'errors/http_500.phtml'
    excinfo = sys.exc_info()[1]
    is401 = isinstance(excinfo,Http401)
    template_args = {
       'path': request.path,
       #'person': request.user.get_full_name(),
       'excinfo': excinfo,
       'is401': is401
           }
    return render_to_response(template_name, template_args, context_instance=RequestContext(request))

