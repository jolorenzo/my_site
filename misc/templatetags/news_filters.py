from django import template
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from coffee.models import News
from misc.models import get_public_group

register = template.Library()


def get_group_filter(user):
    if user.is_superuser:
        q = Q()
    elif user.is_authenticated():
        q = Q(target_groups__in=user.groups.all())
    else:
        q = Q(target_groups__in=[get_public_group().pk, ])
    return q


@register.filter(name='has_news')
def has_news(user):
    return user is not None and get_news(user).exists()


@register.filter(name='has_many_news')
def has_many_news(user):
    return user is not None and get_news(user).count() > 1


@register.filter(name='get_news')
def get_news(user):
    return News.objects_active().filter(get_group_filter(user))


@register.filter(name='get_news_with_count_range')
def get_news_with_count_range(user):
    i = 0
    for n in News.objects_active().filter(get_group_filter(user)):
        yield (i, n)
        i += 1


@register.filter(name='get_news_count_range')
def get_news_count_range(user):
    return range(0, News.objects_active().filter(get_group_filter(user)).count())


@register.filter(name='news_as_href')
def news_as_href(news):
    return format_html(
        '<a href="%s#news-%i">%s</a>' %
        (
            reverse('misc:news_list'),
            news.pk,
            news_as_span(news),
        )
    )


@register.filter(name='news_as_span')
def news_as_span(news):
    if news.title:
        return format_html(
            '<span class="text-%s"><b>%s %s</b>%s</span>' % (news.severity_str(), news.title, _(':'), news.body[:80]))
    else:
        return format_html('<span class="text-%s">%s</span>' % (news.severity_str(), news.body))


@register.filter(name='news_as_div')
def news_as_div(news):
    # if news.title:
    return format_html(
        '<div id="news-%(pk)i" class="news alert alert-dismissable alert-%(severity_str)s fade in">'
        '<a href="#" class="close" data-dismiss="alert" aria-label="close">&#215;</a>'
        '<a '
        'href="%(news_list)s#news-%(pk)i"'
        'data-toggle="popover"'
        'data-class="popover-%(severity_str)s"'
        'data-placement="bottom"'
        'data-content=""'
        # 'data-trigger="click"'
        'class="text-default"'
        'url="%(included)s?included=True"'
        '>'
        '%(as_html)s'
        '</a>'
        '</div>' %
        {
            'pk': news.pk,
            'severity_str': news.severity_str(),
            'news_list': reverse('misc:news_list'),
            'included': reverse('misc:news', args=[news.pk]),
            'as_html': news.as_html(),
        }
    )