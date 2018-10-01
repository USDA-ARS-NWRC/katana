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
import os

from get_topo import get_topo_stats
from grib_crop_wgrib2 import create_new_grib
from windninja_to_nc import convert_wind_ninja


class Katana():
    """

    """
    def __init__():
        self.fp_dem = 'tuolx_50m_topo.nc'
        self.zone_letter = 'N'
        self.zone_number = 11
        self.buff = 6000

        # find start and end dates
        self.start_date = pd.to_datetime('2018-09-20 00:00')
        self.end_date = pd.to_datetime('2018-09-21 00:00')

        self. wy_start = pd.to_datetime('2017-10-01 00:00')

        self.directory = './tmp_hrrr'
        #out_dir = './sim_files_grib'
        self.out_dir = '/data/data'

        # wind ninja inputs
        self.wn_topo = './tuol.asc'
        self.wn_topo_prj = './tuol.prj'
        # prefix that wind ninja will use in the file naming convention
        self.wn_prefix = os.path.splitext(os.path.basename(self.wn_topo))

        # get info about model domain
        self.ts = get_topo_stats(self.fp_dem)
        self.x1 = self.ts['x']
        self.y1 = self.ts['y']


    def run_katana(self):

        # create the new grib files
        date_list, fmt_date = create_new_grib(self.start_date, self.end_date,
                                              self.directory, self.out_dir,
                                              self.x1, self.y1,
                                              zone_letter=self.zone_letter,
                                              zone_number=self.zone_number,
                                              buff=self.buff)


        # make netcdf for each day from ascii outputs
        for idd, day in enumerate(date_list):
            out_dir_day = os.path.join(self.outdir,
                                       'hrrr.{}'.format(day.strftime(fmt_date)))
            # run WindNinja_cli
            # run_wind_ninja()

            # convert that day to netcdf
            # convert_wind_ninja(out_dir_day, self.ts, self.wn_prefix,
            #                    self.wy_start)
