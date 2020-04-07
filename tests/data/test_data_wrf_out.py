

from tests.test_base import KatanaTestCase


class TestWRFout(KatanaTestCase):
    """
    Integration test for Katana using Reynolds Mountain East
    """

    def test_gold_success(self):
        """Check each hour against gold standard
        """

        adj_config = {
            'input': {
                'data_type': 'wrf_out',
                'wrf_filename': './Lakes/input/wrfout_d02_2019-03-05_12_00_00_small.nc'  # noqa
            }
        }
        config = self.update_config(adj_config)

        self.assertTrue(self.run_katana(config))
        self.assertGold(data_type='wrf_out')

    def test_gold_error(self):
        """ Change config to not produce same output as gold file
        """

        adj_config = {
            'input': {
                'data_type': 'wrf_out',
                'wrf_filename': './Lakes/input/wrfout_d02_2019-03-05_12_00_00_small.nc'  # noqa
            },
            'wind_ninja': {
                'output_wind_height': 10.0
            }
        }

        config = self.update_config(adj_config)
        self.assertTrue(self.run_katana(config))

        self.assertGold(data_type='wrf_out', assert_true=False)
