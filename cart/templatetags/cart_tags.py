from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    if value is None:
        value = 0
    return float(value) * arg 