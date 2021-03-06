import os, sys

from django.http import HttpResponsePermanentRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext

from webapps.generic.views import *
from webapps.generic.models import *
from webapps.generic.errors import *

VALID_FACTORS = [
    'student'
]

def index(request):
    authenticate(request, VALID_FACTORS)
    return render_to_response('home/index.html',context_instance=RequestContext(request))

