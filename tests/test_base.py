import os
import shutil
import unittest
from copy import deepcopy
from glob import glob

import numpy as np
from inicheck.tools import cast_all_variables, get_user_config

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


class KatanaTestCase(unittest.TestCase):
    """
    The base test case for Katana that will load in the configuration
    file and store as the base config. Also will remove the output
    directory upon tear down.
    """

    @classmethod
    def setUpClass(cls):
        """
        Runs the short simulation over reynolds mountain east
        """

        cls.test_dir = os.path.abspath('tests/Lakes')
        cls.test_config = os.path.abspath('tests/config.ini')
        cls.out_dir = os.path.join(cls.test_dir, 'output')

        # read in the base configuration
        cls.base_config = get_user_config(cls.test_config,
                                          modules=['katana'])

    def tearDown(self):
        """
        Clean up the output directory
        """

        nodelete = ['.keep']
        nodelete = [os.path.join(self.out_dir, filename)
                    for filename in nodelete]
        for the_file in os.listdir(self.out_dir):
            file_path = os.path.join(self.out_dir, the_file)
            if file_path not in nodelete:
                pass
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)

        # topo directory
        folder = os.path.join(self.test_dir, 'topo', 'topo_windninja_topo*')
        for filename in glob(folder):
            os.unlink(filename)

    def assertGold(self, data_type='hrrr', assert_true=True):
        """Assert that the gold files match

        Keyword Arguments:
            assert_true {bool} -- either assertTrue or
                assertFalse (default: {True})
        """

        d1 = 'data20190305/wind_ninja_data'
        hour_list = ['{}/topo_windninja_topo_03-05-2019_1300_200m_vel.asc',
                     '{}/topo_windninja_topo_03-05-2019_1400_200m_vel.asc',
                     '{}/topo_windninja_topo_03-05-2019_1500_200m_vel.asc',
                     '{}/topo_windninja_topo_03-05-2019_1600_200m_vel.asc']
        hour_list = [hl.format(d1) for hl in hour_list]

        for hl in hour_list:
            output_now = os.path.join(self.out_dir, hl)

            output_gold = os.path.join(self.test_dir, 'gold', data_type,
                                       os.path.basename(hl))
            if assert_true:
                self.assertTrue(compare_image(output_gold, output_now))
            else:
                self.assertFalse(compare_image(output_gold, output_now))

    def run_katana(self, config_file=None):
        """Run katana for the given config file
        """
        if config_file is None:
            config_file = self.test_config

        try:
            k = Katana(config_file)
            k.run_katana()
            result = True
        except Exception as e:
            print(e)
            result = False

        return result

    def change_config_option(self, section, option, value, config=None):
        """Change a configuration option in the config file. Either pass
        a UserConfig object or copy the base config to begin modifying.

        Arguments:
            section {str} -- config section name
            option {str} -- config option name
            value {str} -- config option value

        Keyword Arguments:
            config {UserConfig} -- If None will copy the base config,
                    else it will modify an existing config (default: {None})
        """

        if config is None:
            config = deepcopy(self.base_config)

        config.raw_cfg[section][option] = value
        config.apply_recipes()
        config = cast_all_variables(config, config.mcfg)

        return config

    def update_config(self, update, config=None):
        """Update the config file with a dictionary of items

        Arguments:
            update {dict} -- dict of section updates

        Keyword Arguments:
            config {UserConfig} -- UserConfig object or copy 
                the base config (default: {None})
        """

        if config is None:
            config = deepcopy(self.base_config)

        config.raw_cfg.update(update)
        config.apply_recipes()
        config = cast_all_variables(config, config.mcfg)

        return config
