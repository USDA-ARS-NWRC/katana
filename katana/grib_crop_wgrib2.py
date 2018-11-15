import numpy as np
import matplotlib.pyplot as plt
from katana.get_topo import get_topo_stats
import utm
from subprocess import Popen, PIPE
import os
import pandas as pd
import datetime
import netCDF4 as nc
import glob


def grib_to_sgrib(fp_in, out_dir, file_dt, x, y, logger, 
                  buff=1500, zone_letter='N', zone_number=11,
                  nthreads_w=1):
    """
    Function to write 4 bands from grib2 to cropped grib2

    Args:
            fp_in: grib file path
            out_dir: output directory to write hrrr data
            file_dt: time stamp of file
            x: x coords in utm of new domain
            y: y coords in utm of new domain
            logger: instance of logger
            buff: buffer in meters for buffering domain
            zone_letter: UTM zone letter (N)
            zone_number: UTM zone number
            nthreads_w:  number of threads for wgrib2 commands
    """
    # date format for files
    #fmt = '%Y%m%d-%H-%M'
    fmt1 = '%Y%m%d'
    fmt2 = '%H'
    dir1 = os.path.join(out_dir,
                        'data{}'.format(file_dt.strftime(fmt1)),
                        'wind_ninja_data',
                        'hrrr.{}'.format(file_dt.strftime(fmt1)))

    # make file names
    tmp_grib = os.path.join(dir1, 'tmp.grib2')
    fp_out = os.path.join(dir1,
                          'hrrr.t{}z.wrfsfcf00.grib2'.format(file_dt.strftime(fmt2)))

    # create directory if needed
    if not os.path.isdir(dir1):
        os.makedirs(dir1)

    # find bounds (to_latlon returns (LATITUDE, LONGITUDE).)
    ur = np.array(utm.to_latlon(np.max(x)+buff, np.max(y)+buff, zone_number, zone_letter))
    ll = np.array(utm.to_latlon(np.min(x)-buff, np.min(y)-buff, zone_number, zone_letter))
    # get latlon bounds
    lats = ll[0]
    latn = ur[0]
    lonw = ll[1]
    lone = ur[1]

    # call to crop grid
    action = 'wgrib2 {} -ncpu {} -small_grib {}:{} {}:{} {}'.format(fp_in, nthreads_w,
                                                                    lonw, lone,
                                                                    lats, latn, tmp_grib)

    # run commands
    logger.debug('\nRunning command {}'.format(action))
    s = Popen(action, shell=True, stdout=PIPE, stderr=PIPE)

    while True:
        line = s.stdout.readline().decode()
        eline = s.stderr.readline().decode()

        if not line:
            break

        # if it failed, find a different forecast hour
        if "FATAL" in eline:
            fatl = True
            break
        else:
            fatl = False

    # tryingn to find better grib file
    if fatl:
        del(s)
        os.remove(tmp_grib)

        logger.warning('\nsmall grib did not work, trying a forecast hour\n')

        # find the directory name
        hrrr_dir = os.path.dirname(fp_in)
        fname = os.path.basename(fp_in)
        # try:
        # find the start and forecast hour
        st_hr = int(fname[6:8]) - 1
        fx_hr = int(fname[17:19]) + 1
        # get a new file to open
        new_file = os.path.join(hrrr_dir,
                                'hrrr.t{:02d}z.wrfsfcf{:02d}.grib2'.format(st_hr, fx_hr))
        action = 'wgrib2 {} -ncpu {} -small_grib {}:{} {}:{} {}'.format(new_file, nthreads_w,
                                                                        lonw, lone,
                                                                        lats, latn, tmp_grib)
        logger.debug('\n\nTrying {}'.format(action))
        s = Popen(action, shell=True, stdout=PIPE, stderr=PIPE)
        while True:
            line = s.stdout.readline().decode()
            eline = s.stderr.readline().decode()
            if not line:
                break

            # if it failed, find a different forecast hour
            if "FATAL" in eline:
                raise ValueError('Cannot find decent grib file for {}'.format(file_dt))

    # call to grab correct variables
    action2 = "wgrib2 {} -ncpu {} -match 'TMP:2 m|UGRD:10 m|VGRD:10 m|TCDC:' -GRIB {}"
    action2 = action2.format(tmp_grib,
                             nthreads_w,
                             fp_out)
    # action2 = "wgrib2 {} -match '^(66|71|72|101):' -GRIB {}".format(tmp_grib,
    #                                                                 fp_out)

    logger.debug('\nRunning command {}'.format(action2))
    s2 = Popen(action2, shell=True, stdout=PIPE)
    s2.wait()

    os.remove(tmp_grib)


def create_new_grib(start_date, end_date, directory, out_dir,
                    x1, y1, logger,
                    zone_letter='N', zone_number=11, buff=6000,
                    nthreads_w=1, make_new_gribs=True):
    """
    Function to iterate through the dates and create new, cropped grib files
    needed to run WindNinja

    Args:
        start_date:     datetime object for start of run
        end_date:       datetime object for end of run
        directory:      directory storing the individual day directories for hrrr files
        out_dir:        output directory for new hrrr files
        x1:             UTM X coords for dem as numpy array
        y1:             UTM Y coords for dem as numpy array
        logger:         Instance of logger
        zone_letter:    UTM zone letter for dem
        zone_number:    UTM zone number for dem
        buff:           buffer to add onto dem domain in meters
        nthreads_w:     number of threads for wgrib2 commands
        make_new_gribs: actually make the new gribs or just count how many we would make

    Returns:
        date_list:      list of datetime days that are converted
        num_list:       number of run hours per day

    Additional:
        outputs new hrrr grib2 files in out_dir
    """

    # get list of days to grab
    fmt = '%Y%m%d'
    dtt = end_date - start_date
    ndays = int(dtt.days)
    date_list = [start_date + datetime.timedelta(days=x) for x in range(0, ndays+1)]

    # list to track number of hours for each day
    num_list = []

    # loop through dates
    for idt, dt in enumerate(date_list):
        counter = 0
        # get files
        hrrr_dir = os.path.join(directory,
                                'hrrr.{}/hrrr.t*f00.grib2'.format(dt.strftime(fmt)))
        fps = glob.glob(hrrr_dir)

        if len(fps) == 0:
            logger.warning('No matching files in {}'.format(hrrr_dir))

        # write and read new netcdfs
        for idf, fp in enumerate(fps):
            bn = os.path.basename(fp)
            # find hours from start of day
            add_hrs = int(bn[6:8]) + int(bn[17:19])
            file_time = pd.to_datetime(dt + datetime.timedelta(hours=add_hrs))

            # check if we are in the date range
            if file_time >= start_date and file_time <= end_date:
                # option to cut down on already completed work
                if make_new_gribs:
                    # convert grib to smaller gribgs with only the needed variables for WindNinjaS
                    grib_to_sgrib(fp, out_dir, file_time, x1, y1, logger, buff=buff,
                                zone_letter=zone_letter, zone_number=zone_number,
                                nthreads_w=nthreads_w)

                # track hours per day
                counter += 1

            else:
                logger.warning('{} is not in date range and will not be included'.format(file_time))

        num_list.append(counter)

    return date_list, num_list
