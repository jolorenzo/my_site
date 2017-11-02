# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, RequestFactory, override_settings
from datetime import timedelta
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser

from coffee.models import *
from coffee.views import list_order


class CoffeeTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_dashboard_not_authenticated_user(self):
        url = reverse('coffee:list_order')
        response = self.client.get(url)
        self.assertTemplateNotUsed(response, 'coffee/list_order.html')
        self.failUnlessEqual(response.status_code, 302)

    def test_dashboard_authenticated_user(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('coffee:list_order'))
        self.failUnlessEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coffee/list_order.html')
        self.client.logout()

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get('coffee/list_order.html')

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.user

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = list_order(request)
        self.assertNotEquals(response.status_code, 200)


class OrderTests(TestCase):
    def test_est_recent_avec_futur_article(self):
        """
        Vérifie si la méthode est_recent d'un Article ne
        renvoie pas True si l'Article a sa date de publication
        dans le futur.
        """

        futur_order = Order(ordered_date=datetime.now() + timedelta(days=20))
        # Il n'y a pas besoin de remplir tous les champs, ni de sauvegarder
        self.assertEqual(futur_order.est_recent(), False)


class SearchFormTestCase(TestCase):
    def test_empty_get(self):
        response = self.client.get('/en/dev/search/', HTTP_HOST='docs.djangoproject.dev:8000')
        self.assertNotEquals(response.status_code, 200)


class MultiDomainTestCase(TestCase):
    @override_settings(ALLOWED_HOSTS=['otherserver'])
    def test_other_domain(self):
        response = self.client.get('http://otherserver/foo/bar/')


class LogInTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def test_login(self):
        # send login data
        response = self.client.post('/accounts/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_authenticated)
