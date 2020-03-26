#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_katana
----------------------------------

Tests for an entire Katana run.
"""

from katana.framework import Katana
from tests.test_base import KatanaTestCase


class TestNomadsHRRR(KatanaTestCase):
    """
    Integration test for Katana using Reynolds Mountain East
    """

    def test_gold_success(self):
        """Check each hour against gold standard
        """

        try:
            k = Katana(self.test_config)
            k.run_katana()
            result = True
        except Exception as e:
            print(e)
            result = False

        assert(result)
        self.assertGold()

    def test_gold_error(self):
        """ Change config to not produce same output as gold file
        """

        config = self.change_config_option(
            'wind_ninja', 'output_wind_height', 10.0)

        result = self.run_katana(config)

        assert(result)
        self.assertGold(assert_true=False)

    def test_make_new_gribs(self):
        """
        Test if the full Katana suite can run
        """

        # Try full katana framework
        try:
            k = Katana(self.test_config)
            k.run_katana()
            result = True
        except Exception as e:
            print(e)
            result = False

        self.assertTrue(result)

        # Try again without making new gribs
        config = self.change_config_option(
            'output', 'make_new_gribs', False)

        try:
            k = Katana(config)
            k.run_katana()
            result = True
        except Exception as e:
            print(e)
            result = False

        self.assertTrue(result)
