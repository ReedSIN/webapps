from django.db import models

from django.forms import ModelForm
from webapps.generic.models import SinUser

class SBInfoEntry(models.Model):
  contact = models.ForeignKey(SinUser)
  title = models.CharField(max_length = 50)
  message = models.TextField()
  starts_on = models.DateTimeField(auto_now = True)
  run_duration = models.IntegerField()

#  def is_active(self):
#    # if today is after starts_on + run_duration
#
#  def get_all_active():
#    for entry in SBInfoEntry.objects.all():
#      if entry.is_active() yield entry
