import os, sys

DJANGO_ROOT =  os.path.dirname(os.path.dirname(__file__))
WORKSPACE_ROOT = os.path.dirname(DJANGO_ROOT)

for d in os.listdir(DJANGO_ROOT):
  sys.path.append(os.path.abspath(d))
  

sys.path.append(DJANGO_ROOT)
sys.path.append(WORKSPACE_ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps.settings'

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
  environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
  return _application(environ, start_response)

