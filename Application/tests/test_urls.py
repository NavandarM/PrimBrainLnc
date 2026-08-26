from django.test import SimpleTestCase
from django.urls import resolve, reverse


class ReverseUrlTests(SimpleTestCase):
    def test_index_resolves(self):
        self.assertEqual(reverse('index'), '/')

    def test_application_named_urls_resolve(self):
        names = ['home', 'search', 'downloads', 'contact', 'statistics', 'user-area', 'explore-db', 'faqs']
        for name in names:
            with self.subTest(name=name):
                url = reverse(f'Application:{name}')
                self.assertTrue(resolve(url))

    def test_results_from_ids_url_includes_both_args(self):
        url = reverse('Application:results-from-ids', args=('TCONS_1', 'Human'))
        self.assertIn('TCONS_1', url)
        self.assertIn('Human', url)
        match = resolve(url)
        self.assertEqual(match.kwargs, {'lncIDs': 'TCONS_1', 'OrgS': 'Human'})
