from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from Application.forms import (
    ExploreFormSeq,
    ExploreMultipleIds,
    ExplorationForm,
    ExplorationFormByIDs,
    Is_fasta_file,
    UserMessageForm,
    check_for_location,
    confirm_organism,
)


class CheckForLocationValidatorTests(SimpleTestCase):
    def test_accepts_valid_format(self):
        check_for_location('Chr1:1231-1413')  # should not raise

    def test_rejects_missing_chr_prefix(self):
        with self.assertRaises(ValidationError):
            check_for_location('1:1231-1413')

    def test_rejects_non_numeric_positions(self):
        with self.assertRaises(ValidationError):
            check_for_location('Chr1:abc-1413')

    def test_missing_colon_raises_indexerror_not_validationerror(self):
        # Pre-existing bug: the validator does value.split(":")[1] without checking
        # a colon is present, so malformed input with no ":" blows up with an
        # unhandled IndexError instead of a clean form ValidationError. Documenting
        # the current behavior here rather than silently working around it.
        with self.assertRaises(IndexError):
            check_for_location('not-a-location')


class ConfirmOrganismValidatorTests(SimpleTestCase):
    def test_accepts_known_organisms_case_insensitively(self):
        confirm_organism('human')
        confirm_organism('CHIMP')
        confirm_organism('Gorilla')
        confirm_organism('gibbon')

    def test_rejects_unknown_organism(self):
        with self.assertRaises(ValidationError):
            confirm_organism('Martian')


class IsFastaFileValidatorTests(SimpleTestCase):
    def test_accepts_content_starting_with_caret(self):
        Is_fasta_file('>header\nATCG')  # should not raise

    def test_rejects_content_without_caret(self):
        with self.assertRaises(ValidationError):
            Is_fasta_file('ATCG')


class UserMessageFormTests(SimpleTestCase):
    def _valid_data(self, **overrides):
        data = {
            'Name': 'Jane', 'Email': 'jane@example.com', 'Phone': '',
            'Organization': '', 'Description': 'Nice tool', 'botcatcher': '',
        }
        data.update(overrides)
        return data

    def test_valid_submission_passes(self):
        form = UserMessageForm(self._valid_data())
        self.assertTrue(form.is_valid())

    def test_honeypot_filled_fails_validation(self):
        form = UserMessageForm(self._valid_data(botcatcher='spammer'))
        self.assertFalse(form.is_valid())
        self.assertIn('botcatcher', form.errors)

    def test_missing_required_fields_fails(self):
        form = UserMessageForm(self._valid_data(Name='', Email=''))
        self.assertFalse(form.is_valid())
        self.assertIn('Name', form.errors)
        self.assertIn('Email', form.errors)


class ExplorationFormByIDsTests(SimpleTestCase):
    def test_blank_form_is_valid_since_fields_are_optional(self):
        form = ExplorationFormByIDs(data={})
        self.assertTrue(form.is_valid())

    def test_accepts_id_and_organism_choice(self):
        form = ExplorationFormByIDs(data={'ID': 'TCONS_1', 'Organism': 'Human'})
        self.assertTrue(form.is_valid())

    def test_rejects_organism_outside_choices(self):
        form = ExplorationFormByIDs(data={'ID': 'TCONS_1', 'Organism': 'Martian'})
        self.assertFalse(form.is_valid())


class ExplorationFormTests(SimpleTestCase):
    def test_valid_location_passes(self):
        form = ExplorationForm(data={'Location': 'Chr1:100-200', 'Organism': 'Human', 'Overlap': ''})
        self.assertTrue(form.is_valid())

    def test_invalid_location_fails(self):
        form = ExplorationForm(data={'Location': 'Chr1:abc-200', 'Organism': 'Human', 'Overlap': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('Location', form.errors)

    def test_blank_location_is_valid_since_field_is_optional(self):
        form = ExplorationForm(data={'Location': '', 'Organism': '', 'Overlap': ''})
        self.assertTrue(form.is_valid())


class ExploreFormSeqTests(SimpleTestCase):
    def test_valid_fasta_sequence_and_database_passes(self):
        form = ExploreFormSeq(data={'Sequence': '>h\nATCG', 'Organism_db': ['Human']})
        self.assertTrue(form.is_valid())

    def test_non_fasta_sequence_fails(self):
        form = ExploreFormSeq(data={'Sequence': 'ATCG', 'Organism_db': ['Human']})
        self.assertFalse(form.is_valid())
        self.assertIn('Sequence', form.errors)

    def test_missing_database_selection_fails(self):
        form = ExploreFormSeq(data={'Sequence': '>h\nATCG'})
        self.assertFalse(form.is_valid())
        self.assertIn('Organism_db', form.errors)

    def test_missing_sequence_fails(self):
        form = ExploreFormSeq(data={'Organism_db': ['Human']})
        self.assertFalse(form.is_valid())
        self.assertIn('Sequence', form.errors)


class ExploreMultipleIdsTests(SimpleTestCase):
    def test_blank_form_is_valid_since_fields_are_optional(self):
        form = ExploreMultipleIds(data={})
        self.assertTrue(form.is_valid())

    def test_accepts_multiple_ids_and_organism(self):
        form = ExploreMultipleIds(data={'MultiIDs': 'TCONS_1, TCONS_2', 'Organism': 'Gibbon'})
        self.assertTrue(form.is_valid())
