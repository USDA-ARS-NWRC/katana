import logging
import os
from copy import deepcopy
from datetime import datetime

from katana import utils
from katana.wind_ninja import WindNinja


class WRFout():

    def __init__(self, config, topo):
        """Init the WRFout class

        WRFout prepares and runs WindNinja for a single wrfout file.
        Unlike NomadsHRRR where there can be multiple files in a
        directory, WRFout has been designed to just take a single
        file that has multiple time steps contained within it.

        Arguments:
            config {dict} -- dictionary of configuration options
            topo {Topo class} -- katana.data.topo.Topo class instance
        """

        self._logger = logging.getLogger(__name__)

        self.config = config
        self.topo = topo

        self.wrf_filename = self.config['input']['wrf_filename']

        self.start_date = self.config['time']['start_date']
        self.end_date = self.config['time']['end_date']
        self.fmt_date = '%Y%m%d'

        # create an hourly time step between the start date and end date
        self.date_list = utils.daterange(self.start_date, self.end_date)

        # create a daily list between the start and end date
        self.day_list = utils.daylist(self.start_date, self.end_date)

        self.out_dir = self.config['output']['out_location']

        self._logger.debug('WRFout initialized')

    def initialize_data(self):
        """Initialize the data if needed
        """
        pass

    def run(self):
        """Run the WindNinja simulation for WRFout
        """

        # make config, run wind ninja, make netcdf
        self._logger.info(
            'Running WindNinja for WRF file {}'.format(self.wrf_filename))

        start_time = datetime.now()

        if len(self.day_list) == 1:
            out_dir_day = os.path.join(self.out_dir,
                                       'data{}'.format(
                                           self.day_list[0].strftime(
                                               self.fmt_date)),
                                       'wind_ninja_data')
        else:
            # The file is split up over days
            # Therefore will have to write to a temporary directory
            # and sort the files after WindNinja runs
            out_dir_day = os.path.join(self.out_dir, 'tmp')

            # make output folder if it doesn't exist
        if not os.path.isdir(out_dir_day):
            os.makedirs(out_dir_day)

        # run WindNinja_cli
        wn_cfg = deepcopy(self.config['wind_ninja'])
        wn_cfg['forecast_filename'] = self.wrf_filename
        wn_cfg['elevation_file'] = self.topo.windninja_topo
        wn_cfg['output_path'] = out_dir_day

        wn = WindNinja(
            wn_cfg,
            self.config['output']['wn_cfg'])
        wn.run_wind_ninja()

        telapsed = datetime.now() - start_time
        self._logger.debug('Total elapsed time for WRFout: {} sec'.format(
            telapsed.total_seconds()))
