from unittest import mock

from django.test import TestCase
from django.urls import reverse

from .base import StaticFixturesMixin
from .factories import make_general_info


class ResultsFromIdsViewTests(StaticFixturesMixin, TestCase):
    def test_known_id_renders_results_page(self):
        make_general_info('TCONS_TEST1', 'Human', Orthologs_Human='TCONS_TEST1')
        url = reverse('Application:results-from-ids', args=('TCONS_TEST1', 'Human'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')
        self.assertEqual(response.context['browser_org'], 'hg19')

    def test_id_lookup_is_case_insensitive(self):
        make_general_info('TCONS_TEST1', 'Human', Orthologs_Human='TCONS_TEST1')
        url = reverse('Application:results-from-ids', args=('tcons_test1', 'human'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')

    def test_unknown_id_renders_warning_page(self):
        url = reverse('Application:results-from-ids', args=('NOPE', 'Human'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'warnings.html')


class ExploreViewTests(StaticFixturesMixin, TestCase):
    def test_get_renders_all_four_search_forms(self):
        response = self.client.get(reverse('Application:explore-db'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explore.html')

    def test_id_search_with_known_id_renders_results(self):
        make_general_info('TCONS_TEST1', 'Human', Orthologs_Human='TCONS_TEST1')
        response = self.client.post(reverse('Application:explore-db'), {
            'ID': 'TCONS_TEST1', 'Organism': 'Human', 'Idss': 'Search',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')

    def test_id_search_with_unknown_id_renders_warning(self):
        response = self.client.post(reverse('Application:explore-db'), {
            'ID': 'NOPE', 'Organism': 'Human', 'Idss': 'Search',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'warnings.html')

    def test_id_search_missing_fields_redirects_with_message(self):
        response = self.client.post(reverse('Application:explore-db'), {
            'ID': '', 'Organism': '', 'Idss': 'Search',
        })
        self.assertEqual(response.status_code, 302)

    def test_location_search_exact_match_renders_results(self):
        make_general_info('TCONS_LOC1', 'Human', Chr='chr1', Start=100, End=200, Orthologs_Human='TCONS_LOC1')
        response = self.client.post(reverse('Application:explore-db'), {
            'Location': 'chr1:100-200', 'Organism': 'Human', 'Overlap': '', 'Locations': 'Search',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')

    def test_location_search_with_overlap_widens_match(self):
        make_general_info('TCONS_LOC2', 'Human', Chr='chr2', Start=500, End=600, Orthologs_Human='TCONS_LOC2')
        response = self.client.post(reverse('Application:explore-db'), {
            'Location': 'chr2:505-595', 'Organism': 'Human', 'Overlap': '10', 'Locations': 'Search',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')

    def test_location_search_missing_fields_redirects_with_message(self):
        response = self.client.post(reverse('Application:explore-db'), {
            'Location': '', 'Organism': '', 'Locations': 'Search',
        })
        self.assertEqual(response.status_code, 302)

    def test_multi_id_search_splits_on_comma_newline_and_whitespace(self):
        response = self.client.post(reverse('Application:explore-db'), {
            'MultiIDs': 'TCONS_1, TCONS_2\nTCONS_3 TCONS_4', 'Organism': 'Human', 'MultiIds': 'Search',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')
        self.assertEqual(
            response.context['MultiIds_results'],
            ['TCONS_1', 'TCONS_2', 'TCONS_3', 'TCONS_4'],
        )

    def test_multi_id_search_missing_fields_redirects_with_message(self):
        response = self.client.post(reverse('Application:explore-db'), {
            'MultiIDs': '', 'Organism': '', 'MultiIds': 'Search',
        })
        self.assertEqual(response.status_code, 302)

    def test_sequence_search_renders_blast_results(self):
        with mock.patch('Application.views.run_blast', return_value='mocked blast table') as mocked_run_blast:
            response = self.client.post(reverse('Application:explore-db'), {
                'Sequence': '>query\nATCG', 'Organism_db': ['Human'], 'Sequences': 'Search',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')
        self.assertIn('mocked blast table', response.content.decode())
        mocked_run_blast.assert_called_once()
        self.assertEqual(mocked_run_blast.call_args.args[1], ['Human'])
