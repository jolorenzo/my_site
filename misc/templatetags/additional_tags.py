from datetime import datetime
from django.utils.translation import ugettext_lazy as _

from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

import re

from misc import mylog, models
from misc.models import ObjectGrantedContextualized

register = template.Library()


@register.simple_tag
def active(request, pattern):
    try:
        if str(pattern) == str(request.path):
            return 'active'
        if str(reverse(pattern)) == str(request.path):
            return 'active'
        if request.method == 'GET' and 'next' in request.GET:
            if request.GET['next'] == str(pattern) or request.GET['next'] == str(reverse(pattern)):
                return 'next-active'
    except AttributeError as e:
        mylog.error(e, "can't work with request object and pattern %s " % pattern)
        raise
    return ''


@register.filter(name='is_url_to')
def is_url_to(request, pattern):
    try:
        if str(pattern) == str(request.path):
            return True
        if str(reverse(pattern)) == str(request.path):
            return True
    except AttributeError as e:
        mylog.error(e, "can't work with request object and pattern %s " % pattern)
        raise
    return False


@register.tag(name='captureas')
def do_captureas(parser, token):
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name.")
    nodelist = parser.parse(('endcaptureas',))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class CaptureasNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''


@register.filter
def div(value, arg):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        value = int(value)
        arg = int(arg)
        if arg: return value / arg
    except:
        pass
    return ''


@register.filter
def as_ul_inline(value, split_str):
    return as_ul_with_class(value, split_str, "list-inline list-inline-hover")


@register.filter
def as_csv(value, split_str):
    try:
        output = []
        for s in value.split(split_str):
            if len(s) > 0:
                output.append(s)
        return mark_safe(", ".join(output))
    except:
        pass
    return value


@register.filter
def as_p(value, split_str='\n'):
    output = []
    for s in value.split(split_str):
        if len(s) > 0:
            output.append('<p>%s</p>' % s)
    return mark_safe("\n".join(output))


@register.filter
def as_ul(value, split_str='\n'):
    return as_ul_with_class(value, split_str)


def as_ul_with_class(value, split_str, ul_classes=""):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        output = []
        output.append('<ul class="%s">' % ul_classes)
        for s in value.split(split_str):
            if len(s) > 0:
                output.append('<li>%s</li>' % s)
        output.append('</ul>')
        return mark_safe("\n".join(output))
    except Exception as e:
        mylog.error(e, )
    return value


@register.filter
def safe_id(value):
    return value \
        .replace(".", "_") \
        .replace(":", "_") \
        .replace("[", "_") \
        .replace("]", "_") \
        .replace(",", "_") \
        .replace("\"", "_")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='can_see_simple_html')
def can_see_simple_html(request, o):
    perm = o.__module__[0: o.__module__.index('.') + 1] + 'can_see_simple_html_' + o.__class__.__name__.lower()
    perm = o.__module__[0: o.__module__.index('.') + 1] + 'can_see_simple_html'
    mylog.debug(request.user.user_permissions.all())
    # return can_see(request, o) and \
    return request.user.has_perm(perm)


@register.filter(name='can_see')
def can_see(request, o):
    return ObjectGrantedContextualized(o=o, user=request.user).can_see()


@register.filter(name='can_edit')
def can_edit(request, o):
    return ObjectGrantedContextualized(o=o, user=request.user).can_edit()


@register.filter(name='can_delete')
def can_delete(request, o):
    return ObjectGrantedContextualized(o=o, user=request.user).can_delete()


@register.filter(name='trim')
def trim(string, trim_length, first=None, second=None, third=None):
    return models.trim(string, trim_size_min=trim_length, trim_size_max=int(trim_length * 1.05),
                                 trim_size_hard=int(trim_length * 1.1))


@register.filter(name='linebreaksp')
def linebreaksp(string):
    return mark_safe("<p>" + string.replace("\n", "</p><p>") + "</p>")


@register.filter(name='hrefmaker')
def hrefmaker(string):
    # return mark_safe(string)
    return mark_safe(
        re.sub(
            r"\[([^]]*)\]^\(",
            r'<a href="\1" target="_blank"><span class="glyphicon glyphicon-new-window"></span></a>',
            re.sub(
                r"\[([^]]*)\]\(([^\)]*)\)",
                r'<a href="\2" target="_blank">\1</a>',
                string
            )
        ))


@register.filter(name='fakehrefmaker')
def fakehrefmaker(string):
    # return mark_safe(string)
    return mark_safe(re.sub(r"\[([^]]*)\]", r'<i class="gnw"></i>', string))


@register.filter(name='p_justify')
def p_justify(string):
    return mark_safe(string.replace("<p>", "<p  align=\"justify\">"))


