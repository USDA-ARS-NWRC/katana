import numpy as np
import pandas as pd
import os
from subprocess import Popen, PIPE
from datetime import datetime
import logging
import coloredlogs

from katana.get_topo import get_topo_stats, netcdf_dem_to_ascii
from katana.grib_crop_wgrib2 import create_new_grib
from katana.windninja_to_nc import convert_wind_ninja


class Katana():
    """
    Class created to wrap all functionality needed to run WindNinja in the
    context of the USDA ARS snow-water supply modeling workflow
    """

    def __init__(self, fp_dem, zone_letter, zone_number, buff, start_date,
                 end_date, directory, out_dir,wn_cfg,
                 nthreads, nthreads_w, dxy, loglevel, logfile):
        """
        Args:
            fp_dem:         path to netcdf topo file used for smrf
            zone_letter:    UTM zone letter (probably N)
            zone_number:    UTM zone letter
            buff:           WindNinja domain buffer desired (m)
            start_date:     datetime object for start date
            end_date:       datetime object for end date
            directory:      directory containing HRRR grib2 files (directory/hrrr.<date>/hrrr*.grib2)
            out_dir:        output directory where (out_dir/data<date>) will be written
            wn_cfg:         file path where WindNinja config file will be stored
            nthreads:       number of threads used to run WindNinja
            nthreads_w:     number of threads used for wgrib2 commands
            dxy:            grid resolution for running WindNinja
            loglevel:       level for logging info
            logfile:        file where log will be stored
        """

        ################################################
        # Start parsing the arguments
        ################################################
        self.fp_dem = fp_dem
        self.zone_letter = zone_letter
        self.zone_number = zone_number
        self.buff = buff

        # find start and end dates
        self.start_date = start_date
        self.end_date = end_date

        self.fmt_date = '%Y%m%d'

        self.directory = directory
        #out_dir = './sim_files_grib'
        self.out_dir = out_dir

        self.nthreads_w = nthreads_w

        ################################################
        # Create logger
        ################################################
        self.create_log(loglevel, logfile)

        ################################################
        # Find WindNinja parameters
        ################################################
        # wind ninja inputs
        self.wn_cfg = os.path.abspath(wn_cfg)
        # prefix that wind ninja will use in the file naming convention
        self.wn_prefix = os.path.splitext(os.path.basename(self.fp_dem))[0]
        self.nthreads = nthreads

        # write ascii dem for WindNinja
        topo_add = '_windninja_topo'
        dir_topo = os.path.dirname(self.fp_dem)
        self.wn_topo = os.path.join(dir_topo,
                                    self.wn_prefix+topo_add+'.asc')
        self.wn_topo_prj = os.path.join(dir_topo,
                                        self.wn_prefix+topo_add+'.prj')
        # write new files
        netcdf_dem_to_ascii(self.fp_dem, self.wn_topo, self._logger)

        # get info about model domain
        self.ts = get_topo_stats(self.fp_dem)
        self.x1 = self.ts['x']
        self.y1 = self.ts['y']
        self.dxy = dxy

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

        field_styles =  {'hostname': {'color': 'magenta'},
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

        # print title and mountains
        # title, mountain = self.title()
        # for line in mountain:
        #     self._logger.info(line)
        # for line in title:
        #     self._logger.info(line)
        # dump saved logs
        # if len(self.tmp_log) > 0:
        #     for l in self.tmp_log:
        #         self._logger.info(l)
        # if len(self.tmp_warn) > 0:
        #     for l in self.tmp_warn:
        #         self._logger.warning(l)
        # if len(self.tmp_err) > 0:
        #     for l in self.tmp_err:
        #         self._logger.error(l)

    def make_wn_cfg(self, out_dir, wn_topo, num_hours):
        """
        Edit and write the config file options for the WindNinja program

        Args:
            out_dir:
            wn_topo:
            num_hours:

        """

        # populate config files
        base_cfg = {
                    'num_threads'                     : self.nthreads,
                    'elevation_file'                  : os.path.abspath(wn_topo),
                    'initialization_method'           : 'wxModelInitialization',
                    'time_zone'                       : 'Atlantic/Reykjavik',
                    'forecast_filename'               : os.path.abspath(out_dir),
                    'forecast_duration'               : num_hours,
                    'output_wind_height'              : 5.0,
                    'units_output_wind_height'        : 'm',
                    'output_speed_units'              : 'mps',
                    'vegetation'                      : 'grass',
                    'input_speed_units'               : 'mps',
                    'input_wind_height'               : 10.0,
                    'units_input_wind_height'         : 'm',
                    'diurnal_winds'                   : True,
                    'mesh_resolution'                 : self.dxy,
                    'units_mesh_resolution'           : 'm',
                    'write_goog_output'               : False,
                    'write_shapefile_output'          : False,
                    'write_ascii_output'              : True,
                    'write_farsite_atm'               : False,
                    'write_wx_model_goog_output'      : False,
                    'write_wx_model_shapefile_output' : False,
                    'write_wx_model_ascii_output'     : False
                    }

        # write each line to config
        self._logger.info('Creating file {}'.format(self.wn_cfg))
        with open(self.wn_cfg, 'w') as f:
            for k,v in base_cfg.items():
                f.write('{} = {}\n'.format(k,v))

    def run_wind_ninja(self):
        """
        Create the command line call to run the WindNinja_cli

        """
        action = 'WindNinja_cli {}'.format(self.wn_cfg)

        self._logger.info('Running {}'.format(action))
        s = Popen(action, shell=True,stdout=PIPE)

        while True:
            line = s.stdout.readline().decode()
            self._logger.debug(line)
            if not line:
                break
        #s.wait()

    def run_katana(self):
        """
        Function to crop grib files, create WindNinja config, and run WindNinja
        """

        # create the new grib files
        date_list, num_list = create_new_grib(self.start_date, self.end_date,
                                              self.directory, self.out_dir,
                                              self.x1, self.y1, self._logger,
                                              zone_letter=self.zone_letter,
                                              zone_number=self.zone_number,
                                              buff=self.buff,
                                              nthreads_w=self.nthreads_w)

        self._logger.debug(date_list)
        # make config, run wind ninja, make netcdf
        for idd, day in enumerate(date_list):
            if num_list[idd] > 0:
                out_dir_day = os.path.join(self.out_dir,
                                           'data{}'.format(day.strftime(self.fmt_date))
                                           , 'wind_ninja_data')
                out_dir_wn = os.path.join(out_dir_day,
                                           'hrrr.{}'.format(day.strftime(self.fmt_date)))
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

        self._logger.info('Katana closed --> %s' % datetime.now())
