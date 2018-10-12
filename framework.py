"""
Basic outline for reading in grib files, converting to cropped netCDF
with the correct variables

Notes:
Initialize a smrf instance from the correct config to make all of this easier, follow the loadGrid.py outline

Outline:
-make hrrr.HRRR class
-set variable map to desired one
-make up a boundary box (add half km, round to nearest half km on either side of domain?)
-call class.get_saved_data with correct boundary box, var map, and grib file location
-create netcdf of the files
-write data to netcdf (make sure units, variables match the ones in the grib file to start)

"""
import numpy as np
import pandas as pd
import os
from subprocess import Popen, PIPE
from datetime import datetime

from get_topo import get_topo_stats
from grib_crop_wgrib2 import create_new_grib
from windninja_to_nc import convert_wind_ninja


class Katana():
    """
    Class created to wrap all functionality needed to run WindNinja in the
    context of the USDA ARS snow-water supply modeling workflow
    """

    def __init__(self, fp_dem, zone_letter, zone_number, buff, start_date,
                 end_date, wy_start, directory, out_dir, wn_topo,
                 wn_topo_prj, wn_cfg, nthreads, dxy):


        self.fp_dem = fp_dem
        self.zone_letter = zone_letter
        self.zone_number = zone_number
        self.buff = buff

        # find start and end dates
        self.start_date = start_date
        self.end_date = end_date

        self. wy_start = wy_start

        self.fmt_date = '%Y%m%d'

        self.directory = directory
        #out_dir = './sim_files_grib'
        self.out_dir = out_dir

        # wind ninja inputs
        self.wn_topo = wn_topo
        self.wn_topo_prj = wn_topo_prj
        self.wn_cfg = os.path.abspath(wn_cfg)
        # prefix that wind ninja will use in the file naming convention
        self.wn_prefix = os.path.splitext(os.path.basename(self.wn_topo))[0]
        self.nthreads = nthreads

        # get info about model domain
        self.ts = get_topo_stats(self.fp_dem)
        self.x1 = self.ts['x']
        self.y1 = self.ts['y']
        self.dxy = dxy

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
                    'time_zone'                       : 'Europe/London',
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
        print('Creating file {}'.format(self.wn_cfg))
        with open(self.wn_cfg, 'w') as f:
            for k,v in base_cfg.items():
                f.write('{} = {}\n'.format(k,v))

    def run_wind_ninja(self):
        """
        Create the command line call to run the WindNinja_cli

        """
        action = 'WindNinja_cli {}'.format(self.wn_cfg)

        print('Running {}'.format(action))
        s = Popen(action, shell=True,stdout=PIPE)

        while True:
            line = s.stdout.readline().decode()
            print(line)
            if not line:
                break
        #s.wait()

    def run_katana(self):
        """

        """

        # create the new grib files
        date_list, num_list = create_new_grib(self.start_date, self.end_date,
                                              self.directory, self.out_dir,
                                              self.x1, self.y1,
                                              zone_letter=self.zone_letter,
                                              zone_number=self.zone_number,
                                              buff=self.buff)

        print(date_list)
        # make config, run wind ninja, make netcdf
        for idd, day in enumerate(date_list):
            if num_list[idd] > 0:
                out_dir_day = os.path.join(self.out_dir,
                                           'data{}'.format(day.strftime(self.fmt_date)))
                out_dir_wn = os.path.join(out_dir_day,
                                           'hrrr.{}'.format(day.strftime(self.fmt_date)))
                if not os.path.isdir(out_dir_day):
                    os.makedirs(out_dir_day)

                # run WindNinja_cli
                self.make_wn_cfg(out_dir_wn, self.wn_topo, num_list[idd])

                self.run_wind_ninja()

                # # convert that day to netcdf
                # convert_wind_ninja(out_dir_day, self.ts, self.wn_prefix,
                #                    self.wy_start, dxy=self.dxy)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Provide some logging info about when AWSM was closed
        """

        print('Katana closed --> %s' % datetime.now())
