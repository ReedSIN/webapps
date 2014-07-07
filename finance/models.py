from django.db import models
from webapps.generic.models import * 

class Budget(models.Model):
  organization = models.ForeignKey(Organization)
  description = models.TextField()
  response = models.TextField()
  
  requested = models.DecimalField(max_digits = 8, decimal_places = 2)
  allocated = models.DecimalField(max_digits = 8, decimal_places = 2)
  claimed = models.DecimalField(max_digits = 8, decimal_places = 2)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)

  finalized = models.IntegerField(default = 0)
  approved = models.IntegerField(default = 0)

  def is_finalized(self):
    return self.finalized == 1
  
  def is_approved(self):
    return self.approved == 1

class BudgetItem(models.Model):
  budget = models.ForeignKey(Budget)
  
  name = models.CharField(max_length = 50)
  description = models.TextField()
  response = models.TextField()
  
  requested = models.DecimalField(max_digits = 8, decimal_places = 2)
  allocated = models.DecimalField(max_digits = 8, decimal_places = 2)
  claimed = models.DecimalField(max_digits = 8, decimal_places = 2)
  
  created_on = models.DateTimeField(auto_now_add = True)
  modified_on = models.DateTimeField(auto_now = True)
