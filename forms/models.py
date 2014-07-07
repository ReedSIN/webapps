from django.db import models

from webapps.generic.models import *
from webapps.generic.views import *
from webapps.sin_email.models import *

class FormModel(models.Model):
  name = models.CharField(max_length = 50)
  description = models.TextField()
  organization = models.ForeignKey(Organization)
  
  email_signator = models.IntegerField(default = 0)
  user_restricted_list = models.ForeignKey(SinUser, related_name = 'restricted_form', null = True)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
  
  def __str__(self):
    return self.name

CLASS_TYPE_MAP = {
  0 : 'text',
  1 : 'textarea',
  2 : 'radio',
}

EMAIL_SIGNATOR_MAP = {
  0 : 'none',
  1 : 'single',
  2 : 'digest'
}

def inverse_map(m):
  new_map = {}
  for x in m:
    new_map[m[x]] = x  
  return new_map

INVERSE_CLASS_TYPE_MAP = inverse_map(CLASS_TYPE_MAP)
INVERSE_EMAIL_SIGNATOR_MAP = inverse_map(EMAIL_SIGNATOR_MAP)

class FormFieldModel(models.Model):
  form_model = models.ForeignKey(FormModel)
  title = models.CharField(max_length = 200)
  type = models.IntegerField()
  core = models.BooleanField(default = True)
  admin_only = models.BooleanField(default = False)
  
  def get_type(self):
    return CLASS_TYPE_MAP[self.type]
  
  def is_textarea(self):
    return self.type == INVERSE_CLASS_TYPE_MAP['textarea']
  
  def __str__(self):
    return self.title

class FormData(models.Model):
  user = models.ForeignKey(SinUser)
  form_model = models.ForeignKey(FormModel)
  
  subject_template = "[SIN]: New %s submitted"
  message_template = "Form %s:\n\n"
  
  def get_field_data(self):
    return FormFieldData.objects.select_related().order_by('field_model__id').filter(form_data = self)
  
  def get_message(self):
    message = self.message_template % self.form_model.name
    for f in self.form_model.formfieldmodel_set.select_related().order_by('id'):
      data = FormFieldData.objects.get(field_model = f, form_data = self).get_value()
      message = "%s%s: %s\n" % (message,f.title,data)
    return message
  
  def mail_to_signator(self):
    signator_email = self.form_model.organization.signator.email
    subject = self.subject_template % self.form_model.name
    message = self.get_message()
    send_mail(subject, message, signator_email)
  
  def digest_to_signator(self):
    _subject = self.subject_template % self.form_model.name
    digest = None
    try:
      digest = Digest.objects.get(subject = _subject)
    except:
      signator_email = self.form_model.organization.signator
      digest = Digest(recipient = signator_email,
                      subject = _subject)
      digest.save()
    
    message = DigestMessage(parent = digest, message = self.get_message())
    message.save()

class AbstractMethod(Exception): pass

class FormFieldData(models.Model):
  field_model = models.ForeignKey(FormFieldModel)
  form_data = models.ForeignKey(FormData)
  
  def get_value(self):
    try:
      return unicode(self.textfielddata)
    except:
      try:
        return unicode(self.textareadata)
      except:
        try:
          return unicode(self.radiomultidata)
        except:
          return unicode(None)

class TextFieldData(FormFieldData):
  parent = models.OneToOneField(FormFieldData)
  value = models.CharField(max_length = 120)
  
  def __str__(self):
    return unicode(self.value).encode('utf-8')

class TextAreaData(FormFieldData):
  parent = models.OneToOneField(FormFieldData)
  value = models.TextField()
  
  def __str__(self):
    return unicode(self.value).encode('utf-8')

class RadioMultiData(FormFieldData):
  parent = models.OneToOneField(FormFieldData)
  
  def __str__(self):
    data = map(lambda r: unicode("%s").encode("utf-8") % r,self.radioindidata_set.all())
    return unicode(";").encode("utf-8").join(data)

class RadioIndiData(FormFieldData):
  parent = models.ForeignKey(RadioMultiData)
  name = models.CharField(max_length = 50)
  value = models.BooleanField(default = False)
  
  def __str__(self):
    return unicode("%s:%s").encode("utf-8") % (self.name,self.value)

CLASS_MAP = {
  0 : TextFieldData,
  1 : TextAreaData,
  2 : RadioMultiData,
}
