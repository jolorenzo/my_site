# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.contrib.auth import logout, authenticate, login
from django.db import models
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Coffee, Order, ContentOrder, Question, Choice
from .forms import OrderForm, SignUpForm

import urllib2
from bs4 import BeautifulSoup as Soup


class IndexView(generic.ListView):
    template_name = 'coffee/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'coffee/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'coffee/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'coffee/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('coffee:results', args=(question.id,)))


@login_required
def list_coffee(request):
    context = {
        'objects': Coffee.objects.filter(for_sale=True),
    }
    return render(request, 'coffee/index.html', context)


@login_required
def manage_coffee(request):
    context = {
        'objects': Coffee.objects.all(),
    }
    return render(request, 'coffee/sync_coffee.html', context)


@login_required
def get_nespresso_product_price(coffee_tittle):
    name_modified = coffee_tittle.lower().replace(" ", "-")
    url_coffee = "https://www.nespresso.com/pro/fr/fr/product/" + name_modified + "-boite-capsule-cafe"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(url_coffee, headers=hdr)
    page = urllib2.urlopen(req)
    soup = Soup(page, 'html.parser')

    for span in soup.find_all('span', class_="nes_list-price"):
        for coffee_price in span.find_all('span'):
            coffee_price_modified = re.sub(r'[^0-9,]*', '', coffee_price.text)
            coffee_price_float = re.sub(r',', '.', coffee_price_modified)

            return coffee_price_float


@login_required
def sync_coffee(*args, **kwargs):
    old_coffees = Coffee.objects
    old_ids = [o[0] for o in old_coffees.values_list()]
    idle = []
    added = []
    removed = []
    all = []
    print old_ids

    site = "https://www.nespresso.com/pro/fr/fr/pages/commercial-coffee-capsule-range"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(site, headers=hdr)
    page = urllib2.urlopen(req)
    soup = Soup(page, 'html.parser')

    for ultag_grid in soup.find_all('ul', class_="grid clearfix desktop"):
        for litag_grid in ultag_grid.find_all('li'):
            for coffee_title in litag_grid.find_all(class_="title"):
                obj, created = Coffee.objects.get_or_create(name=coffee_title.text, defaults={'price': 0})
                if created:
                    added.append(coffee_title.text)
                    print("Le café ", coffee_title.text, " n'existait pas")
                else:
                    idle.append(obj.name)
                obj.name = coffee_title.text
                obj.price = get_nespresso_product_price(coffee_title.text)
                obj.save()

    # old_coffees = old_coffees.filter(pk__in=old_ids)
    # removed = [o[0] for o in old_coffees.values_list('name')]
    # old_coffees.delete()
    all = [o[0] for o in Coffee.objects.values_list('name')]
    # return JsonResponse(
    #     {
    #         "added": {
    #             "count": len(added),
    #             "names": added,
    #         },
    #         "idle": {
    #             "count": len(idle),
    #             "names": idle
    #         },
    #         "removed": {
    #             "count": len(removed),
    #             "names": removed,
    #         },
    #         "all": {
    #             "count": len(all),
    #             "names": all,
    #         }
    #     }
    # )


@login_required
def list_order(request):
    context = {
        'objects': Order.objects.filter(archived=False),
    }
    return render(request, 'coffee/list_order.html', context)


@login_required
def manage_order(request):
    context = {
        'objects': Order.objects.all(),
    }
    return render(request, 'coffee/list_order.html', context)


@login_required
def list_content_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order_by_users = {}

    qs = ContentOrder.objects \
        .filter(order=order, ) \
        .annotate(price=F('coffee__price'), ) \
        .extra(select={'co_price': 'price * quantity'}) \
        .exclude(user=request.user)

    for co in qs:
        try:
            user_dict = order_by_users[co.user.username]
        except KeyError:
            user_dict = {
                'coffee': {},
                'total_paid': 0,
                'number_coffee': 0,
            }
            order_by_users[co.user.username] = user_dict
        user_dict['coffee'].update({co.coffee.name: co.quantity})
        user_dict['total_paid'] += co.co_price
        user_dict['number_coffee'] = len(user_dict['coffee'])

        # print co

    # print order_by_users
    # print order_by_coffee

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            coffee = form['coffee'].value()
            content_order = form.save(commit=False)
            content_order.user = request.user
            ContentOrder.objects.filter(coffee=coffee, user=content_order.user, ).delete()
            if content_order.quantity > 0:
                content_order.save()
    else:
        form = OrderForm(initial={
            'user': request.user,
            'order': order,
        })

    context = {
        'order_by_users': order_by_users,
        'objects': ContentOrder.objects.filter(order=order, user=request.user),
        'form': form,
    }
    return render(request, 'coffee/detail.html', context)


@login_required
def remove_coffee_of_your_content_order(request, content_id):
    content_order = get_object_or_404(ContentOrder, id=content_id)
    if request.user != content_order.user or not content_order.order.open:
        return HttpResponseForbidden()
    order_id = content_order.order.id
    content_order.delete()
    return redirect(reverse('coffee:list_content_order', args=[order_id]))


@login_required
@permission_required('coffee.change_order')
def results_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # users = get_user_model().objects.filter(contentorder__order_id=order_id).distinct().order_by('username')
    total_paid = ContentOrder.objects.filter(order=order, ).aggregate(
        total=Sum(
            F('coffee__price') * F('quantity'),
            output_field=models.FloatField()
        )
    )

    order_by_users = ContentOrder.objects.filter(order=order, ).values('user__username').order_by(
        'user__username').annotate(
        total=Sum(
            F('coffee__price') * F('quantity'),
            output_field=models.FloatField()
        )
    )

    order_by_coffee = ContentOrder.objects.filter(order=order, ).values('coffee__name').order_by(
        'coffee__name').annotate(
        total_quantity=Sum(
            F('quantity'),
            output_field=models.IntegerField()
        ),
        total_price=Sum(
            F('coffee__price') * F('quantity'),
            output_field=models.FloatField()
        )
    )
    # print order_by_coffee
    context = {
        'order_id': order_id,
        'order_by_users': order_by_users,
        'order_by_coffee': order_by_coffee,
        'total_paid': total_paid,
        'objects': ContentOrder.objects.filter(order=order, ),
    }
    return render(request, 'coffee/results.html', context)


class User_Authentication_Views(object):
    # def registration_view(self, request):
    #    #do_stuff with form and save into your model or whatever you need.

    def logout_view(self, request):
        logout(request)
        return redirect('/accounts/login/')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user.is_active = False
            user.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
