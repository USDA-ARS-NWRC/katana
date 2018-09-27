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
import matplotlib.pyplot as plt
from smrf.framework.model_framework import SMRF
from awsm.data.topo import get_topo_stats
import utm
#import subprocess
from subprocess import Popen, PIPE
import os
import pandas as pd
import datetime
import netCDF4 as nc
import glob


# problem
"""
Have to follow naming convention for hrrr, so run daily
"""

def grib_to_sgrib(fp_in, out_dir, file_dt, x, y, buff=1500, zone_letter='N', zone_number=11):
    """
    Function to write 4 bands from grib2 to cropped grib2

    Args:
            fp_in: grib file path
            out_dir:
            file_dt
            x: x coords in utm of new domain
            y: y coords in utm of new domain
            buff: buffer in meters for buffering domain
            zone_letter:
            zone_number:
    """
    # date format for files
    #fmt = '%Y%m%d-%H-%M'
    fmt1 = '%Y%m%d'
    fmt2 = '%H'
    dir1 = os.path.join(out_dir, 'hrrr.{}'.format(file_dt.strftime(fmt1)))

    # make file names
    tmp_grib = os.path.join(dir1, 'tmp.grib2')
    fp_out = os.path.join(dir1,
                          'hrrr.t00z.wrfsfcf{}.grib2'.format(file_dt.strftime(fmt2)))

    # find bounds (to_latlon returns (LATITUDE, LONGITUDE).)
    ur = np.array(utm.to_latlon(np.max(x)+buff, np.max(y)+buff, zone_number, zone_letter))
    ll = np.array(utm.to_latlon(np.min(x)-buff, np.min(y)-buff, zone_number, zone_letter))
    # get latlon bounds
    lats = ll[0]
    latn = ur[0]
    lonw = ll[1]
    lone = ur[1]

    # call to crop grid
    action = 'wgrib2 {} -small_grib {}:{} {}:{} {}'.format(fp_in, lonw, lone,
                                                           lats, latn, tmp_grib)

    # call to grab correct variables
    action2 = "wgrib2 {} -match '^(66|71|72|101):' -GRIB {}".format(tmp_grib,
                                                                    fp_out)

    # run commands
    print('Running command {}'.format(action))
    s = Popen(action, shell=True,stdout=PIPE)
    s.wait()

    print('Running command {}'.format(action2))
    s = Popen(action2, shell=True,stdout=PIPE)
    s.wait()

    os.remove(tmp_grib)


cfg = "./test_tuol.ini"
fp_in = 'test.grib2'
zone_letter = 'N'
zone_number = 11

#out_dir = './sim_files_grib/'
#out_dir = '/home/micahsandusky/Documents/Code/test_windninja/sim_files_grib'
out_dir = '/home/micahsandusky/Documents/Code/test_windninja/NOMADS-HRRR-CONUS-3-KM-tuol.asc/'
fp_dem = 'tuolx_50m_topo.nc'
start_date = pd.to_datetime('2018-09-20 00:00')
end_date = pd.to_datetime('2018-09-21 00:00')
directory = './tmp_hrrr'

# get list of days to grab
fmt = '%Y%m%d'
dtt = end_date - start_date
ndays = dtt.days
#days_1 = datetime.timedelta(days=1)
date_list = [start_date + datetime.timedelta(days=x) for x in range(0, ndays+1)]

#dt = pd.to_datetime(date_list)[0].strftime(fmt))
#fps = ['tmp_hrrr/hrrr.20180920/hrrr.t00z.wrfsfcf01.grib2', 'tmp_hrrr/hrrr.20180920/hrrr.t00z.wrfsfcf01.grib2']

ts = get_topo_stats(fp_dem)#, filetype='ipw')
x1 = ts['x']
y1 = ts['y']

