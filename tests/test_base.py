import os
import shutil
import unittest
from copy import deepcopy

from inicheck.tools import cast_all_variables
from inicheck.tools import get_user_config


class KatanaTestCase(unittest.TestCase):
    """
    The base test case for SMRF that will load in the configuration
    file and store as the base config. Also will remove the output
    directory upon tear down.
    """

    def setUp(self):
        """
        Runs the short simulation over reynolds mountain east
        """

        self.test_dir = os.path.abspath('tests/RME')
        self.test_config = os.path.abspath('tests/config.ini')
        self.out_dir = os.path.join(self.test_dir, 'output')

        # read in the base configuration
        self.base_config = get_user_config(self.test_config,
                                           modules=['katana'])

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
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)

    def change_config_option(self, section, option, value, config=None):
        """[summary]

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
