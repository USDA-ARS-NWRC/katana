

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
                'wrf_filename': './RME/input/wrfout_d02_2019-03-05_12_00_00.nc'
            },
            'time': {
                'start_date': '2015-03-03 00:00',
                'end_date': '2015-03-03 04:00'
            }
        }
        config = self.update_config(adj_config)

        self.assertTrue(self.run_katana(config))
        # self.assertGold()
