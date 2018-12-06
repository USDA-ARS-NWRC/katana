from datetime import datetime
import argparse
import numpy as np
import pandas as pd
from subprocess import Popen, PIPE
import re

def sample_hrrr_grib2(fp_grib, lat, lon, vars):
    '''
    Use wgrib2 cli to sample variables from a grib2 file at a certain lat and lon

    Args:
        fp_grib:    File pointer to grib2 file
        lat:        lat of point
        lon:        lon of point
        vars:       List of strings matching variables to sample

    Returns:
        vals:       list of values in same order as vars
    '''

    #vars are 2m air temp and 1 hour accm precip
    var_maps = {'air_temp': 'TMP:2 m', 'precip_intensity': 'APCP:surface'}
    vals = {}
    # construct command line argument

    for k in vars:
        action = 'wgrib2  {} '.format(fp_grib)
        action += ' -match "{}" '.format(var_maps[k])
        action += ' -ncpu 1 -s -lon {} {}'.format(lon, lat)

        print('\n\nTrying {}\n'.format(action))
        s = Popen(action, shell=True, stdout=PIPE, stderr=PIPE)
        while True:
            line = s.stdout.readline().decode()
            eline = s.stderr.readline().decode()
            if not line:
                break

            if "FATAL" in eline:
                raise ValueError('Error in wgrib2: \n{}'.format(eline))

            # find the val, lon, lat
            val = float(re.search('val=(.+?)$', line).group(1))
            real_lon = float(re.search('lon=(.+?),', line).group(1))
            real_lat = float(re.search('lat=(.+?),', line).group(1))

            # convert air temp to celcius
            if k == 'air_temp':
                val -= 273.15

            vals[k] = val
            vals['hrrr_lat'] = real_lat
            vals['hrrr_lon'] = real_lon

    return vals


# example outputs
# 66:42877129:d=2018093023:TMP:2 m above ground:1 hour fcst::lon=249.011818,lat=38.998487,val=298.094:lon=254.993808,lat=32.987014,val=300.844
# 71:49027025:d=2018093023:UGRD:10 m above ground:1 hour fcst::lon=249.011818,lat=38.998487,val=7.68041:lon=254.993808,lat=32.987014,val=-4.75709
# 72:50131800:d=2018093023:VGRD:10 m above ground:1 hour fcst::lon=249.011818,lat=38.998487,val=4.10929:lon=254.993808,lat=32.987014,val=4.79679
# 101:66538467:d=2018093023:TCDC:entire atmosphere:1 hour fcst::lon=249.011818,lat=38.998487,val=0:lon=254.993808,lat=32.987014,val=0
