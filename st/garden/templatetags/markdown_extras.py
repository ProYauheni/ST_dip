from django import template
from django.template.defaultfilters import stringfilter
import markdown as md
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
@stringfilter
def markdown(value):
    html = md.markdown(value, extensions=['extra', 'nl2br', 'sane_lists'])
    return mark_safe(html)
