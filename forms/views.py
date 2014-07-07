import demjson

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from webapps.generic.errors import *
from webapps.generic.models import *
from webapps.forms.models import *

VALID_FACTORS = [
  'admin',
  'student',
]

def my_forms(request):
  factor = authenticate(request, VALID_FACTORS)
  admin = (factor == 'admin')
  
  if not admin:
    template_args = {
      'forms' : FormModel.objects.filter(organization__signator = request.user)
      }
  else:
    template_args = {
      'forms' : FormModel.objects.all(),
      }
  return render_to_response('forms/my_forms.phtml', template_args, context_instance=RequestContext(request))

def delete_my_form(request, form_model_id):
  authenticate(request, VALID_FACTORS)
  
  form_model = FormModel.objects.select_related().get(organization__signator = request.user, id = form_model_id) 
  form_data_set = form_model.formdata_set.all()
  for form_d in form_data_set:
    for field_d in form_d.formfielddata_set.all():
      field_d.delete()
    form_d.delete()
  for field in form_model.formfieldmodel_set.all():
    field.delete()
  form_model.delete()
  
  return HttpResponsePermanentRedirect('/webapps/forms/my_forms/')

def clear_my_form(request, form_model_id):
  authenticate(request, VALID_FACTORS)
  
  if not request.user.is_admin():
    form_model = FormModel.objects.select_related().get(organization__signator = request.user, id = form_model_id)
  else:
    form_model = FormModel.objects.select_related().get(id = form_model_id)
  
  for form_d in form_model.formdata_set.all():
    for field_d in form_d.formfielddata_set.all():
      field_d.delete()
    form_d.delete()
  
  return HttpResponsePermanentRedirect('/webapps/forms/my_forms/')

class AlreadySubmittedApplicationException(Exception):
  def __str__(self):
    return "Unable to edit form since form applications have already been submitted. Please clear the form applications and then edit the form again."

def edit_my_form(request, form_model_id):
  authenticate(request, VALID_FACTORS)
  
  if request.method == 'POST' or request.method == 'post':
    query = demjson.decode(request.POST['query_string'])
    if form_model_id == "":
      form_model = FormModel()
    else:
      form_model = FormModel.objects.get(id = form_model_id)
      field_model_list = form_model.formfieldmodel_set.all()
      for f in field_model_list:
        try:
          f.delete()
        except:
          raise AlreadySubmittedApplicationException()
    
    form_model.name = query['title']
    form_model.description = query['description']
    org_id = query['org_id']
    form_model.organization = Organization.objects.get(id = org_id, signator = request.user)
    form_model.email_signator = query['email_signator']
    form_model.save()
    
    for field in query['field_list']:
      f = FormFieldModel(form_model = form_model,
                         title = field['title'],
                         type = field['type'],
                         core = field['core'],
                         admin_only = field['admin_only'])
      f.save()
    return HttpResponsePermanentRedirect('/webapps/forms/my_forms/')
  else:
    if form_model_id == "":
      form_model = None
    else:
      form_model = FormModel.objects.get(id = form_model_id)
    
#    if FormData.objects.filter(form_model = form_model).count() != 0:
#      raise AlreadySubmittedApplicationException()
    
    organizations = request.user.signator_set.all()
    
    template_args = {
      'user' : request.user,
      'organizations' : organizations,
      'form_model' : form_model
      }
    
    return render_to_response('forms/edit_form.phtml',template_args, context_instance=RequestContext(request))

def anonymous_form_list(request):
#  authenticate(request,VALID_FACTORS)
  
  template_args = {
    'form_models' : FormModel.objects.all()
  }
  
  return render_to_response('forms/anonymous_form_list.phtml', template_args, context_instance=RequestContext(request))

