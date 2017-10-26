# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from coffee.models import Order, ContentOrder
from coffee.views import sync_coffee
from .models import Choice, Question, Coffee


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']


class CoffeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'was_for_sale')
    list_filter = ['price']
    search_fields = ['name']

    actions = [
        sync_coffee,
    ]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Coffee, CoffeeAdmin)
admin.site.register(Order)
admin.site.register(ContentOrder)
