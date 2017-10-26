# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone

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

    def __str__(self):
        return self.name


@python_2_unicode_compatible  # only if you need to support Python 2
class Order(models.Model):
    ordered_date = models.DateTimeField('date published')
    paid_price = models.FloatField(default=0)
    open = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return "Order %i" % self.pk


@python_2_unicode_compatible  # only if you need to support Python 2
class ContentOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    order = models.ForeignKey(Order)
    coffee = models.ForeignKey(Coffee)
    quantity = models.PositiveIntegerField(default=1)

    def get_temp_price(self):
        capsule_by_box = 50
        temp_price = (self.coffee.price * self.quantity * capsule_by_box)
        return temp_price

    def __str__(self):
        return "%s wants %i %s" % (
            self.user,
            int(self.quantity),
            self.coffee,
        )
