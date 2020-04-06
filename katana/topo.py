import logging
import os

import numpy as np
from netCDF4 import Dataset


class Topo():
    """Class for working with and storing topo information
    """

    FILLVAL = -9999

    def __init__(self, config):
        """Init the topo class

        Arguments:
            config {dict} -- dictionary of configuration options
        """

        self._logger = logging.getLogger(__name__)

        self.config = config
        self.topo_filename = self.config['topo']['filename']
        self.zone_letter = self.config['topo']['zone_letter']
        self.zone_number = self.config['topo']['zone_number']

        # prefix that wind ninja will use in the file naming convention
        self.windninja_prefix = os.path.splitext(
            os.path.basename(self.topo_filename))[0]

        self.windnina_filenames = '{}{}'.format(
            self.windninja_prefix,
            self.config['topo']['wind_ninja_topo_suffix']
        )

        # write ascii dem for WindNinja
        dir_topo = os.path.dirname(self.topo_filename)
        self.windninja_topo = os.path.join(dir_topo, '{}.asc'.format(
            self.windnina_filenames
        ))

        self.windninja_topo_prj = os.path.join(dir_topo, '{}.prj'.format(
            self.windnina_filenames
        ))

        # get info about model domain
        self.get_topo_stats()
        self.x1 = self.topo_stats['x']
        self.y1 = self.topo_stats['y']

        # write new files
        self.netcdf_dem_to_ascii()

        self._logger.debug('Topo initialized')

    def netcdf_dem_to_ascii(self):
        """
        Write a geotagged ascii dem for use with WindNinja
        Writes the ascii and prj files

        Returns:
            None
        """

        # get the prj file name
        asc_dir = os.path.dirname(self.windninja_topo)
        bn = os.path.splitext(os.path.basename(self.windninja_topo))[0]
        fp_prj = os.path.join(asc_dir, bn+'.prj')

        # get the netcdf
        ds = Dataset(self.topo_filename, 'r')
        dem = ds.variables['dem'][:]

        # create header for projection
        if hasattr(ds.variables['dem'], 'grid_mapping'):
            gridmap = ds.variables['dem'].grid_mapping
            prj_head = ds.variables[gridmap].spatial_ref
        else:
            self._logger.error('No projection info in topo file')

        ds.close()

        cell_size = np.abs(self.topo_stats['dv'])
        # write the header
        asc_head = "ncols {}\nnrows {}\nxllcorner {}\nyllcorner \
            {}\ncellsize {}\nNODATA_value {}"
        asc_head = asc_head.format(
            self.topo_stats['nx'],
            self.topo_stats['ny'],
            np.min(self.topo_stats['x']) - cell_size/2.0,
            np.min(self.topo_stats['y']) - cell_size/2.0,
            np.abs(self.topo_stats['dv']),
            self.FILLVAL)

        # write files
        np.savetxt(self.windninja_topo, dem, header=asc_head, comments='')

        # write prj
        with open(fp_prj, 'w') as prj_file:
            prj_file.write(prj_head)

    def get_topo_stats(self):
        """
        Get stats about topo from the topo file
        Returns:
            ts - dictionary of topo header data
        """

        fp = os.path.abspath(self.topo_filename)

        ds = Dataset(fp, 'r')
        y = ds.variables['y'][:]
        x = ds.variables['x'][:]
        units = ds.variables['y'].units
        ds.close()

        ts = {}
        ts['units'] = units
        ts['nx'] = len(x)
        ts['ny'] = len(y)
        ts['du'] = y[1] - y[0]
        ts['dv'] = x[1] - x[0]
        ts['v'] = x[0]
        ts['u'] = y[0]
        ts['x'] = x
        ts['y'] = y

        self.topo_stats = ts
