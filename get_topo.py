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

def netcdf_dem_to_ascii(fp_nc, fp_asc):
    """
    Write a geotagged ascii dem for use with WindNinja

    Args:
        fp_nc:      file path to netcdf
        fp_asc:     file path to output ascii file. The .prj file will have
                    the same name

    Returns:
        Writes the ascii and prj files

    """
    # check if files exist first
    if os.path.exist(fp_asc):
        print('{} already exists, not creating again'.format(fp_asc))

    # if not, make the files
    else:
        fillval = -9999
        # get the prj file name
        asc_dir = os.path.dirname(fp_asc)
        bn = os.path.splitext(os.path.basename(fp_asc))[0]
        fp_prj = os.path.join(asc_dir, bn+'.prj')

        # get the netcdf
        ds = Dataset(fp_nc, 'r')
        dem = ds.variables['dem'][:]
        # flip dem since we are now indexing from the bottom left
        dem = np.flipud(dem)

        # create header for projection
        gridmap = ds.variables['dem'].grid_mapping
        prj_head = ds.variables[gridmap].spatial_ref

        # close the netcdf
        ds.close()

        # get the projection info
        ts = get_topo_stats(fp_nc)

        cell_size = np.abs(ts['dv'])
        # write the header
        asc_head = "ncols {}\nnrows {}\nxllcorner {}\nyllcorner {}\ncellsize {}\nNODATA_value {}"
        asc_head = asc_head.format(ts['nx'], ts['ny'],
                                   np.min(ts['x'])-cell_size/2.0,
                                   np.min(ts['y'])-cell_size/2.0,
                                   np.abs(ts['dv']),
                                   fillval)


        # prj_head = "Projection {}\nZone {}\nDatum {}\nZunits {}\nUnits {}\nSpheroid {}\nXshift {}\nYshift {}\nParamters"
        # prj_head = prj_head.format('UTM', 11, 'NAD83', 'METERS', 'METERS', 'WGS84',
        #                            0.0, 0.0)


        # write files
        np.savetxt(fp_asc, dem, header=asc_head, comments='')

        # write prj
        with open(fp_prj, 'w') as prj_file:
            prj_file.write(prj_head)
