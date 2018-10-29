"""
instantiate SMRF and use those config options to call the command line
procedures for the Katana program
"""

import numpy as np
import pandas as pd
import os
from subprocess import Popen, PIPE


# docker paths
# image = 'usdaarsnwrc/katana:latest'
image = 'usdaarsnwrc/katana:devel'
# image = 'katana'


topo_dir = '/data/topo'
topo_dir1 = os.path.abspath('/home/micahsandusky/Documents/Code/test_windninja/topo/')

directory = '/data/input'
directory1 = os.path.abspath('../tmp_hrrr')

out_dir = '/data/output'
out_dir1 = os.path.abspath('/home/micahsandusky/Documents/Code/test_windninja/data')

# inputs
buff = 6000
start_date = pd.to_datetime('2018-09-20 00:00')
#end_date = pd.to_datetime('2016-10-20 23:00')
end_date = pd.to_datetime('2018-09-20 03:00')

# wind ninja inputs
# wn_topo = os.path.join(topo_dir, 'tuol.asc')
# wn_topo_prj = os.path.join(topo_dir, 'tuol.prj')
wn_cfg = os.path.join(out_dir, 'windninjarun.cfg')
nthreads = 2
dxy = 400

# smrf params
fp_dem = os.path.join(topo_dir, 'topo_tuol_2019.nc')
zone_letter = 'N'
zone_number = 11

fmt = '%Y%m%d-%H-%M'

# logging
logfile = os.path.join(out_dir, 'log_test.txt')
#logfile = None
loglevel = 'debug'


# make entrypoint take in the run_katana call
action = ' docker run -v {}:{} -v {}:{} -v {}:{}'.format(directory1, directory,
                                                         out_dir1, out_dir,
                                                         topo_dir1, topo_dir)

action += ' {} --start_date {} --end_date {}'
action = action.format(image,
                       start_date.strftime(fmt),
                       end_date.strftime(fmt))

action += ' --input_directory {} --output_directory {}'.format(directory, out_dir)
action += ' --wn_cfg {}'.format(wn_cfg)
action += ' --topo {} --zn_number {} --zn_letter {}'.format(fp_dem, zone_number, zone_letter)
action += ' --buff {} --nthreads {} --dxy {}'.format(buff, nthreads, dxy)
action += ' --loglevel {} --logfile {}'.format(loglevel, logfile)

print('Running {}'.format(action))
s = Popen(action, shell=True,stdout=PIPE)

while True:
    line = s.stdout.readline()
    print(line)
    if not line:
        break
