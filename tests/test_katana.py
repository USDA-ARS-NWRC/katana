#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_katana
----------------------------------

Tests for an entire Katana run.
"""

import os
import unittest

import numpy as np

from katana.framework import Katana
from tests.test_base import KatanaTestCase


def compare_image(gold_image, test_image):
    """
    Compares two netcdfs images to and determines if they are the same.

    Args:
        v_name: Name with in the file contains
        gold_image: File containing gold standard results
        test_image: File containing test results to be compared
    Returns:
        Boolean: Whether the two images were the same
    """

    gold = np.loadtxt(gold_image, skiprows=6)
    rough = np.loadtxt(test_image, skiprows=6)
    result = np.abs(gold-rough)

    return not np.any(result > 0.0)


class TestStandardRME(KatanaTestCase):
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

        d1 = 'data20181001/wind_ninja_data'
        hour_list = ['{}/topo_windninja_topo_10-01-2018_2000_50m_vel.asc',
                     '{}/topo_windninja_topo_10-01-2018_2100_50m_vel.asc',
                     '{}/topo_windninja_topo_10-01-2018_2200_50m_vel.asc',
                     '{}/topo_windninja_topo_10-01-2018_2300_50m_vel.asc']
        hour_list = [hl.format(d1) for hl in hour_list]

        for hl in hour_list:
            output_now = os.path.join(self.out_dir, hl)

            output_gold = os.path.join(self.test_dir, 'gold',
                                       os.path.basename(hl))

            self.assertTrue(compare_image(output_gold, output_now))

    def test_gold_error(self):
        """ Change config to not produce same output as gold file
        """

        config = self.change_config_option(
            'wind_ninja', 'output_wind_height', 10.0)

        result = self.run_katana(config)
        assert(result)

        d1 = 'data20181001/wind_ninja_data'
        hour_list = ['{}/topo_windninja_topo_10-01-2018_2000_50m_vel.asc',
                     '{}/topo_windninja_topo_10-01-2018_2100_50m_vel.asc',
                     '{}/topo_windninja_topo_10-01-2018_2200_50m_vel.asc',
                     '{}/topo_windninja_topo_10-01-2018_2300_50m_vel.asc']
        hour_list = [hl.format(d1) for hl in hour_list]

        for hl in hour_list:
            output_now = os.path.join(self.out_dir, hl)

            output_gold = os.path.join(self.test_dir, 'gold',
                                       os.path.basename(hl))

            self.assertFalse(compare_image(output_gold, output_now))

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
