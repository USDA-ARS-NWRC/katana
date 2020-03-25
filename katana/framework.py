import argparse
import logging
import os
from datetime import datetime

import coloredlogs
from inicheck.config import MasterConfig, UserConfig
from inicheck.output import print_config_report
from inicheck.tools import check_config, get_user_config

from katana import utils
from katana.topo import Topo
from katana.data.nomads_hrrr import NomadsHRRR


def cli():
    '''
    katana is a command line program designed to take a config file. This
    will be fed to the run_katana function within framework.
    '''

    # Parse arguments
    p = argparse.ArgumentParser(
        description='Run Katana, the WindNinja wrapper.')

    p.add_argument('cfg', type=str,
                   help='Path to config file')

    args = p.parse_args()

    # run the katana framework
    with Katana(args.cfg) as k:
        k.run_katana()


class Katana():
    """
    Class created to wrap all functionality needed to run WindNinja in the
    context of the USDA ARS snow-water supply modeling workflow
    """

    def __init__(self, config):
        """[summary]

        Arguments:
            config {string} -- path to the config file or an
                                inicheck UserConfig object
        """

        if isinstance(config, str):
            if not os.path.isfile(config):
                raise Exception('Configuration file does not exist --> {}'
                                .format(config))

            try:
                # Read in the original users config
                self.ucfg = get_user_config(config, modules='katana')

            except UnicodeDecodeError as e:
                print(e)
                raise Exception(('The configuration file is not encoded in '
                                 'UTF-8, please change and retry'))

        elif isinstance(config, UserConfig):
            self.ucfg = config

        else:
            raise Exception(
                'Config passed to Katana is neither file name nor \
                    UserConfig instance')

        self.config_file = self.ucfg.filename

        warnings, errors = check_config(self.ucfg)
        print_config_report(warnings, errors)
        self.config = self.ucfg.cfg

        if len(errors) > 0:
            raise Exception("Error in config file. Check report above.")

        self.start_timing = datetime.now()

        ################################################
        # Start parsing the arguments
        ################################################
        self.parse_config()

        ################################################
        # Create logger
        ################################################
        self.create_log()

        ################################################
        # Initialize the input data
        ################################################
        self.initialize_input_data()

        ################################################
        # Initialize the topo
        ################################################
        self.topo = Topo(self.config)

        self._logger.debug('Katana initialized')

    def parse_config(self):
        """Parse the config file variables for running katana

        Raises:
            None
        """

        # find start and end dates
        self.start_date = self.config['time']['start_date']
        self.end_date = self.config['time']['end_date']
        self.fmt_date = '%Y%m%d'

        # create an hourly time step between the start date and end date
        self.date_list = utils.daterange(self.start_date, self.end_date)

        # create a daily list between the start and end date
        self.day_list = utils.daylist(self.start_date, self.end_date)

        self.data_type = self.config['input']['data_type']

        self.out_dir = self.config['output']['out_location']
        self.wn_cfg = self.config['output']['wn_cfg']

    def create_log(self):
        '''
        Create logger and log file. If logfile is None,
        the logger will print to the screen with colored logs.

        Returns:
            None, creates a logger
        '''

        loglevel = self.config['logging']['log_level']
        logfile = self.config['logging']['log_file']

        level_styles = {'info': {'color': 'white'},
                        'notice': {'color': 'magenta'},
                        'verbose': {'color': 'blue'},
                        'success': {'color': 'green', 'bold': True},
                        'spam': {'color': 'green', 'faint': True},
                        'critical': {'color': 'red', 'bold': True},
                        'error': {'color': 'red'},
                        'debug': {'color': 'green'},
                        'warning': {'color': 'yellow'}}

        field_styles = {'hostname': {'color': 'magenta'},
                        'programname': {'color': 'cyan'},
                        'name': {'color': 'white'},
                        'levelname': {'color': 'white', 'bold': True},
                        'asctime': {'color': 'green'}}

        # start logging
        loglevel = loglevel.upper()

        numeric_level = getattr(logging, loglevel, None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)

        fmt = '%(levelname)s:%(name)s:%(message)s'
        if logfile is not None:
            # let user know
            print('Logging to file: {}'.format(logfile))

            logging.basicConfig(filename=logfile,
                                filemode='w',
                                level=numeric_level,
                                format=fmt)
        else:
            logging.basicConfig(level=numeric_level)
            coloredlogs.install(level=numeric_level,
                                fmt=fmt,
                                level_styles=level_styles,
                                field_styles=field_styles)

        self._loglevel = numeric_level
        self._logger = logging.getLogger(__name__)

    def initialize_input_data(self):
        """Initialize the input data classes based on
        the input data type
        """

        self._logger.info('Initializing input data')

        if self.data_type == 'hrrr':
            # check smrf on how it's done
            self.input_data = NomadsHRRR(self.config)

    def run_katana(self):
        """
        Function to crop grib files, create WindNinja config, and run WindNinja
        """

        # initialize the data in preparation for WindNinja simulation
        self.input_data.initialize_data()

        # run WindNinja
        self.input_data.run()

        self.run_time()
        return True

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def run_time(self):
        """
        Provide some logging info about when Katana was closed
        """
        run_timing = datetime.now() - self.start_timing
        self._logger.info('Katana ran in: {}'.format(run_timing))
        self._logger.info('Katana closed --> {}'.format(datetime.now()))
