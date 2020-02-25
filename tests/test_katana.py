#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_katana
----------------------------------

Tests for an entire Katana run.
"""

import os
import unittest

import dateparser
import numpy as np

from katana.framework import Katana


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


class TestStandardRME(unittest.TestCase):
    """
    Integration test for Katana using Reynolds Mountain East
    """

    @classmethod
    def setUpClass(self):
        """
        Runs the short simulation over reynolds mountain east
        """
        self.test_dir = os.path.abspath('tests/RME')
        self.test_cfg = os.path.abspath('tests/config.ini')
        self.out_dir = os.path.join(self.test_dir, 'output')

        try:
            k = Katana(self.test_cfg)
            k.run_katana()
            result = True
        except:
            result = False

        assert(result)

    def test_image(self):
        """
        Check each hour against gold standard
        """

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

            print('Testing {}'.format(output_now))
            a = compare_image(output_gold, output_now)
            print(a)

            assert(a)


if __name__ == '__main__':
    unittest.main()
