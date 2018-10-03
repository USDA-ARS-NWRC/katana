"""
instantiate SMRF and use those config options to call the command line
procedures for the Katana program
"""

import numpy as np
import pandas as pd
import os
from subprocess import Popen, PIPE

#mnt = '/home/micahsandusky/Documents/Code/test_windninja'
#mnt = os.path.abspath(mnt)
image = './docker-compose.yml'
image = os.path.abspath(image)

# inputs
buff = 6000
directory = '/data/input'
out_dir = '/data/output'
# out_dir = './sim_files_grib'
# wind ninja inputs
wn_topo = '/data/input/tuol.asc'
wn_topo_prj = '/data/input/tuol.prj'
wn_cfg = '/data/input/windninjarun.cfg'
nthreads = 2

# smrf params
fp_dem = '/data/input/tuolx_50m_topo.nc'
zone_letter = 'N'
zone_number = 11

fmt = '%Y%m%d-%H-%M'

start_date = pd.to_datetime('2018-09-28 00:00')
end_date = pd.to_datetime('2018-09-29 23:00')

# derived perams
wy_start = pd.to_datetime('2017-10-01 00:00')

# creat call
# action = 'docker compose ...'

# make entrypoint take in the run_katana call

#action = ' docker run -v {}:/data test'.format(mnt)
action = ' docker compose -f {}'.format(image)
action += ' --start_date {} --end_date {} --water_year_start {}'
action = action.format(start_date.strftime(fmt),
                       end_date.strftime(fmt),
                       wy_start.strftime(fmt))

action += ' --input_directory {} --output_directory {}'.format(directory, out_dir)
action += ' --wn_topo {} --wn_prj {} --wn_cfg {}'.format(wn_topo, wn_topo_prj, wn_cfg)
action += ' --topo {} --zn_number {} --zn_letter {}'.format(fp_dem, zone_number, zone_letter)
action += ' --buff {} --nthreads {}'.format(buff, nthreads)

print('Running {}'.format(action))
s = Popen(action, shell=True,stdout=PIPE)

while True:
    line = s.stdout.readline()
    print(line)
    if not line:
        break
print(action)
