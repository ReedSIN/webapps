from django.db import models

from webapps.generic.models import SinUser
from webapps.generic.views import send_mail

class Digest(models.Model):
  subject = models.CharField(max_length = 100)
  recipient = models.ForeignKey(SinUser)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
  
  def send_digest(self):
    messages = self.digestmessage_set.all()
    full_text = ""
    for m in messages:
      full_text = full_text + m.render() + "\n"
    send_mail(self.subject,full_text,self.recipient.email)

class DigestMessage(models.Model):
  parent = models.ForeignKey(Digest)
  message = models.TextField()
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
  
  def render(self):
    return "Created On: %s\nModified On: %s\nMessage:\n%s\n" % (self.created_on,self.modified_on,self.message)
