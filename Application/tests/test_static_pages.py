from django.test import TestCase
from django.urls import reverse

from Application.models import UserOpinion
from .factories import make_general_info


class StaticPageViewTests(TestCase):
    def test_pages_return_200(self):
        names = ['home', 'search', 'downloads', 'contact', 'statistics', 'faqs']
        for name in names:
            with self.subTest(name=name):
                response = self.client.get(reverse(f'Application:{name}'))
                self.assertEqual(response.status_code, 200)

    def test_index_root_returns_200_with_welcome_context(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['insert_content'], 'Welcome to PrimBrainLnc')

    def test_search_page_lists_entries(self):
        make_general_info('TCONS_S1', 'Human')
        response = self.client.get(reverse('Application:search'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('TCONS_S1_Human', response.content.decode())


class UserAreaViewTests(TestCase):
    def _valid_data(self, **overrides):
        data = {
            'Name': 'Jane Doe', 'Email': 'jane@example.com', 'Phone': '',
            'Organization': '', 'Description': 'Great tool!', 'botcatcher': '',
        }
        data.update(overrides)
        return data

    def test_get_renders_form(self):
        response = self.client.get(reverse('Application:user-area'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_input.html')

    def test_valid_post_creates_user_opinion_and_redirects(self):
        response = self.client.post(reverse('Application:user-area'), self._valid_data())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserOpinion.objects.filter(Name='Jane Doe').exists())

    def test_honeypot_filled_rejects_submission(self):
        response = self.client.post(reverse('Application:user-area'), self._valid_data(botcatcher='spam'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserOpinion.objects.filter(Email='jane@example.com').exists())
