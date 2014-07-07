from django.db import models
from django.forms import ModelForm
from webapps.generic.models import SinUser

class Position(models.Model):
  name = models.CharField(max_length = 50)
  contact = models.ForeignKey(SinUser)
  description = models.TextField()
  expires_on = models.DateTimeField()
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)

class PositionModelForm(ModelForm):
  class Meta:
    model = Position
    fields = ('name','contact','description','expires_on')

YEARS = (
  (0, 'Freshman'),
  (1, 'Sophomore'),
  (2, 'Junior'),
  (3, 'Senior')
)

YEAR_DICT = {
 0 : 'Freshman',
 1 : 'Sophomore',
 2 : 'Junior',
 3 : 'Senior',
 'Freshman' : 0,
 'Sophomore': 1,
 'Junior' : 2,
 'Senior' : 3,
}


class Application(models.Model):
  applicant = models.ForeignKey(SinUser)
  preferred_pron = models.CharField(max_length = 10, blank=True)
  position = models.ForeignKey(Position)
  major = models.CharField(max_length = 30)
  year = models.IntegerField(max_length = 1, choices = YEARS)
  address = models.CharField(max_length = 50)
  phone = models.CharField(max_length = 15)
  email = models.EmailField()
  schedule_conflicts = models.TextField()
  other_reed_positions = models.TextField()
  other_employment = models.TextField()
  experience = models.TextField()
  motivation = models.TextField()
  special_skills = models.TextField()
  appeal = models.TextField()
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)

class ApplicationModelForm(ModelForm):
  class Meta:
    model = Application
    exclude = ('created_on','modified_on')
