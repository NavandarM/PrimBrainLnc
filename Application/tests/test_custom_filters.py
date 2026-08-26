from django.test import SimpleTestCase

from Application.custom_filters import get_range


class GetRangeFilterTests(SimpleTestCase):
    def test_returns_range_object(self):
        self.assertEqual(list(get_range(5)), [0, 1, 2, 3, 4])

    def test_zero_returns_empty_range(self):
        self.assertEqual(list(get_range(0)), [])
