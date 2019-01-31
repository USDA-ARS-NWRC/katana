#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_katana
----------------------------------

Tests for an entire Katana run.
"""

import unittest
import shutil
import os
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from katana.framework import Katana

def compare_image(gold_image,test_image):
    """
    Compares two netcdfs images to and determines if they are the same.

    Args:
        v_name: Name with in the file contains
        gold_image: File containing gold standard results
        test_image: File containing test results to be compared
    Returns:
        Boolean: Whether the two images were the same
    """

    gold= np.loadtxt(gold_image, skiprows=6)

    rough = np.loadtxt(test_image, skiprows=6)

    result = np.abs(gold-rough)

    return  not np.any(result>0.0)


class TestStandardRME(unittest.TestCase):
    """
    Integration test for AWSM using reynolds mountain east
    """

    @classmethod
    def setUpClass(self):
        """
        Runs the short simulation over reynolds mountain east
        """
        self.test_dir = os.path.abspath('tests/RME')
        # check whether or not this is being ran as a single test or part of the suite
        self.fp_dem = os.path.join(self.test_dir, 'topo/topo.nc')
        self.zone_letter = 'N'
        self.zone_number = 11
        self.buff = 6000
        start_date = '2018-10-01 20:00'
        end_date = '2018-10-01 23:00'
        self.directory = os.path.join(self.test_dir, 'input')
        self.out_dir = os.path.join(self.test_dir, 'output')
        self.wn_cfg = os.path.join(self.test_dir, 'output/wn_cfg.txt')
        self.nthreads = 1
        self.nthreads_w = 1
        self.dxy = 50
        self.loglevel = 'info'
        self.logfile = os.path.join(self.test_dir, 'output/log.txt')
        self.make_new_gribs = True

        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

        try:
            k =  Katana(self.fp_dem, self.zone_letter,
                        self.zone_number, self.buff,
                        self.start_date, self.end_date,
                        self.directory, self.out_dir,
                        self.wn_cfg, self.nthreads,
                        self.nthreads_w,
                        self.dxy, self.loglevel,
                        self.logfile, self.make_new_gribs)
            k.run_katana()
            result = True
        except:
            result = False

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
