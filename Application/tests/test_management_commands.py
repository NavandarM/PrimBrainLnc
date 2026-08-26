from unittest import mock

import pandas as pd
from django.core.management import call_command
from django.test import TestCase

from Application.models import GeneralInfo

ROW = {
    'LncRNA_Id': 'TCONS_CMD1', 'LncRNA_Id1': 'TCONS_CMD1_Human', 'Chr': 'chr1', 'Start': 1, 'End': 100,
    'Strand': '+', 'TSS': '1', 'Promoter_start': '0', 'Promoter_end': '1', 'Length': '100', 'Exon_number': '1',
    'Class': 'lincRNA', 'Direction': 'sense', 'Location': 'intergenic', 'Status_of_Expression': 'Expressed',
    'Orthologs_status': '1:1', 'Overlap_gene_id': '', 'Overlap_ref_id': '', 'Class_code': 'u', 'Organism': 'Human',
    'Orthologs_Human': 'TCONS_CMD1', 'Orthologs_Chimp': 'nan', 'Orthologs_Gorilla': 'nan', 'Orthologs_Gibbon': 'nan',
    'DEGRegion_human': '', 'DEGRegion_chimp': '',
}


class UpdateModelsCommandTests(TestCase):
    def test_bulk_creates_records_from_csv(self):
        df = pd.DataFrame([ROW])
        with mock.patch('Application.management.commands.update_models.pd.read_csv', return_value=df):
            call_command('update_models')

        self.assertEqual(GeneralInfo.objects.count(), 1)
        record = GeneralInfo.objects.get(LncRNA_uid='TCONS_CMD1_Human')
        self.assertEqual(record.LncRNA_id, 'TCONS_CMD1')
        self.assertEqual(record.Chr, 'chr1')
        self.assertEqual(record.Organism, 'Human')
        self.assertEqual(record.Tr_Class, 'lincRNA')
        self.assertEqual(record.DEG_Human, '')

    def test_handles_multiple_rows(self):
        second_row = dict(ROW, LncRNA_Id='TCONS_CMD2', LncRNA_Id1='TCONS_CMD2_Chimp', Organism='Chimp')
        df = pd.DataFrame([ROW, second_row])
        with mock.patch('Application.management.commands.update_models.pd.read_csv', return_value=df):
            call_command('update_models')

        self.assertEqual(GeneralInfo.objects.count(), 2)