@register.filter(name='reduction2')
def reduction(string):
    if len(string) <= 10:
        return string
    reduced = string
    reduced = reduced.replace("france-bioinformatique.fr", "IFB")
    reduced = reduced.replace("an", "")
    reduced = reduced.replace("on", "")
    reduced = reduced.replace("in", "")
    reduced = reduced.replace("en", "")
    reduced = reduced.replace("que", "k")
    reduced = reduced.replace("a", "")
    reduced = reduced.replace("e", "")
    reduced = reduced.replace("i", "")
    reduced = reduced.replace("o", "")
    reduced = reduced.replace("u", "")
    reduced = reduced.replace("y", "")
    reduced = reduced.replace("h", "")
    reduced = reduced.replace("s", "")
    reduced = reduced.replace("tt", "t")
    reduced = reduced.replace("mm", "m")
    reduced = reduced.replace("nn", "n")
    return mark_safe('<span title="%s">%s</span>' % (string, reduced))


@register.filter(name='reduction3')
def reduction(string):
    if len(string) <= 10:
        return string
    big_parts = []
    for big_part in string.split("@"):
        parts = []
        for part in big_part.split("."):
            l = len(part)
            if 3 < l <= 5:
                part = part[0:2] + part[-1]
            elif 5 < l:
                part = part[0:2] + part[-2:]
            parts.append(part)
        big_parts.append(".".join(parts))
    reduced = "@".join(big_parts)

    return mark_safe('<span title="%s">%s</span>' % (string, reduced))


@register.filter(name='reduction')
def reduction(string):
    if len(string) <= 10:
        return string
    big_parts = []
    at_cut = string.split("@")
    l_at_cut = len(at_cut)
    for i in range(0, l_at_cut):
        parts = []
        big_part = at_cut[i]
        if i == l_at_cut - 1:
            end_part = "<span class=\"reduced\">" + big_part[big_part.rfind("."):] + "</span>"
            big_part = big_part[:big_part.rfind(".")]
        else:
            end_part = ""
        for part in big_part.split("."):
            l = len(part)
            if 3 < l <= 5:
                part = part[0:2] + "<span class=\"reduced\">" + part[2:] + "</span>"
            elif 5 < l:
                part = part[0:2] + "<span class=\"reduced\">" + part[2:-2] + "</span>" + part[-2:]
            parts.append(part)
        big_parts.append(".".join(parts) + end_part)
    reduced = "@".join(big_parts)

    return mark_safe(reduced)


@register.filter(name='date_reduction')
def date_reduction(d):
    if d is None:
        return d
    # if datetime.now().date
    # if d.
    day = "%s, "
    hour = "%s"
    if d.date() == datetime.today().date():
        return mark_safe("<span class=\"reduced\">%s, </span>%s" % (d.strftime("%b %d %Y"), d.strftime("%Hh%M")))
    else:
        return mark_safe("%s<span class=\"reduced\"> %s</span>" % (d.strftime("%b %d"), d.strftime("%Y, %Hh%M")))
        # return str(d)


@register.filter(name='uuid_reduction')
def uuid_reduction(uuid):
    try:
        # i = str(uuid).find("-")
        i = 4
        return mark_safe("%s<span class=\"reduced\">%s</span>" % (uuid[:i], uuid[i:]))
    except ValueError as e:
        mylog.error(e, )
        return uuid


# @register.tag
# def value_from_settings(parser, token):
#     try:
#         # split_contents() knows not to split quoted strings.
#         tag_name, var = token.split_contents()
#     except ValueError:
#         raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
#     return ValueFromSettings(getattr(settings, token.split_contents()[1], None))
#
#
# class ValueFromSettings(template.Node):
#     def __init__(self, var):
#         self.arg = template.Variable(var)
#
#     def render(self, context):
#         return settings.__getattr__(str(self.arg))

# @register.assignment_tag
# def define(val=None):
#     return getattr(settings, val, None)

@register.filter(name='admin_url')
def admin_url(object, arg):
    return reverse('admin:%s_%s_%s' % (type(object)._meta.app_label, type(object)._meta.model_name, arg),
                   args=(object.id,))


@register.filter(name='admin_url_change')
def admin_url_change(object):
    return admin_url(object, "change")


@register.filter(name='make_command_from_url')
def make_command_from_url(object):
    object = str(object)
    if object.startswith("ssh://"):
        pos = object.index("@")
        return "ssh -A -p 22 %s" % object[6:]
    if object.startswith("scp://"):
        pos = object.index("@")
        return "scp -P 22 ${%s} %s:${%s}" % (_('local_path_env_var_scp'), object[6:], _('distant_path_env_var_scp'),)
    return ""


@register.filter(name='url_as_sens_to_be_link')
def url_as_sens_to_be_link(object):
    object = str(object)
    if object.startswith("scp://"):
        return False
    return True


@register.filter(name='is_array')
def is_array(o):
    return isinstance(o, (list, tuple))


@register.filter(name='get_cookie_localized')
def get_cookie_localized(request, cookie_name):
    result = request.COOKIES.get(request.get_full_path().replace("/", "-").split("?")[0] + cookie_name, '')
    return result


@register.filter(name='get_cookie_localized_boolean')
def get_cookie_localized_boolean(request, cookie_name):
    return str(get_cookie_localized(request, cookie_name)) == "true"
