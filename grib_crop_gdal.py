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
from smrf.framework.model_framework import SMRF
from awsm.data.topo import get_topo_stats
import utm
#import subprocess
from subprocess import Popen, PIPE

def grib_to_geotiff(fp_in, fp_out, x, y, buff=1500, prjsrs='EPSG:26911'):
    """
    Function to write 4 bands from grib2 to geotiff and crop domain
    inputs:
            fp_in: grib file path
            fp_out: geotiff file path
            x: x coords in utm of new domain
            y: y coords in utm of new domain
            buff: buffer in meters for buffering domain
            prjsrs: assuming UTM 11, extents of cropped domain
    """
    action = 'gdal_translate -projwin_srs {} -projwin {} {} {} {} \
              -b 9 -b 10 -b 66 -b 101  {} {}\
              '.format(prjsrs,
                       np.min(x) - buff, np.max(y) + buff,
                       np.max(x) + buff, np.min(y) - buff,
                       fp_in, fp_out)

    print('Running command [{}]'.format(action))
    s = Popen(action, shell=True,stdout=PIPE)
    s.wait()


cfg = "./test.ini"
fp_in = 'test.grib2'
fp_out = 'new.tif'

# initialize smrf
s = SMRF(cfg)

# calculate bbox based off of smrf params
zone_number = s.config['gridded']['zone_number']

u = utm.from_latlon(s.config['topo']['basin_lat'],
                    s.config['topo']['basin_lon'],
                    zone_number)
use_zone_number = u[2]
use_zone_letter = u[3]

ts = get_topo_stats(s.config['topo']['dem'], filetype='ipw')
x = ts['x']
y = ts['y']


####Notes####
"""
Create list of files based on input dates here. Run through files and
create matching tiffs. Then create netcdf file from all of the tiffs
"""

grib_to_geotiff(fp_in, fp_out, x, y, buff=1500, prjsrs='EPSG:26911')

# ur = np.array(utm.to_latlon(np.max(x), np.max(y), use_zone_number, use_zone_letter))
# ll = np.array(utm.to_latlon(np.min(x), np.min(y), use_zone_number, use_zone_letter))
#
# buff = 0.1 # buffer of bounding box in degrees
# ur += buff
# ll -= buff
# bbox = np.append(np.flipud(ll), np.flipud(ur))
#
# dates = '20180722'
# path_hrrr = '/home/micahsandusky/hrrr_sample/'
# path1 = 'hrrr.{}/'.format(dates)
# files = 'hrrr.t{:02d}z.wrfsfcf01.grib2'
#
# #fp_open = os.path.join('./tmp_hrrr/',files)
# fp_open = os.path.join('./tmp_hrrr/new.grib2')
#
# fp ='/home/micahsandusky/hrrr_sample/test.grib2'

# gdal_translate -of netCDF -projwin_srs EPSG:26911 -projwin 259416.9 4179136.1 353117.1 4096335.9  test.grib2 new.nc
# EPSG:26911


# action = 'gdalwarp -te_srs -of GRIB -te {} {} {} {}'
# action = action.format(np.min(x)-buff, np.min(y)-buff,
#                        np.max(x)+buff, np.max(y)+buff)

#print(action)
