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

    ### This is to determine whether or not to display a link
    ### to the user's registrations under the Funding Poll
    ### dropdown.
    ## Sloppy now-- only omits the link if it is BEFORE registation
    ## just in case reg closes and the signator needs to check their
    ## orgs are stil registered.
    ## -BB (1/22/14)

    return render_to_response('VotW/index.phtml',context_instance=RequestContext(request))

