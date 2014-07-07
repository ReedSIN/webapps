from django import template

register = template.Library()

@register.filter
def nbsp(v):
  if v == "":
    return "&nbsp;"
  else:
    return v
