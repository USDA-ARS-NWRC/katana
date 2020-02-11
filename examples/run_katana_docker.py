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
directory1 = os.path.abspath('/home/micahsandusky/test_windninja/tmp_hrrr')
out_dir1 = os.path.abspath('/home/micahsandusky/test_windninja/data')

# inputs
buff = 6000
start_date = dateparser.parse('2018-09-28 00:00')
end_date = dateparser.parse('2018-09-29 23:00')

# wind ninja inputs
wn_topo = os.path.join(directory, 'tuol.asc')
wn_topo_prj = os.path.join(directory, 'tuol.prj')
wn_cfg = os.path.join(directory, 'windninjarun.cfg')
nthreads = 2
dxy = 200

# smrf params
fp_dem = os.path.join(directory, 'tuolx_50m_topo.nc')
zone_letter = 'N'
zone_number = 11

fmt = '%Y%m%d-%H-%M'

# derived perams
wy_start = dateparser.parse('2017-10-01 00:00')


# make entrypoint take in the run_katana call
action = ' docker run -v {}:{} -v {}:{} {}'.format(directory1, directory,
                                                   out_dir1, out_dir, image)

action += ' --start_date {} --end_date {} --water_year_start {}'
action = action.format(start_date.strftime(fmt),
                       end_date.strftime(fmt),
                       wy_start.strftime(fmt))

action += ' --input_directory {} --output_directory {}'.format(
    directory, out_dir)
action += ' --wn_topo {} --wn_prj {} --wn_cfg {}'.format(
    wn_topo, wn_topo_prj, wn_cfg)
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
