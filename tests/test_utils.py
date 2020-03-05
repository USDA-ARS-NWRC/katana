import unittest
from datetime import date, datetime

from katana import utils


class TestUtils(unittest.TestCase):
    """Tests for `katana.utils` package."""

    def test_parse_date_str(self):
        value = utils.parse_date("2019-10-1")
        self.assertEqual(datetime(2019, 10, 1), value)

        value = utils.parse_date("2019-10-1 1:00")
        self.assertEqual(datetime(2019, 10, 1, 1, 0), value)

        value = utils.parse_date("2019-10-2 15:35")
        self.assertEqual(datetime(2019, 10, 2, 15, 35), value)

        value = utils.parse_date("2019-10-10 23:21")
        self.assertEqual(datetime(2019, 10, 10, 23, 21), value)

    def test_parse_date_fails_int(self):
        with self.assertRaises(TypeError):
            utils.parse_date(10)

    def test_parse_date_datetime(self):
        to_convert = datetime(2019, 10, 1)
        value = utils.parse_date(to_convert)
        self.assertEqual(value, to_convert)

    def test_parse_date_date(self):
        to_convert = date(2019, 10, 1)
        expected = datetime(2019, 10, 1)
        value = utils.parse_date(to_convert)
        self.assertEqual(value, expected)

    def test_date_range(self):

        start_date = datetime(2019, 10, 1, 1)
        end_date = datetime(2019, 10, 1, 5)

        date_list = utils.daterange(start_date, end_date)

        self.assertTrue(len(date_list) == 5)
        self.assertTrue(date_list[0] == start_date)
        self.assertTrue(date_list[-1] == end_date)

        start_date = datetime(2017, 7, 2, 1)
        end_date = datetime(2017, 7, 3, 5)

        date_list = utils.daterange(start_date, end_date)

        self.assertTrue(len(date_list) == 29)
        self.assertTrue(date_list[0] == start_date)
        self.assertTrue(date_list[-1] == end_date)
