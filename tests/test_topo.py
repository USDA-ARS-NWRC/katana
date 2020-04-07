import netCDF4 as nc
import numpy as np

from katana.topo import Topo
from tests.test_base import KatanaTestCase


class TestTopo(KatanaTestCase):

    def test_topo(self):
        """Check that the ascii topo is equal to the netcdf topo
        """

        t = Topo(self.base_config.cfg)

        nt = nc.Dataset(t.topo_filename)
        na = np.loadtxt(t.windninja_topo, skiprows=6)

        self.assertTrue(np.array_equal(nt.variables['dem'][:], na))

        nt.close()
