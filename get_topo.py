import numpy as np
from netCDF4 import Dataset
import os

def get_topo_stats(fp, filetype='netcdf'):
    """
    Get stats about topo from the topo file
    Returns:
        ts - dictionary of topo header data
    """

    fp = os.path.abspath(fp)

    ts = {}

    if filetype == 'netcdf':
        ds = Dataset(fp, 'r')
        ts['units'] = ds.variables['y'].units
        y = ds.variables['y'][:]
        x = ds.variables['x'][:]
        ts['nx'] = len(x)
        ts['ny'] = len(y)
        ts['du'] = y[1] - y[0]
        ts['dv'] = x[1] - x[0]
        ts['v'] = x[0]
        ts['u'] = y[0]
        ts['x'] = x
        ts['y'] = y
        ds.close()

    elif filetype == 'ascii':
        header = {}
        ff = open(fp, 'r')
        for idl, line in enumerate(ff):
            tmp_line = line.strip().split()
            header[tmp_line[0]] = tmp_line[1]
            if idl >= 5:
                break
        ff.close()

        ts['nx'] = int(header['ncols'])
        ts['ny'] = int(header['nrows'])
        ts['du'] = float(header['cellsize'])
        ts['dv'] = float(header['cellsize'])
        ts['u'] = float(header['yllcorner'])
        ts['v'] = float(header['xllcorner'])

        ts['x'] = ts['v'] + ts['dv']*np.arange(ts['nx'])
        ts['y'] = ts['u'] + ts['du']*np.arange(ts['ny'])

    else:
        raise IOError('Not a supported topo filetype')

    return ts
