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
nbsp.is_safe = True

@register.filter
def truncate(value,arg):
  try:
    if len(value) > arg-3:
      return value[:arg-3] + '...'
    else:
      return value
  except:
    return ""
