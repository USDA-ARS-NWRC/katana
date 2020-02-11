"""
instantiate SMRF and use those config options to call the command line
procedures for the Katana program
"""

import numpy as np
import dateparser
import os
from subprocess import Popen, PIPE


# docker paths
image = 'usdaarsnwrc/katana:latest'
directory = '/data/input'
out_dir = '/data/output'
topo_dir = '/data/topo'

topo_dir1 = os.path.abspath('/home/micahsandusky/test_windninja/tmp_hrrr')
directory1 = os.path.abspath('/data/snowpack/forecasts/hrrr')
out_dir1 = os.path.abspath(
    '/data/blizzard/tuolumne/devel/wy2017/test_windninja/data')

# inputs
buff = 6000
start_date = dateparser.parse('2016-10-12 00:00')
#end_date = dateparser.parse('2016-10-20 23:00')
end_date = dateparser.parse('2016-10-12 23:00')

# wind ninja inputs
wn_topo = os.path.join(topo_dir, 'tuol.asc')
wn_topo_prj = os.path.join(topo_dir, 'tuol.prj')
wn_cfg = os.path.join(out_dir, 'windninjarun.cfg')
nthreads = 24
dxy = 100

# smrf params
fp_dem = os.path.join(topo_dir, 'tuolx_50m_topo.nc')
zone_letter = 'N'
zone_number = 11

fmt = '%Y%m%d-%H-%M'

# derived perams
wy_start = dateparser.parse('2016-10-01 00:00')


# make entrypoint take in the run_katana call
action = ' docker run -v {}:{} -v {}:{} -v {}:{}'.format(directory1, directory,
                                                         out_dir1, out_dir,
                                                         topo_dir1, topo_dir)

action += ' {} --start_date {} --end_date {} --water_year_start {}'
action = action.format(image,
                       start_date.strftime(fmt),
                       end_date.strftime(fmt),
                       wy_start.strftime(fmt))

action += ' --input_directory {} --output_directory {}'.format(
    directory, out_dir)
action += ' --wn_cfg {}'.format(wn_cfg)
action += ' --topo {} --zn_number {} --zn_letter {}'.format(
    fp_dem, zone_number, zone_letter)
action += ' --buff {} --nthreads {} --dxy {}'.format(buff, nthreads, dxy)

print('Running {}'.format(action))
s = Popen(action, shell=True, stdout=PIPE)

while True:
    line = s.stdout.readline()
    print(line)
    if not line:
        break