#initialize_hrrr_nc(fp_out)
#print(date_list)
is_initalized = False
for idt, dt in enumerate(date_list[:1]):
    # get files
    #fps = ['tmp_hrrr/hrrr.20180920/hrrr.t00z.wrfsfcf01.grib2', 'tmp_hrrr/hrrr.20180920/hrrr.t00z.wrfsfcf01.grib2']
    hrrr_dir = os.path.join(directory,
                            'hrrr.{}/hrrr.t*.grib2'.format(dt.strftime(fmt)))
    fps = glob.glob(hrrr_dir)
    # write and read new netcdfs
    for idf, fp in enumerate(fps):
        bn = os.path.basename(fp)
        # find hours from start of day
        add_hrs = int(bn[6:8]) + int(bn[17:19])
        file_time = pd.to_datetime(dt + datetime.timedelta(hours=add_hrs))

        if file_time >= start_date and file_time <= end_date:
            # convert grib to temp nc
            grib_to_sgrib(fp, out_dir, file_time, x1, y1, buff=9000,
                          zone_letter=zone_letter, zone_number=zone_number)

        else:
            print('{} is not in date range'.format(file_time))

"""
 - loop through days and file
 - initialize time series netcdf
 - parse date
 - write temp netcdf
 - read in netcdf and store in time series netcdf
 - delete temp netcdf

"""
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


# extra stuff
# double reftime2(time2)
# 	standard_name = "forecast_reference_time"
# 	long_name = "GRIB reference time"
# 	calendar = "proleptic_gregorian"
# 	units = "Hour since 2018-09-06T00:00:00Z"
# 	_CoordinateAxisType = "RunTime"
# double time2(time2)
# 	units = "Hour since 2018-09-06T00:00:00Z"
# 	standard_name = "time"
# 	long_name = "GRIB forecast or observation time"
# 	calendar = "proleptic_gregorian"
# 	bounds = "time2_bounds"
# 	_CoordinateAxisType = "Time"
# float height_above_ground(height_above_ground)
# 	units = "m"
# 	long_name = "Specified height level above ground"
# 	positive = "up"
# 	Grib_level_type = 103
# 	datum = "ground"
# 	_CoordinateAxisType = "Height"
# 	_CoordinateZisPositive = "up"
# float y(y)
# 	standard_name = "projection_y_coordinate"
# 	units = "km"
# 	_CoordinateAxisType = "GeoY"
# float x(x)
# 	standard_name = "projection_x_coordinate"
# 	units = "km"
# 	_CoordinateAxisType = "GeoX"
# LambertConformal_Projection
# 	grid_mapping_name = "lambert_conformal_conic"
# 	latitude_of_projection_origin .
# 	longitude_of_central_meridian = 265.
# 	standard_parallel = 25.
# 	earth_radius = 6371200.
# 	_CoordinateTransformType = "Projection"
# 	_CoordinateAxisTypes = "GeoX GeoY"
# double reftime(time)
# 	standard_name = "forecast_reference_time"
# 	long_name = "GRIB reference time"
# 	calendar = "proleptic_gregorian"
# 	units = "Hour since 2018-09-06T00:00:00Z"
# 	_CoordinateAxisType = "RunTime"
# double time(time)
# 	units = "Hour since 2018-09-06T00:00:00Z"
# 	standard_name = "time"
# 	long_name = "GRIB forecast or observation time"
# 	calendar = "proleptic_gregorian"
# 	_CoordinateAxisType = "Time"
# float height_above_ground1(height_above_ground1)
# 	units = "m"
# 	long_name = "Specified height level above ground"
# 	positive = "up"
# 	Grib_level_type = 103
# 	datum = "ground"
# 	_CoordinateAxisType = "Height"
# 	_CoordinateZisPositive = "up"
# double reftime1(time1)
# 	standard_name = "forecast_reference_time"
# 	long_name = "GRIB reference time"
# 	calendar = "proleptic_gregorian"
# 	units = "Hour since 2018-09-06T00:00:00Z"
# 	_CoordinateAxisType = "RunTime"
# double time1(time1)
# 	units = "Hour since 2018-09-06T00:00:00Z"
# 	standard_name = "time"
# 	long_name = "GRIB forecast or observation time"
# 	calendar = "proleptic_gregorian"
# 	bounds = "time1_bounds"
# 	_CoordinateAxisType = "Time"
