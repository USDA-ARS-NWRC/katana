"""
instantiate SMRF and use those config options to call the command line
procedures for the Katana program
"""

# inputs
buff = 6000
directory = './tmp_hrrr'
out_dir = '/data/data'

# smrf params
fp_dem = 'tuolx_50m_topo.nc'
zone_letter = 'N'
zone_number = 11

start_date = pd.to_datetime('2018-09-20 00:00')
end_date = pd.to_datetime('2018-09-21 00:00')

# derived perams
wy_start = pd.to_datetime('2017-10-01 00:00')

# creat call
action = 'docker compose ...'

# make entrypoint take in the run_katana call
