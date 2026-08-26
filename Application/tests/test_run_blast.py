import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from Application import views
from .base import StaticFixturesMixin


class IsFileNotEmptyTests(TestCase):
    def test_empty_file_is_false(self):
        with tempfile.NamedTemporaryFile() as f:
            self.assertFalse(views.is_file_not_empty(f.name))

    def test_nonempty_file_is_true(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'data')
            f.flush()
            self.assertTrue(views.is_file_not_empty(f.name))


class CreateHyperlinkTests(TestCase):
    def test_builds_link_to_results_from_ids(self):
        html = views.create_hyperlink('TCONS_TEST1_Human')
        expected_url = reverse('Application:results-from-ids', args=('TCONS_TEST1', 'Human'))
        self.assertIn(f'href="{expected_url}"', str(html))
        self.assertIn('TCONS_TEST1_Human', str(html))


class RunBlastMockedTests(StaticFixturesMixin, TestCase):
    def test_concatenates_only_the_selected_organisms_fasta_files(self):
        calls = []

        def fake_run(cmd, **kwargs):
            calls.append(cmd)
            return mock.Mock(returncode=0)

        with mock.patch('Application.views.subprocess.run', side_effect=fake_run), \
             mock.patch('Application.views.is_file_not_empty', return_value=False):
            result = views.run_blast('/dev/null', ['Human', 'Gorilla'])

        self.assertEqual(result, 'No hit for the given query!')
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], 'makeblastdb')
        self.assertEqual(calls[1][0], 'blastn')

        combined_fasta = (self.static_dir / 'Tmp' / 'GenomePrepInput.fasta').read_text()
        self.assertIn('TCONS_TEST1_Human', combined_fasta)
        self.assertIn('TCONS_TEST1_Gorilla', combined_fasta)
        self.assertNotIn('TCONS_TEST1_Chimp', combined_fasta)

    def test_makeblastdb_failure_propagates(self):
        with mock.patch('Application.views.subprocess.run', side_effect=subprocess.CalledProcessError(1, 'makeblastdb')):
            with self.assertRaises(subprocess.CalledProcessError):
                views.run_blast('/dev/null', ['Human'])

    def test_formats_hits_as_html_table_with_working_links(self):
        blast_output_path = self.static_dir / 'Tmp' / 'BLAST_output.txt'

        def fake_run(cmd, **kwargs):
            if cmd[0] == 'blastn':
                blast_output_path.write_text(
                    'query1\tTCONS_TEST1_Human\t100.000\t60\t0\t0\t1\t60\t1\t60\t0.0\t100\n'
                )
            return mock.Mock(returncode=0)

        with mock.patch('Application.views.subprocess.run', side_effect=fake_run):
            result = views.run_blast('/dev/null', ['Human'])

        expected_url = reverse('Application:results-from-ids', args=('TCONS_TEST1', 'Human'))
        self.assertIn(f'href="{expected_url}"', str(result))
        self.assertIn('TCONS_TEST1_Human', str(result))


@unittest.skipUnless(
    shutil.which('makeblastdb') and shutil.which('blastn'),
    'BLAST is not installed on PATH in this environment',
)
class RunBlastRealIntegrationTest(StaticFixturesMixin, TestCase):
    """Exercises the actual conda-installed BLAST binaries end to end, when available."""

    def test_real_blast_run_finds_exact_match(self):
        human_sequence = 'GATTACACCGTAAGGCTTAGCCATGGACCTTAACGGTTCCAGGTAAGCTGATCCAGGTTA'
        query_path = self.static_dir / 'query.fasta'
        query_path.write_text(f'>query\n{human_sequence}\n')

        result = views.run_blast(str(query_path), ['Human'])

        self.assertIn('TCONS_TEST1_Human', str(result))