def anonymous_form_detail(request, form_model_id):
#  authenticate(request, VALID_FACTORS)
  
  if request.method == 'POST':
    query = request.POST
    _form_model = FormModel.objects.get(id = form_model_id)
    
    form_data = FormData()
    form_data.form_model = _form_model
    form_data.user = request.user
    form_data.save()
    
    for f in query:
      _field_model = FormFieldModel.objects.get(id = f)
      field_data_class = CLASS_MAP[_field_model.type]
      field = field_data_class()
      field.field_model = _field_model
      field.form_data = form_data
      field.value = query[f]
      field.save()
    
    if _form_model.email_signator == 1:
      form_data.mail_to_signator()
    elif _form_model.email_signator == 2:
      form_data.digest_to_signator()
    
    return render_to_response('forms/thank_you.phtml', context_instance=RequestContext(request))
  
  form_model = FormModel.objects.get(id = form_model_id)
  
  template_args = {
    'model' : form_model,
    'fields' : form_model.formfieldmodel_set.all().order_by('id'),
  }
  
  return render_to_response('forms/anonymous_form_detail.phtml',template_args, context_instance=RequestContext(request))

def result_list(request, form_model_id):
  factor = authenticate(request, VALID_FACTORS)
  admin = (factor == 'admin')
  
  form_model = FormModel.objects.get(id = form_model_id)
  
  if form_model.organization.signator != request.user and not admin:
    return HttpResponse403()
  
  if request.GET.get('csv',None):
    return csv_result_list(form_model)
  
  template_args = {
    'model' : form_model,
    'fields' : form_model.formfieldmodel_set.select_related().all(),
    'form_data' : form_model.formdata_set.select_related().all(),
  }
  
  return render_to_response('forms/result_list.phtml',template_args, context_instance=RequestContext(request))

def csv_result_list(model):
  fields = model.formfieldmodel_set.all()
  results = model.formdata_set.select_related().all()
  names = [f.title for f in fields]
  values = [r.get_field_data() for r in results]
  
  import csv, cStringIO
  output = cStringIO.StringIO()
  writer = csv.writer(output, dialect = csv.excel)
  
  writer.writerow([n.encode("utf-8") for n in names])
  
  def escape(v):
    return unicode(v.get_value()).encode("utf-8")
  
  def get_row(s):
    return [escape(d) for d in s]
  
  writer.writerows([get_row(v) for v in values])
  resultant = output.getvalue()
  output.close()
  
  response = HttpResponse(resultant, mimetype = "text/csv")
  response['Content-Disposition'] = 'attachment; filename=formresults.csv'
  
  return response

def result_detail(request, form_data_id):
  factor = authenticate(request, VALID_FACTORS)
  admin = (factor == 'admin')
  
  if request.method != 'GET':
    return HttpResponse400()
  
  if request.GET.get('as_csv',False) != False:
    return result_detail_csv(request, form_data_id)
  
  form_data = FormData.objects.select_related().get(id = form_data_id)
  user = form_data.user
  
  if form_data.form_model.organization.signator != request.user and not admin:
    return HttpResponse403()
  
  template_args = {
    'user' : user,
    'data' : form_data,
  }
  
  return render_to_response('forms/result_detail.phtml',template_args, context_instance=RequestContext(request))

def result_detail_csv(request, form_id):
  form_model = FormModel.objects.select_related().get(id = form_id)
  
  if form_model.organization.signator != request.user:
    return HttpResponse403()
  
  form_fields = form_model.formfieldmodel_set.all()
  form_data_list = form_model.formdata_set.select_related().all()
  
  message = "User,"
  
  # Make header
  for f in form_fields:
    message = "%s%s," % (message,f.name)
  message = message[:-1] + "\n"
  
  for f in form_data_list:
    message = "%s%s," % (message, f.user.get_full_name())
    for f in fields:
      field_data = f.formfielddata_set.filter(field_model = f)[0]
      message = "%s%s," % (message, field_data.value)
    message = message[:-1] + "\n"
  
  r = HttpResponse(message, mimetype = "text/csv")
  r['Content-Disposition'] = 'attachment; filename=%s_data.csv' % form_model.name
  return r
