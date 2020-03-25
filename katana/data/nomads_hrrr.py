import os
from datetime import datetime
from copy import deepcopy
import logging

from katana.grib_crop_wgrib2 import create_new_grib
from katana.wind_ninja import WindNinja
from katana import utils


class NomadsHRRR():

    def __init__(self, config, topo):
        """Init the NomadsHRRR class

        Arguments:
            config {dict} -- dictionary of configuration options
            topo {Topo class} -- katana.data.topo.Topo class instance
        """

        self._logger = logging.getLogger(__name__)

        self.config = config
        self.topo = topo

        self.buffer = self.config['input']['hrrr_buffer']
        self.directory = self.config['input']['hrrr_directory']
        self.make_new_gribs = self.config['output']['make_new_gribs']
        self.nthreads_w = self.config['input']['hrrr_num_wgrib_threads']

        self.start_date = self.config['time']['start_date']
        self.end_date = self.config['time']['end_date']
        self.fmt_date = '%Y%m%d'

        # create an hourly time step between the start date and end date
        self.date_list = utils.daterange(self.start_date, self.end_date)

        # create a daily list between the start and end date
        self.day_list = utils.daylist(self.start_date, self.end_date)

        self.out_dir = self.config['output']['out_location']

        self._logger.debug('NomadsHRRR initialized')

    def initialize_data(self):
        """Initialize the data if needed
        """

        self.num_files = create_new_grib(
            self.date_list,
            self.directory, self.out_dir,
            self.topo.x1, self.topo.y1, self._logger,
            zone_letter=self.topo.zone_letter,
            zone_number=self.topo.zone_number,
            buff=self.buffer,
            nthreads_w=self.nthreads_w,
            make_new_gribs=self.make_new_gribs)

        self._logger.info('NomadsHRRR data initialized')

    def run(self):
        """Run the WindNinja simulation for NormadsHRRR
        """

        # make config, run wind ninja, make netcdf
        for idd, day in enumerate(self.day_list):
            self._logger.info('Running WindNinja for day {}'.format(day))
            self._logger.debug(
                '{} input files will be ran'.format(self.num_files[day]))

            start_time = datetime.now()

            out_dir_day = os.path.join(self.out_dir,
                                       'data{}'.format(
                                           day.strftime(self.fmt_date)),
                                       'wind_ninja_data')
            out_dir_wn = os.path.join(out_dir_day,
                                      'hrrr.{}'.format(
                                          day.strftime(self.fmt_date)))

            # make output folder if it doesn't exist
            if not os.path.isdir(out_dir_day):
                os.makedirs(out_dir_day)

            # run WindNinja_cli
            wn_cfg = deepcopy(self.config['wind_ninja'])
            wn_cfg['forecast_filename'] = out_dir_wn
            # wn_cfg['forecast_duration'] = 0  # num_list[idd]
            wn_cfg['elevation_file'] = self.topo.windninja_topo

            wn = WindNinja(
                wn_cfg,
                self.config['output']['wn_cfg'])
            wn.run_wind_ninja()

            telapsed = datetime.now() - start_time
            self._logger.debug('Running day took {} sec'.format(
                telapsed.total_seconds()))