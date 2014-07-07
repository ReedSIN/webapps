from datetime import datetime

from django.db import models

from webapps.generic.models import SinUser

class PaideiaClass(models.Model):
  time = models.DateTimeField()
  end = models.DateTimeField()
  name = models.CharField(max_length=100)
  teacher = models.ForeignKey(SinUser)
  teacher_name = models.CharField(max_length=100)
  length = models.IntegerField()
  location = models.CharField(max_length=100)
  
  description = models.TextField()
  notes = models.TextField()
  fbevent = models.CharField(max_length=200)

  class Meta:
    ordering = ['name']

  def __str__(self):
    return self.name

    return self.user.first_name + ' ' + self.user.last_name

class Teacher(models.Model):
  user = models.ForeignKey(SinUser)
  name = models.CharField(max_length=100)

  class Meta:
    ordering = ['name']

  def __str__(self):
    return str(self.user)
