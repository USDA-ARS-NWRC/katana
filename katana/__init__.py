# -*- coding: utf-8 -*-

__version__ = '0.3.1'

__core_config__ = os.path.abspath(os.path.dirname(__file__) + '/CoreConfig.ini')
__recipes__ = os.path.abspath(os.path.dirname(__file__) + '/recipes.ini')

from . import framework
from . import get_topo
from . import grib_crop_wgrib2
from . import utils
