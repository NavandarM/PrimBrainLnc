from django.test import TestCase

from Application.models import GeneralInfo, UserOpinion
from .factories import make_general_info


class GeneralInfoModelTests(TestCase):
    def test_str_returns_lncrna_uid(self):
        entry = make_general_info('TCONS_M1', 'Human')
        self.assertEqual(str(entry), 'TCONS_M1_Human')

    def test_db_table_name(self):
        self.assertEqual(GeneralInfo._meta.db_table, 'General_Info')

    def test_lncrna_uid_is_primary_key(self):
        entry = make_general_info('TCONS_M2', 'Chimp')
        self.assertEqual(GeneralInfo._meta.pk.name, 'LncRNA_uid')
        self.assertEqual(entry.pk, 'TCONS_M2_Chimp')


class UserOpinionModelTests(TestCase):
    def test_str_returns_name(self):
        opinion = UserOpinion.objects.create(Name='Jane Doe', Email='jane@example.com')
        self.assertEqual(str(opinion), 'Jane Doe')

    def test_optional_fields_default_to_blank(self):
        opinion = UserOpinion.objects.create(Name='Jane', Email='jane@example.com')
        self.assertEqual(opinion.Phone, '')
        self.assertEqual(opinion.Organization, '')
        self.assertEqual(opinion.Description, '')
