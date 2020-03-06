
import sys
from unittest.mock import patch

from katana.framework import cli
from tests.test_base import KatanaTestCase


class TestKatanaCli(KatanaTestCase):
    """
    Integration test for Katana using Reynolds Mountain East
    """

    def test_run_katana_cli(self):
        """Test the cli run_katana
        """

        test_args = ['run_katana', self.test_config]
        with patch.object(sys, 'argv', test_args):
            cli()
            self.assertGold()

        test_args = ['run_katana', '/tmp/config.ini']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(Exception) as context:
                cli()

            self.assertTrue("Configuration file does not exist"
                            in str(context.exception))
