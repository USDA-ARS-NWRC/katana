import logging
import os
from datetime import datetime
from subprocess import PIPE, Popen

import coloredlogs

from katana.get_topo import get_topo_stats, netcdf_dem_to_ascii
from katana.grib_crop_wgrib2 import create_new_grib

from inicheck.config import MasterConfig, UserConfig
from inicheck.tools import get_user_config, check_config
from inicheck.output import print_config_report, generate_config
from inicheck.tools import cast_all_variables


class Katana():
    """
    Class created to wrap all functionality needed to run WindNinja in the
    context of the USDA ARS snow-water supply modeling workflow
    """

    def __init__(self, config):
        #
        # fp_dem, zone_letter, zone_number, buff, start_date,
        #              end_date, directory, out_dir,wn_cfg,
        #              nthreads, nthreads_w, dxy, loglevel, logfile, make_new_gribs):
        """
        Args:
            fp_dem:         path to netcdf topo file used for smrf
            zone_letter:    UTM zone letter (probably N)
            zone_number:    UTM zone letter
            buff:           WindNinja domain buffer desired (m)
            start_date:     datetime object for start date
            end_date:       datetime object for end date
            directory:      directory containing HRRR grib2
                            files (directory/hrrr.<date>/hrrr*.grib2)
            out_dir:        output directory where (out_dir/data<date>)
                            will be written
            wn_cfg:         file path where WindNinja config file
                            will be stored
            nthreads:       number of threads used to run WindNinja
            nthreads_w:     number of threads used for wgrib2 commands
            dxy:            grid resolution for running WindNinja
            loglevel:       level for logging info
            logfile:        file where log will be stored
            make_new_gribs: option to use existing gribs if this
                            step has been completed
        """
        if isinstance(config, str):
            if not os.path.isfile(config):
                raise Exception('Configuration file does not exist --> {}'
                                .format(config))
            configFile = config

            try:
                mcfg = MasterConfig(modules=['katana'])

                # Read in the original users config
                self.ucfg = get_user_config(configFile, mcfg=mcfg)
                self.configFile = configFile

            except UnicodeDecodeError as e:
                print(e)
                raise Exception(('The configuration file is not encoded in '
                                 'UTF-8, please change and retry'))

        elif isinstance(config, UserConfig):
            self.ucfg = config
            configFile = ''

        else:
            raise Exception(
                'Config passed to Katana is neither file name nor UserConfig instance')

        print("Checking config file for issues...")
        warnings, errors = check_config(self.ucfg)
        print_config_report(warnings, errors)

        self.config = self.ucfg.cfg
        # print(self.config)

        self.start_timing = datetime.now()
        ################################################
        # Start parsing the arguments
        ################################################
        self.fp_dem = self.config['topo']['filename']
        self.zone_letter = self.config['topo']['zone_letter']
        self.zone_number = self.config['topo']['zone_number']

        # find start and end dates
        self.start_date = self.config['time']['start_date']
        self.end_date = self.config['time']['end_date']
        self.fmt_date = '%Y%m%d'

        self.buff = self.config['input']['buffer']
        self.data_type = self.config['input']['data_type']
        self.directory = self.config['input']['directory']
        if self.data_type != 'hrrr':
            raise IOError('Not an approved input datatype')

        self.out_dir = self.config['output']['out_location']
        self.make_new_gribs = self.config['output']['make_new_gribs']
        self.wn_cfg = self.config['output']['wn_cfg']
        self.dxy = self.config['output']['dxy']

        # system config variables
        self.nthreads_w = self.config['system']['nthreads_grib']
        self.nthreads = self.config['system']['nthreads']

        ################################################
        # Create logger
        ################################################
        # logging config variables
        loglevel = self.config['logging']['log_level']
        logfile = self.config['logging']['log_file']
        self.create_log(loglevel, logfile)

        ################################################
        # Find WindNinja parameters
        ################################################

        # prefix that wind ninja will use in the file naming convention
        self.wn_prefix = os.path.splitext(os.path.basename(self.fp_dem))[0]

        # write ascii dem for WindNinja
        topo_add = '_windninja_topo'
        dir_topo = os.path.dirname(self.fp_dem)
        self.wn_topo = os.path.join(dir_topo,
                                    self.wn_prefix+topo_add+'.asc')
        self.wn_topo_prj = os.path.join(dir_topo,
                                        self.wn_prefix+topo_add+'.prj')
        # write new files
        netcdf_dem_to_ascii(self.fp_dem, self.wn_topo, self._logger,
                            utm_let=self.zone_letter, utm_num=self.zone_number)

        # get info about model domain
        self.ts = get_topo_stats(self.fp_dem)
        self.x1 = self.ts['x']
        self.y1 = self.ts['y']

    def create_log(self, loglevel, logfile):
        '''
        Create logger and log file. If logfile is None,
        the logger will print to the screen with colored logs.

        Args:
            loglevel:   level of information from logs (debug, info, etc)
            logfile:    location of file where log will be written

        Returns:
            creates a logger
        '''

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

    def make_wn_cfg(self, out_dir, wn_topo, num_hours):
        """
        Edit and write the config file options for the WindNinja program

        Args:
            out_dir:
            wn_topo:
            num_hours:

        Result:
            Writes WindNinja config file
        """

        # populate config files
        base_cfg = {
            'num_threads': self.nthreads,
            'elevation_file': os.path.abspath(wn_topo),
            'initialization_method': 'wxModelInitialization',
            'time_zone': 'Atlantic/Reykjavik',
            'forecast_filename': os.path.abspath(out_dir),
            'forecast_duration': num_hours,
            'output_wind_height': 5.0,
            'units_output_wind_height': 'm',
            'output_speed_units': 'mps',
            'vegetation': 'grass',
            'input_speed_units': 'mps',
            'input_wind_height': 10.0,
            'units_input_wind_height': 'm',
            'diurnal_winds': True,
            'mesh_resolution': self.dxy,
            'units_mesh_resolution': 'm',
            'write_goog_output': False,
            'write_shapefile_output': False,
            'write_ascii_output': True,
            'write_farsite_atm': False,
            'write_wx_model_goog_output': False,
            'write_wx_model_shapefile_output': False,
            'write_wx_model_ascii_output': False
        }

        # write each line to config
        self._logger.info('Creating file {}'.format(self.wn_cfg))
        with open(self.wn_cfg, 'w') as f:
            for k, v in base_cfg.items():
                f.write('{} = {}\n'.format(k, v))

    def run_wind_ninja(self):
        """
        Create the command line call to run the WindNinja_cli

        """
        # construct call
        action = 'WindNinja_cli {}'.format(self.wn_cfg)

        # run command line using Popen
        self._logger.info('Running {}'.format(action))
        s = Popen(action, shell=True, stdout=PIPE, stderr=PIPE)

        # read output from commands
        while True:
            line = s.stdout.readline().decode()
            eline = s.stderr.readline().decode()
            self._logger.debug(line)
            # break if we're done
            if not line:
                break
            # error if WindNinja errors
            if "Exception" in eline:
                self._logger.error("WindNinja has an error")
                raise Exception(eline)

    def run_katana(self):
        """
        Function to crop grib files, create WindNinja config, and run WindNinja
        """

        # create the new grib files for entire run period
        date_list, num_list = create_new_grib(
            self.start_date, self.end_date,
            self.directory, self.out_dir,
            self.x1, self.y1, self._logger,
            zone_letter=self.zone_letter,
            zone_number=self.zone_number,
            buff=self.buff,
            nthreads_w=self.nthreads_w,
            make_new_gribs=self.make_new_gribs)

        # self._logger.debug(date_list)
        # make config, run wind ninja, make netcdf
        for idd, day in enumerate(date_list):
            # if there are files
            if num_list[idd] > 0:
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
                self.make_wn_cfg(out_dir_wn, self.wn_topo, num_list[idd])

                self.run_wind_ninja()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Provide some logging info about when AWSM was closed
        """
        run_timing = datetime.now() - self.start_timing
        self._logger.info('Katana ran in: {}'.format(run_timing))
        self._logger.info('Katana closed --> {}'.format(datetime.now()))
