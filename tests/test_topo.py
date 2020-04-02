import netCDF4 as nc
import numpy as np
import logging
import unittest
import os

from katana.get_topo import netcdf_dem_to_ascii


class TestTopo(unittest.TestCase):

    def test_topo(self):
        """Check each hour against gold standard
        """

        topo_in = 'tests/RME/topo/topo.nc'
        topo_out = 'tests/RME/output/topo.asc'

        logger = logging.getLogger(__name__)
        netcdf_dem_to_ascii(topo_in, topo_out, logger)

        nt = nc.Dataset(topo_in)
        na = np.loadtxt(topo_out, skiprows=6)

        self.assertTrue(np.array_equal(nt.variables['dem'][:], na))

        nt.close()
        os.remove(topo_out)
