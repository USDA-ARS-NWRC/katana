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
from get_topo import get_topo_stats
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

    # create directory if needed
    if not os.path.isdir(dir1):
        os.makedirs(dir1)

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

# Inputs
fp_dem = 'tuolx_50m_topo.nc'
cfg = "./test_tuol.ini"
zone_letter = 'N'
zone_number = 11

start_date = pd.to_datetime('2018-09-20 00:00')
end_date = pd.to_datetime('2018-09-21 00:00')
directory = './tmp_hrrr'
out_dir = './sim_files_grib'

# out_dir = '/home/micahsandusky/Documents/Code/test_windninja/NOMADS-HRRR-CONUS-3-KM-tuol.asc/'

# get list of days to grab
fmt = '%Y%m%d'
dtt = end_date - start_date
ndays = dtt.days
date_list = [start_date + datetime.timedelta(days=x) for x in range(0, ndays+1)]

ts = get_topo_stats(fp_dem)
x1 = ts['x']
y1 = ts['y']

for idt, dt in enumerate(date_list[:1]):
    # get files
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
