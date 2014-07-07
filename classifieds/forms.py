from django import forms

"""

-- Jacob Menick
-- January 2014

The main thing to note here is that we put categories here rather than in models to allow for flexibility.
Future webmasters may decide they want to rejig the post categories, and I don't wanna make y'all fuck with that in mysql. 

"""

category_choices= (
    ('Trade','Trade'), 
    ('Missed Connections', 'Missed Connections'),
    ('Lost & Found', 'Lost & Found'), 
    ('Ramblings', 'Ramblings'), 
    ('Happenin', 'Things happenin'),
)

class AdForm(forms.Form):
    title = forms.CharField(max_length = 50)
    text = forms.CharField(max_length = 2000, widget=forms.Textarea) #used Textarea widget so that the ad text input is a block rather than a line. 
    category = forms.ChoiceField(choices=category_choices)
    email = forms.EmailField(required = False)
    phone = forms.CharField(max_length = 10, required = False)
    
class CommentForm(forms.Form):
    text = forms.CharField(max_length = 1000, widget=forms.Textarea)

class MessageForm(forms.Form):
    """Currently named 'message', because maybe one day it could be used for a native messaging app.  Right now, it's being used to facilitate requests for contact information on Missed Connections."""

    body = forms.CharField(max_length = 300, required = False, widget=forms.Textarea)
