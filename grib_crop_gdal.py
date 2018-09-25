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


def grib_to_nc(fp_in, fp_out, x, y, buff=1500, prjsrs='EPSG:26911'):
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
    action = 'gdal_translate -of netCDF -projwin_srs {} -projwin {} {} {} {} \
              -b 71 -b 72 -b 66 -b 101  {} {}\
              '.format(prjsrs,
                       np.min(x) - buff, np.max(y) + buff,
                       np.max(x) + buff, np.min(y) - buff,
                       fp_in, fp_out)

    print('Running command [{}]'.format(action))
    s = Popen(action, shell=True,stdout=PIPE)
    s.wait()


def initialize_hrrr_nc(fp_out, start_date, x, y):
    """
    Initialize the netcdf to store the hrrr forcing data

    Args:


    """
    fmt = '%Y-%m-%d %H:%M:%S'
    # chunk size
    cs = (6, 10, 10)

    # store ref dims for each variables
    variable_dims = {
                      'Maximum_temperature_height_above_ground_12_Hour_Maximum':('time2', 'height_above_ground', 'y', 'x'),
                      'Minimum_temperature_height_above_ground_12_Hour_Minimum':('time1', 'height_above_ground', 'y', 'x'),
                      'Total_cloud_cover_entire_atmosphere_single_layer_layer':('time', 'y', 'x'),
                      'Wind_direction_from_which_blowing_height_above_ground':('time', 'height_above_ground1', 'y', 'x'),
                      'Wind_speed_height_above_ground':('time', 'height_above_ground1', 'y', 'x')
                      }

    # store attributes for each variable
    variable_dict = {
        'Maximum_temperature_height_above_ground_12_Hour_Maximum' : {
    		'long_name' : "Maximum temperature (12_Hour Maximum) @ Specified height level above ground",
    		'units' : "K",
    		#'abbreviation' : "TMAX"
    		# 'missing_value' : NaNf
    		# 'grid_mapping' : "LambertConformal_Projection"
    		# 'coordinates' : "reftime2 time2 height_above_ground y x "
    		# 'Grib_Statistical_Interval_Type' : "Maximum"
    		# 'cell_methods' : "time2: maximum"
    		# 'Grib_Variable_Id' : "VAR_0-0-4_L103_I12_Hour_S2"
    		# 'Grib2_Parameter' : 0, 0, 4
    		# 'Grib2_Parameter_Discipline' : "Meteorological products",
    		# 'Grib2_Parameter_Category' : "Temperature",
    		# 'Grib2_Parameter_Name' : "Maximum temperature",
    		# 'Grib2_Level_Type' : 103,
    		# 'Grib2_Level_Desc' : "Specified height level above ground",
    		# 'Grib2_Generating_Process_Type' : "Forecast"
            },
    	'Minimum_temperature_height_above_ground_12_Hour_Minimum' : {
    		'long_name' : "Minimum temperature (12_Hour Minimum) @ Specified height level above ground",
    		'units' : "K",
    		'abbreviation' : "TMIN",
    		# missing_value = NaNf
    		# grid_mapping = "LambertConformal_Projection"
    		# coordinates = "reftime1 time1 height_above_ground y x "
    		# Grib_Statistical_Interval_Type = "Minimum"
    		# cell_methods = "time1: minimum"
    		# Grib_Variable_Id = "VAR_0-0-5_L103_I12_Hour_S3"
    		# Grib2_Parameter = 0, 0, 5
    		# Grib2_Parameter_Discipline = "Meteorological products"
    		# Grib2_Parameter_Category = "Temperature"
    		# Grib2_Parameter_Name = "Minimum temperature"
    		# Grib2_Level_Type = 103
    		# Grib2_Level_Desc = "Specified height level above ground"
    		# Grib2_Generating_Process_Type = "Forecast"
            },
    	'Total_cloud_cover_entire_atmosphere_single_layer_layer' : {
    		'long_name' : "Total cloud cover @ Entire atmosphere layer layer",
    		'units' : "%",
    		# abbreviation = "TCDC"
    		# missing_value = NaNf
    		# grid_mapping = "LambertConformal_Projection"
    		# coordinates = "reftime time y x "
    		# Grib_Variable_Id = "VAR_0-6-1_L200_layer"
    		# Grib2_Parameter = 0, 6, 1
    		# Grib2_Parameter_Discipline = "Meteorological products"
    		# Grib2_Parameter_Category = "Cloud"
    		# Grib2_Parameter_Name = "Total cloud cover"
    		# Grib2_Level_Type = 200
    		# Grib2_Level_Desc = "Entire atmosphere layer"
    		# Grib2_Generating_Process_Type = "Forecast"
            },
    	'Wind_direction_from_which_blowing_height_above_ground' : {
    		'long_name' : "Wind direction (from which blowing) @ Specified height level above ground",
    		'units' : "degree_true",
    		# abbreviation = "WDIR"
    		# missing_value = NaNf
    		# grid_mapping = "LambertConformal_Projection"
    		# coordinates = "reftime time height_above_ground1 y x "
    		# Grib_Variable_Id = "VAR_0-2-0_L103"
    		# Grib2_Parameter = 0, 2, 0
    		# Grib2_Parameter_Discipline = "Meteorological products"
    		# Grib2_Parameter_Category = "Momentum"
    		# Grib2_Parameter_Name = "Wind direction (from which blowing)"
    		# Grib2_Level_Type = 103
    		# Grib2_Level_Desc = "Specified height level above ground"
    		# Grib2_Generating_Process_Type = "Forecast"
            },
    	 'Wind_speed_height_above_ground' : {
    		'long_name' : "Wind speed @ Specified height level above ground",
    		'units' : "m/s",
    		# abbreviation = "WIND"
    		# missing_value = NaNf
    		# grid_mapping = "LambertConformal_Projection"
    		# coordinates = "reftime time height_above_ground1 y x "
    		# Grib_Variable_Id = "VAR_0-2-1_L103"
    		# Grib2_Parameter = 0, 2, 1
    		# Grib2_Parameter_Discipline = "Meteorological products"
    		# Grib2_Parameter_Category = "Momentum"
    		# Grib2_Parameter_Name = "Wind speed"
    		# Grib2_Level_Type = 103
    		# Grib2_Level_Desc = "Specified height level above ground"
    		# Grib2_Generating_Process_Type = "Forecast"
            }
        }

    if os.path.isfile(fp_out):
        print('Opening {}, data may be overwritten!'.format(fp_out))
        ds = nc.Dataset(fp_out, 'a')
        h = '[{}] Data added or updated'.format(
            datetime.datetime.now().strftime(fmt))
        setattr(ds, 'last_modified', h)

    else:
        ds = nc.Dataset(fp_out, 'w')

        # create the dimensions
        ds.createDimension('time', None)
        ds.createDimension('time1', None)
        ds.createDimension('time2', None)
        ds.createDimension('height_above_ground', 1)
        ds.createDimension('height_above_ground1', 1)
        ds.createDimension('y', len(y))
        ds.createDimension('x', len(x))

        # create some variables
        ds.createVariable('time', 'f', 'time')
        ds.createVariable('time1', 'f', 'time1')
        ds.createVariable('time2', 'f', 'time2')
        # ds.createVariable('reftime', 'f', 'time')
        # ds.createVariable('reftime1', 'f', 'time1')
        # ds.createVariable('reftime2', 'f', 'time2')
        ds.createVariable('height_above_ground', 'f', 'height_above_ground')
        ds.createVariable('height_above_ground1', 'f', 'height_above_ground1')
        ds.createVariable('y', 'f', 'y')
        ds.createVariable('x', 'f', 'x')

        # setattr(em.variables['time'], 'units', 'hours since %s' % options['time']['start_date'])
        setattr(ds.variables['time'], 'units', 'hours since %s' % start_date)
        setattr(ds.variables['time'], 'calendar', 'proleptic_gregorian')
        setattr(ds.variables['time1'], 'units', 'hours since %s' % start_date)
        setattr(ds.variables['time1'], 'calendar', 'proleptic_gregorian')
        setattr(ds.variables['time2'], 'units', 'hours since %s' % start_date)
        setattr(ds.variables['time2'], 'calendar', 'proleptic_gregorian')
        # setattr(ds.variables['reftime'], 'units', 'hours since %s' % start_date)
        # setattr(ds.variables['reftime'], 'calendar', 'proleptic_gregorian')
        # setattr(ds.variables['reftime1'], 'units', 'hours since %s' % start_date)
        # setattr(ds.variables['reftime1'], 'calendar', 'proleptic_gregorian')
        # setattr(ds.variables['reftime2'], 'units', 'hours since %s' % start_date)
        # setattr(ds.variables['reftime2'], 'calendar', 'proleptic_gregorian')

        setattr(ds.variables['x'], 'units', 'km')
        setattr(ds.variables['y'], 'units', 'km')

        # change to km?
        ds.variables['y'][:] = y / 1000.0
        ds.variables['x'][:] = x / 1000.0

        # set attributes and dimensions for variables
        for v, f in variable_dict.items():
            ds.createVariable(v, 'f', variable_dims[v], chunksizes=cs)
            for key, val in f.items():
                setattr(ds.variables[v], key, val)

        # # define some global attributes
        # ds.setncattr_string('Conventions', 'CF-1.6')
        # ds.setncattr_string('dateCreated', datetime.now().strftime(self.fmt))
        # ds.setncattr_string('created_with', 'Created with awsm {} and smrf {}'.format(awsm_version, smrf_version))
        # ds.setncattr_string('history', '[{}] Create netCDF4 file'.format(datetime.now().strftime(fmt)))
        # ds.setncattr_string('institution',
        #         'USDA Agricultural Research Service, Northwest Watershed Research Center')

    # save the open dataset so we can write to it
    return ds

