from copy import deepcopy

from inicheck.tools import cast_all_variables

from tests.test_base import KatanaTestCase


class TestRecipes(KatanaTestCase):
    """Test the recipes 
    """

    def cast_recipes(self, config):
        """Cast the inicheck recipes

        Arguments:
            config {UserConfig} -- UserConfig object to modify

        Returns:
            UserConfig -- Modified UserConfig object
        """

        config.apply_recipes()
        config = cast_all_variables(config, config.mcfg)

        return config

    def master_config(self, config):
        """Create a master config dictionary with a
        list of the keys

        Arguments:
            config {UserConfig} -- UserConfig object to create
                a master config from

        Returns:
            [dict] -- master_config dict that has all sections
                and items from the provided UserConfig
        """

        master_config = {}
        for key in config.mcfg.cfg.keys():
            master_config[key] = list(config.mcfg.cfg[key].keys())

        return master_config

    def check_config(self, config, master_config):
        """Check that the config read by inicheck matches
        the master_config (expected) results

        Arguments:
            config {inicheck UserConfig} -- UserConfig object to check
            master_config {dict} -- dict of sections and items
                that should be in the UserConfig
        """

        # ensure that there are no
        for key, items in master_config.items():
            test_items = list(config.cfg[key].keys())

            for item in items:
                self.assertTrue(item in test_items)
                test_items.remove(item)

            self.assertTrue(len(test_items) == 0)

    def test_hrrr_recipe(self):
        """Test the hrrr recipe
        """

        # no changes to the base config
        config = deepcopy(self.base_config)

        # get the master config list
        master_config = self.master_config(config)

        # make changes
        master_config['input'] = [
            'data_type',
            'hrrr_directory',
            'hrrr_buffer',
            'hrrr_num_wgrib_threads'
        ]

        self.check_config(config, master_config)

    def test_wrf_recipe(self):
        """Test the wrf recipe
        """

        config = self.change_config_option(
            'input', 'data_type', 'wrf_out')
        config = self.change_config_option(
            'input', 'wrf_filename', './RME/input/WRF_test.nc', config)

        # get the master config list
        master_config = self.master_config(config)

        # make changes
        master_config['input'] = [
            'data_type',
            'wrf_filename'
        ]
        master_config['output'].remove('make_new_gribs')

        self.check_config(config, master_config)
