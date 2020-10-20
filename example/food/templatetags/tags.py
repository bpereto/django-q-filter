from django import template
register = template.Library()

@register.filter(name='getattr')
def attributeLookup(the_object, attribute_name):
   # Try to fetch from the object, and if it's not found return None.
   return getattr(the_object, attribute_name, None)