def write_data_nc(ds, dt, max_air, min_air, wind_u, wind_v, cloud_cover, add_hrs):
    """
    write_data to netcdf
    Args:

    """
    time_list = ['time', 'time1', 'time2']
    # now find the correct index
    # the current time integer
    times = ds.variables['time']
    # convert to index
    t = nc.date2num(dt.replace(tzinfo=None), times.units, times.calendar)
    # find index in context of file
    if len(times) != 0:
        index = np.where(times[:] == t)[0]
        if index.size == 0:
            index = len(times)
        else:
            index = index[0]
    else:
        index = len(times)

    # insert the time and data
    ds.variables['time'][index] = t
    ds.variables['Total_cloud_cover_entire_atmosphere_single_layer_layer'][index, :] = diff_z

    # calculate angle and magnitude

    wind_speed =
    wind_dir =

    ds.variables['Wind_direction_from_which_blowing_height_above_ground'][index, 0, :] = wind_dir
    ds.variables['Wind_speed_height_above_ground'][index, 0, :] = wind_speed

    # do the 12 hr part
    if add_hrs == 0 or add_hrs == 12:
        
        times1 = ds.variables['time1']
        # find index in context of file
        if len(times1) != 0:
            index = np.where(times1[:] == t)[0]
            if index.size == 0:
                index = len(times1)
            else:
                index = index[0]
        else:
            index = len(times1)
        # some time stuff
        self.detla_ds.variables['time1'][index] = t
        self.detla_ds.variables['time2'][index] = t
        # set variables
        ds.variables['Maximum_temperature_height_above_ground_12_Hour_Maximum'][index,0,:] = max_air
        ds.variables['Minimum_temperature_height_above_ground_12_Hour_Minimum'][index,0,:] = min_air

    ds.sync()


