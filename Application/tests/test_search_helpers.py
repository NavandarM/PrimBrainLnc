from django.test import TestCase

from Application import views
from Application.models import GeneralInfo
from .base import StaticFixturesMixin
from .factories import make_general_info


class QueryProcessorTests(TestCase):
    def test_returns_split_orthologs_and_id_for_matching_entry(self):
        make_general_info(
            'TCONS_H1', 'Human',
            Orthologs_Human='TCONS_H1', Orthologs_Chimp='TCONS_C1;TCONS_C2',
            Orthologs_Gorilla='nan', Orthologs_Gibbon='nan',
        )
        qs = GeneralInfo.objects.filter(LncRNA_id='TCONS_H1')
        result = views.query_processor(qs, 'Human')
        self.assertEqual(result, [['TCONS_H1'], ['TCONS_C1', 'TCONS_C2'], ['nan'], ['nan'], 'TCONS_H1'])

    def test_strips_spaces_from_ortholog_lists(self):
        make_general_info('TCONS_H2', 'Human', Orthologs_Chimp='TCONS_C1; TCONS_C2 ; TCONS_C3')
        qs = GeneralInfo.objects.filter(LncRNA_id='TCONS_H2')
        result = views.query_processor(qs, 'Human')
        self.assertEqual(result[1], ['TCONS_C1', 'TCONS_C2', 'TCONS_C3'])

    def test_returns_warning_string_for_empty_queryset(self):
        qs = GeneralInfo.objects.filter(LncRNA_id='does-not-exist')
        result = views.query_processor(qs, 'Human')
        self.assertIsInstance(result, str)
        self.assertIn('Human', result)

    def test_uses_first_matching_row_when_multiple_match(self):
        # Two rows sharing the same LncRNA_id but distinct primary keys (LncRNA_uid).
        make_general_info('TCONS_DUP', 'Human', Orthologs_Human='FIRST')
        make_general_info('TCONS_DUP', 'HumanDup', Orthologs_Human='SECOND')
        qs = GeneralInfo.objects.filter(LncRNA_id='TCONS_DUP').order_by('LncRNA_uid')
        result = views.query_processor(qs, 'Human')
        self.assertEqual(result[0], ['FIRST'])


class DataPreparationTests(StaticFixturesMixin, TestCase):
    def test_known_organism_and_id_returns_plot_html(self):
        result = views.Data_preparation('Human', 'TCONS_TEST1')
        self.assertIn('plotly', result.lower())

    def test_unknown_organism_returns_message(self):
        result = views.Data_preparation('Martian', 'TCONS_TEST1')
        self.assertEqual(result, 'Expression is Not available!')

    def test_unknown_id_returns_message_instead_of_crashing(self):
        result = views.Data_preparation('Human', 'DOES_NOT_EXIST')
        self.assertEqual(result, 'Expression is Not available for DOES_NOT_EXIST')

    def test_expression_file_is_parsed_only_once_per_process(self):
        views.Data_preparation('Human', 'TCONS_TEST1')
        info_after_first = views._load_expression_data.cache_info()
        views.Data_preparation('Human', 'TCONS_TEST2')
        info_after_second = views._load_expression_data.cache_info()

        self.assertEqual(info_after_second.misses, info_after_first.misses)
        self.assertEqual(info_after_second.hits, info_after_first.hits + 1)
