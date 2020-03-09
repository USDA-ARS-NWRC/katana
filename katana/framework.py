import argparse
import logging
import os
from copy import deepcopy
from datetime import datetime

import coloredlogs
from inicheck.config import MasterConfig, UserConfig
from inicheck.output import print_config_report
from inicheck.tools import check_config, get_user_config

from katana import utils
from katana.get_topo import get_topo_stats, netcdf_dem_to_ascii
from katana.grib_crop_wgrib2 import create_new_grib
from katana.wind_ninja import WindNinja


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
                mcfg = MasterConfig(modules=['katana'])

                # Read in the original users config
                self.ucfg = get_user_config(config, mcfg=mcfg)
                self.config_file = config

            except UnicodeDecodeError as e:
                print(e)
                raise Exception(('The configuration file is not encoded in '
                                 'UTF-8, please change and retry'))

        elif isinstance(config, UserConfig):
            self.ucfg = config
            self.config_file = ''

        else:
            raise Exception(
                'Config passed to Katana is neither file name nor \
                    UserConfig instance')

        warnings, errors = check_config(self.ucfg)
        print_config_report(warnings, errors)
        self.config = self.ucfg.cfg

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
        # Find WindNinja parameters
        ################################################

        # prefix that wind ninja will use in the file naming convention
        self.wn_prefix = os.path.splitext(os.path.basename(self.fp_dem))[0]

        # write ascii dem for WindNinja
        dir_topo = os.path.dirname(self.fp_dem)
        self.wn_topo = os.path.join(dir_topo, '{}{}.asc'.format(
            self.wn_prefix, self.config['topo']['wind_ninja_topo_suffix']
        ))

        self.wn_topo_prj = os.path.join(dir_topo, '{}{}.prj'.format(
            self.wn_prefix, self.config['topo']['wind_ninja_topo_suffix']
        ))

        # write new files
        netcdf_dem_to_ascii(self.fp_dem, self.wn_topo, self._logger,
                            utm_let=self.zone_letter, utm_num=self.zone_number)

        # get info about model domain
        self.ts = get_topo_stats(self.fp_dem)
        self.x1 = self.ts['x']
        self.y1 = self.ts['y']

    def parse_config(self):
        """Parse the config file variables for running katana

        Raises:
            None
        """

        # topo section
        self.fp_dem = self.config['topo']['filename']
        self.zone_letter = self.config['topo']['zone_letter']
        self.zone_number = self.config['topo']['zone_number']

        # find start and end dates
        self.start_date = self.config['time']['start_date']
        self.end_date = self.config['time']['end_date']
        self.fmt_date = '%Y%m%d'

        # create an hourly time step between the start date and end date
        self.date_list = utils.daterange(self.start_date, self.end_date)

        # create a daily list between the start and end date
        self.day_list = utils.daylist(self.start_date, self.end_date)

        self.buff = self.config['input']['buffer']
        self.data_type = self.config['input']['data_type']
        self.directory = self.config['input']['directory']
        if self.data_type != 'hrrr':
            raise IOError('Not an approved input datatype')

        self.out_dir = self.config['output']['out_location']
        self.make_new_gribs = self.config['output']['make_new_gribs']
        self.wn_cfg = self.config['output']['wn_cfg']

        # system config variables
        self.nthreads_w = self.config['input']['num_wgrib_threads']

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

    def run_katana(self):
        """
        Function to crop grib files, create WindNinja config, and run WindNinja
        """

        # create the new grib files for entire run period
        num_files = create_new_grib(
            self.date_list,
            self.directory, self.out_dir,
            self.x1, self.y1, self._logger,
            zone_letter=self.zone_letter,
            zone_number=self.zone_number,
            buff=self.buff,
            nthreads_w=self.nthreads_w,
            make_new_gribs=self.make_new_gribs)

        # make config, run wind ninja, make netcdf
        for idd, day in enumerate(self.day_list):
            self._logger.info('Running WindNinja for day {}'.format(day))
            self._logger.debug(
                '{} input files will be ran'.format(num_files[day]))

            start_time = datetime.now()

            out_dir_day = os.path.join(self.out_dir,
                                       'data{}'.format(
                                           day.strftime(self.fmt_date)),
                                       'wind_ninja_data')
            out_dir_wn = os.path.join(out_dir_day,
                                      'hrrr.{}'.format(
                                          day.strftime(self.fmt_date)))

            # make output folder if it doesn't exist
            if not os.path.isdir(out_dir_day):
                os.makedirs(out_dir_day)

            # run WindNinja_cli
            wn_cfg = deepcopy(self.config['wind_ninja'])
            wn_cfg['forecast_filename'] = out_dir_wn
            # wn_cfg['forecast_duration'] = 0  # num_list[idd]
            wn_cfg['elevation_file'] = self.wn_topo

            wn = WindNinja(
                wn_cfg,
                self.config['output']['wn_cfg'])
            wn.run_wind_ninja()

            telapsed = datetime.now() - start_time
            self._logger.debug('Running day took {} sec'.format(
                telapsed.total_seconds()))

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
