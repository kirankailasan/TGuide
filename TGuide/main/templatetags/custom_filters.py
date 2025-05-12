from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Returns dictionary value for a given key."""
    return d.get(key, "")