cfg = "./test_tuol.ini"
fp_in = 'test.grib2'
#fp_out = 'new.tif'
fp_out = 'new.nc'
fp_force = 'gribnc.nc'
fp_dem = 'tuolx_50m_topo.nc'
start_date = pd.to_datetime('2018-09-20 00:00')
end_date = pd.to_datetime('2018-09-21 23:00')
directory = './tmp_hrrr'

# get list of days to grab
fmt = '%Y%m%d'
dtt = end_date - start_date
ndays = dtt.days
days_1 = datetime.timedelta(days=1)
date_list = [start_date + datetime.timedelta(days=x) for x in range(0, ndays+1)]

#dt = pd.to_datetime(date_list)[0].strftime(fmt))
fps = ['tmp_hrrr/hrrr.20180920/hrrr.t00z.wrfsfcf01.grib2', 'tmp_hrrr/hrrr.20180920/hrrr.t00z.wrfsfcf01.grib2']

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
    print(fps)
    # write and read new netcdfs
    for idf, fp in enumerate(fps):
        bn = os.path.basename(fp)
        # find hours from start of day
        add_hrs = int(bn[6:8]) + int(bn[17:19])
        file_time = pd.to_datetime(dt + datetime.timedelta(hours=add_hrs))

        # magnitudes of min and max air
        max_air = None
        min_air = None
        # arrays of min and max air
        mna = None
        mxa = None

        if file_time >= start_date and file_time <= end_date:
            # convert grib to temp nc
            grib_to_nc(fp_in, fp_out, x1, y1, buff=30000)

            ds_temp = nc.Dataset(fp_out, 'r')

            if not is_initalized:
                x = ds_temp.variables['x'][:]
                y = ds_temp.variables['y'][:]
                print(x, y)
                is_initalized = True
                ds_force = initialize_hrrr_nc(fp_force, start_date, x, y)

            wind_u = ds_temp.variables['Band1'][:]
            wind_v = ds_temp.variables['Band2'][:]
            at = ds_temp.variables['Band3'][:] + 273.15
            cloud_cover = ds_temp.variables['Band4'][:]

            tmp_min_air = np.nanmin(air_temp)
            tmp_max_air = np.nanmax(air_temp)
            if max_air is None and min_air is None:
                min_air = tmp_min_air
                max_air = tmp_max_air
                mna = at
                mxa = at
            else:
                if tmp_min_air < min_air:
                    min_air = tmp_min_air
                    mna = at
                if tmp_max_air < max_air:
                    max_air = tmp_max_air
                    mxa = at

            # find the min and max for a 12 hr period
            write_data_nc(ds_force, file_time, mxa, mna,
                          wind_u, wind_v, cloud_cover, add_hrs)

            if add_hrs == 12 or add_hrs = 0:
                max_air = None
                min_air = None

            ds_temp.close()
            #os.remove(fp_out)

        else:
            print('{} is not in date range'.format(file_time))

    # close new dataset
    ds_force.close()




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
