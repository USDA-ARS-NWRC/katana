# -*- coding: utf-8 -*-

import os

# super sneaky inicheck thinger
from . import utils  # noqa

__version__ = '0.3.2'

__core_config__ = os.path.abspath(
    os.path.dirname(__file__) + '/CoreConfig.ini')
__recipes__ = os.path.abspath(os.path.dirname(__file__) + '/recipes.ini')
__config_checkers__ = 'utils'

# from . import framework
# from . import get_topo
# from . import grib_crop_wgrib2
