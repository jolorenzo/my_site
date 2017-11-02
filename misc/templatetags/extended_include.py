from django import template
from django.template.defaultfilters import stringfilter
from django.template.defaulttags import CommentNode
from django.template.loader_tags import do_include


register = template.Library()

@register.tag('include_if_exists')
def do_include_if_exists(parser, token):
    try:
        return do_include(parser, token)
    except template.TemplateDoesNotExist:
        return CommentNode()

@register.filter
@stringfilter
def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False

