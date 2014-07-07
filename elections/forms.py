from django.forms import ModelForm
from webapps.elections.models import *


"""

-- Jacob Menick
-- April 2014

Forms for the elections app. 

Except damn, though. You wana just do these in javascript? 

"""

class ElectionForm(ModelForm):
    class Meta:
        model = Election
        fields = ['position', 'startDateTime', 'endDateTime', 'numSeats']
        # Need to figure out how to allow administrator to put in the election's candidates. 

    
    
