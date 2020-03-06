from katana.framework import Katana
from tests.test_base import KatanaTestCase


class TestConfigurations(KatanaTestCase):

    def test_wind_ninja_error_init_method(self):
        """Pass a wrong config option for initialization method to WindNinja
        """

        config = self.change_config_option(
            'wind_ninja', 'initialization_method', 'AmericaNotAnOption')

        k = Katana(config)
        with self.assertRaises(Exception) as context:
            k.run_katana()

        self.assertTrue("WindNinja has an error"
                        in str(context.exception))

    def test_wind_ninja_time_zone(self):
        """Time zone config for WindNinja
        """

        config = self.change_config_option(
            'wind_ninja', 'time_zone', 'UTC')

        k = Katana(config)
        with self.assertRaises(Exception) as context:
            k.run_katana()

        self.assertTrue("WindNinja has an error"
                        in str(context.exception))

        config = self.change_config_option(
            'wind_ninja', 'time_zone', 'America/Denver')

        k = Katana(config)
        self.assertTrue(k.run_katana())


class TestInputConfigurations(KatanaTestCase):
    """Test the input configuration options
    """

    def test_input_directory(self):
        """Test input directory error
        """

        config = self.change_config_option(
            'input', 'directory', '/tmp')

        k = Katana(config)
        with self.assertRaises(Exception) as context:
            k.run_katana()

        self.assertTrue("No good grib file for 2018-10-01 20"
                        in str(context.exception))

    def test_input_data_type(self):
        """Test input data type error
        """

        config = self.change_config_option(
            'input', 'data_type', 'not_a_datatype')

        with self.assertRaises(Exception) as context:
            Katana(config)

        self.assertTrue("Not an approved input datatype"
                        in str(context.exception))

    def test_input_buffer(self):
        """Test input buffer
        """

        config = self.change_config_option(
            'input', 'buffer', 3000)
        k = Katana(config)
        self.assertTrue(isinstance(k, Katana))

        config = self.change_config_option(
            'input', 'buffer', '3000')
        self.assertTrue(isinstance(k, Katana))
