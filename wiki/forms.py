from django import forms
from webapps.wiki.models import Wiki
"""
-- Brett Beutell
-- Jan/Feb 2014

"""

def getWikis():
    """ Spits out names of all Wiki Objects to be used as categories """
    """ If there are no wikis, we print a test category, 'HEHE'. """
    res = (('HEHE','HEHE'),)
    wikis = Wiki.objects.all()
    if wikis != []:
        for wiki in wikis:
            res = res + ((reswiki.name,reswiki.name),)
    return res
        
WIKI_CHOICES = getWikis() # Change if getWikis() doesn't work
                          # For now, they comprise the Article.wiki choice field
FLAG_TYPE_CHOICES = (
    ('Inaccurate','Inaccurate'),
    ('Confusing','Confusing'),
)

FLAG_STATUS_CHOICES = (
    ('Pending','Pending'),
    ('Resolved','Resolved'),
)

class WikiAppForm(forms.Form):
    # Define css classes for styling on the page
    # NOTE - these have to be called via .css_classes() method on a bound field of the form
    # e.g., form = WikiAppForm(...) 
    #       form['name'].css_classes()
    #
    error_css_class = 'error'
    required_css_class = 'required'

    # Now, the actual data
    name = forms.CharField(max_length = 50)
    is_moderated = forms.BooleanField(required=False)
    has_comments = forms.BooleanField(required=False)
    description = forms.CharField(max_length=10000,widget=forms.Textarea)
    justification = forms.CharField(max_length=10000,widget=forms.Textarea)
    email = forms.EmailField(required=False)

class WikiForm(forms.Form):
    error_css_class = 'error'
    required_css_class = 'required'

    name = forms.CharField(max_length = 50)
    is_moderated = forms.BooleanField(required=False)
    has_comments = forms.BooleanField(required=False)
    description = forms.CharField(max_length=10000,widget=forms.Textarea)

    addtl_moderator = forms.CharField(max_length = 100, required = False)

class ArticleForm(forms.Form):
    wiki_name = forms.ChoiceField(choices=WIKI_CHOICES) #Uses global variable at top
    title = forms.CharField(max_length = 50)
    is_featured = forms.BooleanField(required=False)
    is_private = forms.BooleanField(required=False)

class SectionForm(forms.Form):
    title = forms.CharField(max_length = 50)
    body = forms.CharField(max_length = 10000, widget=forms.Textarea)

class FlagForm(forms.Form):
    flag_type = forms.ChoiceField(choices=FLAG_TYPE_CHOICES) # Also uses global variable at top
    #flag_status = forms.ChoiceField(choices=FLAG_STATUS_CHOICES) # Again, global variable
    flag_description = forms.CharField(max_length = 1000, widget=forms.Textarea)

class CommentForm(forms.Form):
    text = forms.CharField(max_length = 4000, widget=forms.Textarea)
    
