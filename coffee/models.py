# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query_utils import Q
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.contrib.auth.models import Group

from mysite import settings


@python_2_unicode_compatible  # only if you need to support Python 2
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


@python_2_unicode_compatible  # only if you need to support Python 2
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def get_nespresso_product_url(self):
        choice_text_modified = self.choice_text.lower().replace(" ", "-")

        url_choice = "https://www.nespresso.com/pro/fr/fr/product/" + choice_text_modified + "-boite-capsule-cafe"
        return url_choice

    def __str__(self):
        return self.choice_text


@python_2_unicode_compatible  # only if you need to support Python 2
class Coffee(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField(default=0)
    for_sale = models.BooleanField(default=True)

    def was_for_sale(self):
        now = True
        return now == self.for_sale

    was_for_sale.admin_order_field = 'for_sale'
    was_for_sale.boolean = True
    was_for_sale.short_description = 'For sale?'

    def get_nespresso_product_url(self):
        name_modified = self.name.lower().replace(" ", "-")

        url_coffee = "https://www.nespresso.com/pro/fr/fr/product/" + name_modified + "-boite-capsule-cafe"
        return url_coffee

    def get_price_per_box(self):
        capsule_by_box = 50
        price_per_box = (self.price * capsule_by_box)
        return price_per_box

    def __str__(self):
        return self.name


@python_2_unicode_compatible  # only if you need to support Python 2
class Order(models.Model):
    ordered_date = models.DateTimeField('date published')
    paid_price = models.FloatField(default=0)
    open = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def est_recent(self):
        """ Retourne True si l'order a été publié dans
            les 30 derniers jours """
        return (datetime.now() - self.ordered_date).days < 30 and self.ordered_date < datetime.now()

    def __str__(self):
        return "Order %i" % self.pk


@python_2_unicode_compatible  # only if you need to support Python 2
class ContentOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    order = models.ForeignKey(Order)
    coffee = models.ForeignKey(Coffee)
    quantity = models.PositiveIntegerField(default=1)

    def get_temp_price(self):
        temp_price = (self.coffee.price * self.quantity)
        return temp_price

    def quantity_is_correct(total_quantity):
        quantity_by_box = 50

        if [total_quantity % quantity_by_box == 0]:  # that line is added by me
            is_divisible = True
        else:
            is_divisible = False

        return is_divisible

    def __str__(self):
        return "%s wants %i %s" % (
            self.user,
            int(self.quantity),
            self.coffee,
        )


class News(models.Model):
    class Meta:
        ordering = ["-end", "-start", ]
        verbose_name = _('News')
        verbose_name_plural = pgettext_lazy('plural form', 'News')

    """ This class is made to store the date of the last firewall(s) update"""
    title = models.TextField(null=False, blank=True)
    body = models.TextField(null=False, blank=False)
    severity = models.IntegerField(
        _('severity'),
        choices=(
            (1, "success"),
            (2, "info"),
            (3, "warning"),
            (4, "danger"),
        ),
        default=2)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    target_groups = models.ManyToManyField(
        Group,
        verbose_name=_(u'target_groups'),
        blank=True,
    )

    def severity_str(self):
        return [c for i, c in News._meta.get_field('severity').choices if i == self.severity][0]

    def __unicode__(self):
        return "News(#%i) %s" % (
            self.pk,
            self.title if len(self.title + "") > 0 else self.body[:100],
        )

    def as_html(self):
        if self.title:
            return "<b>%(title)s %(two_dots)s</b>%(body)s" % {
                'title': self.title.encode('ascii', 'xmlcharrefreplace'),
                'two_dots': _(':'),
                'body': self.body.encode('ascii', 'xmlcharrefreplace'),
            }
        return self.body

    def clean(self):
        if self.start is not None and self.end is not None and self.end <= self.start:
            raise ValidationError(_('End datetime can only be after start datetime'))
        if self.start is None and self.end is None:
            raise ValidationError(_('Please either select a start datetime or an end datetime'))

    @staticmethod
    def objects_active():
        return News.objects. \
            filter(News.get_active_filter())

    @staticmethod
    def get_active_filter():
        return (Q(start=None) | Q(start__lt=timezone.now())) & (Q(end=None) | Q(end__gt=timezone.now()))
