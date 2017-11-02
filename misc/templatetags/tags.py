from django import template
from django.core.urlresolvers import reverse

from django.utils.safestring import mark_safe
import re

from coffee import models
from misc import mylog
from misc.models import ObjectGrantedContextualized

register = template.Library()


@register.simple_tag
def active(request, pattern):
    if str(pattern) == str(request.path):
        return 'active'
    if str(reverse(pattern)) == str(request.path):
        return 'active'
    return ''


@register.filter(name='trim')
def trim(string, trim_length, first=None, second=None, third=None):
    return models.trim(string, trim_size_min=trim_length)


@register.filter(name='linebreaksp')
def linebreaksp(string):
    return mark_safe("<p>" + string.replace("\n", "</p><p>") + "</p>")


@register.filter(name='hrefmaker')
def hrefmaker(string):
    # return mark_safe(string)
    return mark_safe(
        re.sub(r"\[([^]]*)\]", r'<a href="\1" target="_blank"><span class="glyphicon glyphicon-new-window"></span></a>',
               string))


@register.filter(name='url_to_href')
def url_to_href(string):
    return mark_safe(re.sub(r"^(.*[/])([^/]+[/]?)$", r'<a href="\1\2" target="_blank">\2</a>',string))


@register.filter(name='fakehrefmaker')
def fakehrefmaker(string):
    # return mark_safe(string)
    return mark_safe(re.sub(r"\[([^]]*)\]", r'<i class="gnw"></i>', string))


@register.filter(name='p_justify')
def p_justify(string):
    return mark_safe(string.replace("<p>", "<p  align=\"justify\">"))


@register.filter(name='escape_semi_coma')
def escape_semi_coma(str_org):
    return str(str_org).encode('utf-8').strip().replace("&nbsp;", " ").replace("; ", ", ").replace(";", ", ")


@register.filter(name='is_kind')
def is_kind(things, kind):
    return things.filter(kind=kind)


# @register.simple_tag
# def strlen(request, pattern):
#     if str(pattern) == str(request.path):
#         return 'active'
#     if str(reverse(pattern)) == str(request.path):
#         return 'active'
#     return ''


def contextualized(request, o):
    # if o.__class__ == UseCase:
    #     return UseCaseContextualized(uc=o, user=request.user)
    # if o.__class__ == Requirement:
    #     return RequirementContextualized(req=o, user=request.user)
    return ObjectGrantedContextualized(o=o, user=request.user)


@register.filter(name='can_see_simple_html')
def can_see_simple_html(request, o):
    perm = o.__module__[0: o.__module__.index('.') + 1] + 'can_see_simple_html_' + o.__class__.__name__.lower()
    perm = o.__module__[0: o.__module__.index('.') + 1] + 'can_see_simple_html'
    mylog.debug(request.user.user_permissions.all())
    # return can_see(request, o) and \
    return request.user.has_perm(perm)


@register.filter(name='can_see')
def can_see(request, o):
    return contextualized(request, o).can_see()


@register.filter(name='can_edit')
def can_edit(request, o):
    return contextualized(request, o).can_edit()


@register.filter(name='can_delete')
def can_delete(request, o):
    return contextualized(request, o).can_delete()
