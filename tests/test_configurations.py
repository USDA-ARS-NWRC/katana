import unittest
import os, shutil
import numpy as np
import pandas as pd
from copy import deepcopy

from inicheck.tools import cast_all_variables
from inicheck.tools import get_user_config, check_config
from katana.framework import Katana


class KatanaTestCase(unittest.TestCase):
    """
    The base test case for SMRF that will load in the configuration file and store as
    the base config. Also will remove the output directory upon tear down.
    """

    def setUp(self):
        """
        Runs the short simulation over reynolds mountain east
        """
        self.test_dir = os.path.abspath('tests/RME')
        self.test_cfg = os.path.abspath('tests/config.ini')
        # read in the base configuration
        self.base_config = get_user_config(self.test_cfg,
                                           modules = ['katana'])

    def tearDown(self):
        """
        Clean up the output directory
        """

        folder = os.path.join(self.test_dir, 'output')
        nodelete = os.path.join(folder, '.keep')
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            if file_path != nodelete:
                pass
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)


class TestConfigurations(KatanaTestCase):

    def test_base_run(self):
        """
        Test if the full Katana suite can run
        """

        # Try full katana framework
        try:
            k =  Katana(self.test_cfg)
            k.run_katana()
            result = True
        except:
            result = False

        print('Finished test one')
        self.assertTrue(result)

        # Try again without making new gribs
        config = deepcopy(self.base_config)
        config.raw_cfg['output']['make_new_gribs'] = False
        config.apply_recipes()

        config = cast_all_variables(config, config.mcfg)

        try:
            k =  Katana(config)
            k.run_katana()
            result = True
        except:
            result = False

        print('Finished test two')
        self.assertTrue(result)
