from django import template
register = template.Library()

@register.filter("hash")
def hash(h, key):
  return h[key]
