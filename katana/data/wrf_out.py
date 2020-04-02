import logging
import os
import shutil
from copy import deepcopy
from datetime import datetime
from glob import glob

import netCDF4 as nc
import pytz

from katana import utils
from katana.data.data_base import BaseData
from katana.wind_ninja import WindNinja


class WRFout(BaseData):

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

        super().__init__(config, topo)

        # WRF file information
        self.wrf_filename = self.config['input']['wrf_filename']
        self.get_wrf_time_info()

        self.out_dir_tmp = os.path.join(self.out_dir, 'tmp')

        self._logger.debug('WRFout initialized')

    def get_wrf_time_info(self):
        """Retrieve information from the WRF file as to the time
        range of the file
        """

        f = nc.Dataset(self.wrf_filename)
        t = f.variables['Times']

        # borrowed from SMRF
        t.set_auto_maskandscale(False)
        try:
            times = [('').join(v) for v in t]
        except TypeError:
            times = []
            for v in t:
                times.append(''.join([s.decode('utf-8') for s in v]))
        except Exception:
            raise Exception('Could not convert WRF times to readable format')

        # remove the underscore and convert to datetime object
        times = [utils.parse_date(v.replace('_', ' '))
                 for v in times]

        # set the timezone
        self.wrf_times = [pytz.utc.localize(t) for t in times]

        f.close()

        self.check_file_dates()

    def check_file_dates(self):
        """Check that the WRF file dates coorespond to the dates provided
        """

        # check that the dates are within the file range
        in_between_dates = []
        for d in self.wrf_times:
            if d >= self.start_date and d <= self.end_date:
                in_between_dates.append(d)

        num_dates = len(in_between_dates)
        num_list = len(self.date_list)
        num_wrf = len(self.wrf_times)

        if num_dates != num_list:
            self._logger.warning('Not all dates present in WRF file')

        if num_dates == 0:
            self._logger.error(
                'No times in WRF file between the start and end date')

        if num_wrf > num_list:
            self._logger.warning("There are {} more times in the WRF file "
                                 "than specified. WindNinja will perform "
                                 "simulations for all times in file".format(
                                     num_wrf - num_list))

    def run(self):
        """Run the WindNinja simulation for WRFout

        A few things can happen with the WRF files. First,
        there can be more times in the file than are desired.
        Second, there WRF file can be split up over multiple days,
        but WindNinja will only output to one directory. Therefore,
        all the WindNinja output for WRF will be into a temporary
        directory and moved into the right folders afterwards. This
        ensures that there is only output between the start and end
        date and will be able to handle multiple days.
        """

        # make config, run wind ninja, make netcdf
        self._logger.info(
            'Running WindNinja for WRF file {}'.format(self.wrf_filename))

        start_time = datetime.now()

        if not os.path.isdir(self.out_dir_tmp):
            os.makedirs(self.out_dir_tmp)

        # run WindNinja_cli
        wn_cfg = deepcopy(self.config['wind_ninja'])
        wn_cfg['forecast_filename'] = self.wrf_filename
        wn_cfg['elevation_file'] = self.topo.windninja_topo
        wn_cfg['output_path'] = self.out_dir_tmp

        wn = WindNinja(
            wn_cfg,
            self.config['output']['wn_cfg'])
        wn.run_wind_ninja()

        # move files to where then need to go
        self.organize_outputs()

        telapsed = datetime.now() - start_time
        self._logger.debug('Total elapsed time for WRFout: {} sec'.format(
            telapsed.total_seconds()))

    def organize_outputs(self):
        """Organize the WRF outputs from the temporary directory
        to the day folders
        """

        self._logger.info('Moving output files to day directories')

        # if the start and end time are over multiple days
        # create the structure
        for day in self.day_list:
            self.make_output_day_folder(day)

        file_names = glob(
            os.path.join(
                self.out_dir_tmp, '{}*'.format(self.topo.windnina_filenames)
            ))

        # go through each file and decode the date
        # then put into the right place
        for file_name in file_names:
            fname = os.path.basename(file_name)
            f = fname.replace(self.topo.windnina_filenames, '').split('_')
            date_value = utils.parse_date(f[1])

            if date_value is None:
                raise Exception('Could not determine the WindNinja file date')

            new_path = os.path.join(self.output_day_folder(date_value), fname)

            # move the file to it's new destination
            shutil.move(file_name, new_path)

        # remove the tmp dir and anything left in it
        shutil.rmtree(self.out_dir_tmp)
