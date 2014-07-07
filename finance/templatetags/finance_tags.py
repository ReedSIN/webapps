from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter
@stringfilter
def nbsp(v):
  if v == "":
    return "&nbsp;"
  else:
    return v

