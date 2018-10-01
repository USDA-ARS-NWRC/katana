import numpy as np
from matplotlib import pyplot as plt
import os
import pandas as pd
import netCDF4 as nc
from get_topo import get_topo_stats
import glob
import pytz
from datetime import datetime

'''
Read in our top file and write ascii dem to run WindNinja
'''


def create_nc(ts, wy_start, out_dir):
    # ========================================================================
    # NetCDF file
    # ========================================================================
    m = {}
    m['name'] = ['wind_speed']
    m['units'] = ['m/s']
    m['description'] = ['wind speed']

    netcdfFile = os.path.join(out_dir, 'wind_speed.nc')

    dimensions = ('time', 'y', 'x')
    ds = nc.Dataset(netcdfFile, 'w')

    # create the dimensions
    ds.createDimension('time', None)
    ds.createDimension('y', ts['ny'])
    ds.createDimension('x', ts['nx'])

    # create some variables
    ds.createVariable('time', 'f', dimensions[0])
    ds.createVariable('y', 'f', dimensions[1])
    ds.createVariable('x', 'f', dimensions[2])

    setattr(ds.variables['time'], 'units', 'hours since %s' % wy_start)
    setattr(ds.variables['time'], 'calendar', 'standard')
    setattr(ds.variables['time'], 'time_zone', 'UTC')
    ds.variables['x'][:] = ts['x']
    ds.variables['y'][:] = ts['y']

    # ds image
    for i, v in enumerate(m['name']):
        ds.createVariable(v, 'f', dimensions[:3], chunksizes=(24, 10, 10))
        setattr(ds.variables[v], 'units', m['units'][i])
        setattr(ds.variables[v], 'description', m['description'][i])

    return ds

def convert_wind_ninja(out_dir_day, ts, wn_prefix, wy_start):
    """

    Args:
        out_dir_day:    directory for output for the simulation day
        ts:             get_topo_stats dictionary
        wn_prefix:      prefix for WindNinja output files
        wy_start:       start date for water year in question

    Returns:
        

    """
    # initialize the netcdf file
    ds = create_nc(ts, wy_start, out_dir_day)
    # get the grid spacing
    dxy = int(np.abs(ts['dx']))

    # get the ascii files that need converted
    d = sorted(glob.glob(os.path.join(out_dir_day,'{}_*_{:d}_vel.asc'.format(wn_prefix, dxy))),
                                      key=os.path.getmtime)
    # sort the files by date time
    d.sort(key=lambda f: pd.to_datetime(os.path.basename(f).split('_')[1]+' '+os.path.basename(f).split('_')[2]))
    print(d)
    # put each timestep into netcdf
    j = 0
    for idf, f in enumerate(d):
        # get date from the file name
        dt = pd.to_datetime(os.path.basename(f).split('_')[1]+' '+os.path.basename(f).split('_')[2])

        ############# NEED #######
        # Need to look at time zone from WindNinja cfg and convert
        # back to UTC so that we are consistent with SMRF outputs
        ######### END NEED #######
        #tmpdate = dt.replace(tzinfo=pytz.timezone('UTC'))

        # get the data
        data = np.loadtxt(f, skiprows=6)
        # manipulate the data
        ############# NEED #######
        # Manipulate data to match SMRF grid if needed
        ######### END NEED #######
        data = data[:-1,:-1] * 0.447 #convert?

        # assign times
        nctimes = ds.variables['time']
        nct = nc.date2num(dt.replace(tzinfo=None), nctimes.units,
                          nctimes.calendar)
        # put in dataset
        ds.variables['time'][idf] = nct
        ds.variables['wind_speed'][idf, :] = data*mask
        ds.setncattr_string('last modified', datetime.now())
        # sync up the dataset
        ds.sync()

    ds.close()