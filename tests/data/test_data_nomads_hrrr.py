#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_katana
----------------------------------

Tests for an entire Katana run.
"""

from tests.test_base import KatanaTestCase


class TestNomadsHRRR(KatanaTestCase):
    """
    Integration test for Katana using Reynolds Mountain East
    """

    def test_gold_success(self):
        """Check each hour against gold standard
        """

        self.assertTrue(self.run_katana())
        self.assertGold()

    def test_gold_error(self):
        """ Change config to not produce same output as gold file
        """

        config = self.change_config_option(
            'wind_ninja', 'output_wind_height', 10.0)

        self.assertTrue(self.run_katana(config))

        self.assertGold(assert_true=False)

    def test_make_new_gribs(self):
        """
        Test if the full Katana suite can run
        """

        self.assertTrue(self.run_katana())

        # Try again without making new gribs
        config = self.change_config_option(
            'output', 'make_new_gribs', False)

        self.assertTrue(self.run_katana(config))
