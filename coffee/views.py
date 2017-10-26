# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from coffee.models import Order, ContentOrder
from .models import Choice, Question, Coffee
from .forms import OrderForm

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


def list_coffee(request):
    context = {
        'objects': Coffee.objects.filter(for_sale=True),
    }
    return render(request, 'coffee/index.html', context)


def manage_coffee(request):
    context = {
        'objects': Coffee.objects.all(),
    }
    return render(request, 'coffee/sync_coffee.html', context)


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


def list_order(request):
    context = {
        'objects': Order.objects.filter(archived=False),
    }
    return render(request, 'coffee/list_order.html', context)


def list_content_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            coffee = form['coffee'].value()
            content_order = form.save(commit=False)
            coffee_content_order = ContentOrder.objects.filter(coffee=coffee)
            if coffee_content_order:
                content_order.id = coffee_content_order.values('id')
            content_order.user = request.user
            content_order.order = order
            content_order.save()
            content_order_to_remove = ContentOrder.objects.filter(quantity=0)
            if content_order_to_remove:
                content_order_to_remove.delete()
    else:
        form = OrderForm()

    context = {
        'objects': ContentOrder.objects.all(),
        'form': form,
    }
    return render(request, 'coffee/detail.html', context)


def remove_coffee_of_your_content_order(request, content_id):
    content_order = ContentOrder.objects.get(id=content_id)
    content_order.delete()
    return render(request, 'coffee/detail.html')
