import datetime
import glob
import os
import subprocess

import dateparser
import numpy as np
import utm

fmt1 = '%Y%m%d'
fmt2 = '%H'


def wind_ninja_output_dir(out_dir, file_datetime):
    """Create the wind ninja output directory for HRRR files

    Arguments:
        out_dir {str} -- output directory path
        file_datetime {datetime} -- datetime of the file

    Returns:
        str -- path to the cropped HRRR data
    """
    return os.path.join(out_dir,
                        'data{}'.format(file_datetime.strftime(fmt1)),
                        'wind_ninja_data',
                        'hrrr.{}'.format(file_datetime.strftime(fmt1)))


def call_wgrib2(action, logger):
    """Execute a wgrib2 command

    Arguments:
        action {str} -- command for wgrib2 to execute
        logger {logger} -- logger instance

    Returns:
        Boolean -- True if call succeeds
    """

    # run command line using Popen
    logger.debug('Running "{}"'.format(action))

    with subprocess.Popen(
        action,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    ) as s:

        # stream the output of WindNinja to the logger
        return_code = s.wait()
        if return_code:
            for line in s.stdout:
                logger.warning(line.rstrip())
            logger.warning("An error occured while running wgrib2 action")
        else:
            for line in s.stdout:
                logger.debug(line.rstrip())

        return return_code


def grib_to_small_grib(fp_in, out_dir, file_dt, x, y, logger,
                       buff=6000, zone_letter='N', zone_number=11,
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

    Returns:
            not fatl:   True if the run was succesful
            tmp_grib:   File pointer to temporary grib file
            fp_out:     File pointer to final grib file

    """
    # date format for files
    # fmt = '%Y%m%d-%H-%M'
    dir1 = wind_ninja_output_dir(out_dir, file_dt)

    # make file names
    tmp_grib = os.path.join(dir1, 'tmp.grib2')
    fp_out = os.path.join(dir1,
                          'hrrr.t{}z.wrfsfcf00.grib2'.format(
                              file_dt.strftime(fmt2)))

    # create directory if needed
    if not os.path.isdir(dir1):
        os.makedirs(dir1)

    # find bounds (to_latlon returns (LATITUDE, LONGITUDE).)
    ur = np.array(utm.to_latlon(np.max(x)+buff, np.max(y) +
                                buff, zone_number, zone_letter))
    ll = np.array(utm.to_latlon(np.min(x)-buff, np.min(y) -
                                buff, zone_number, zone_letter))
    # get latlon bounds
    lats = ll[0]
    latn = ur[0]
    lonw = ll[1]
    lone = ur[1]

    # call to crop grid
    action = 'wgrib2 {} -ncpu {} -small_grib {}:{} {}:{} {}'.format(
        fp_in, nthreads_w,
        lonw, lone,
        lats, latn, tmp_grib)

    # # run commands
    # logger.debug('Running command "{}"'.format(action))
    # s = Popen(action, shell=True, stdout=PIPE, stderr=PIPE)

    fatl = call_wgrib2(action, logger)

    # trying to find better grib file
    if fatl:
        os.remove(tmp_grib)
        logger.warning(
            'Creating small grib did not work, trying a forecast hour')

    return not fatl, tmp_grib, fp_out


def sgrib_variable_crop(tmp_grib, nthreads_w, fp_out, logger):
    """
    Take the small grib file from grib_to_small_grib and cut it down
    to the variables we need

    Args:
        tmp_grib:   File path to small grib2 file
        nthreads_w: Number of threads for running wgrib2 commands
        fp_out:     Path for outputting final grib2 file

    Returns:

    """

    # call to grab correct variables
    action2 = "wgrib2 {} -ncpu {} -match \
        'TMP:2 m|UGRD:10 m|VGRD:10 m|TCDC:' -GRIB {}"
    action2 = action2.format(tmp_grib,
                             nthreads_w,
                             fp_out)

    fatl = call_wgrib2(action2, logger)

    if fatl:
        logger.warning(
            'Cutting variables from grib did not work')

    os.remove(tmp_grib)

    return not fatl


def create_new_grib(date_list, directory, out_dir,
                    x1, y1, logger,
                    zone_letter='N', zone_number=11, buff=6000,
                    nthreads_w=1, make_new_gribs=True):
    """
    Function to iterate through the dates and create new, cropped grib files
    needed to run WindNinja

    Args:
        start_date:     datetime object for start of run
        end_date:       datetime object for end of run
        directory:      directory storing the individual day
                        directories for hrrr files
        out_dir:        output directory for new hrrr files
        x1:             UTM X coords for dem as numpy array
        y1:             UTM Y coords for dem as numpy array
        logger:         Instance of logger
        zone_letter:    UTM zone letter for dem
        zone_number:    UTM zone number for dem
        buff:           buffer to add onto dem domain in meters
        nthreads_w:     number of threads for wgrib2 commands
        make_new_gribs: actually make the new gribs or just count
                        how many we would make

    Returns:
        date_list:      list of datetime days that are converted
        num_list:       number of run hours per day

    Additional:
        outputs new hrrr grib2 files in out_dir
    """

    fx_start_hour = 0

    logger.info('Creating new gribs for topo domain')

    # create a datelist dict to hold the files
    out_files = {}
    for dt in date_list:
        if dt.date() not in out_files.keys():
            out_files[dt.date()] = 0

    # option to cut down on already completed work
    if make_new_gribs:

        # loop through dates
        for idt, dt in enumerate(date_list):
            logger.info('Working on grib file for {}'.format(dt))

            # try different forecast hours to get a working file
            for fx_hr in range(fx_start_hour, fx_start_hour+8):
                fp = hrrr_file_name_finder(directory, dt, fx_hr)

                # convert grib to smaller gribs with only the needed
                # variables for WindNinjaS
                sgrib, tmp_grib, fp_out = grib_to_small_grib(
                    fp,
                    out_dir,
                    dt,
                    x1, y1,
                    logger,
                    buff=buff,
                    zone_letter=zone_letter,
                    zone_number=zone_number,
                    nthreads_w=nthreads_w)

                # proceed and break when we get a good file
                if sgrib:
                    # grab just the variables we need
                    status = sgrib_variable_crop(tmp_grib, nthreads_w,
                                                 fp_out, logger)
                    if status:
                        out_files[dt.date()] += 1
                        break

                # kill job if we didn't find a good file
                if fx_hr == 6:
                    raise IOError('No good grib file for {}'.format(
                        dt.strftime('%Y-%m-%d %H')))

    else:
        logger.info(("Make new gribs set to False,"
                     " no grib files were processed"))
        for day in out_files.keys():
            dir1 = wind_ninja_output_dir(out_dir, day)

            files = glob.glob1(dir1, '*.grib2')
            out_files[day] = len(files)

    return out_files


def hrrr_file_name_finder(base_path, date, fx_hr=0):
    """
    Find the file pointer for a hrrr file with a specific forecast hour

    hours    0    1    2    3    4
             |----|----|----|----|
    forecast
    start    fx hour
             |----|----|----|----|
    00       01   02   03   04   05
    01            01   02   03   04
    02                 01   02   03
    03                      01   02

    Adapted from `weather_forecast_retrieval.utils`

    Args:
        base_path:  The base HRRR directory. For
                    /data/forecasts/hrrr/hrrr.20180203/...
                    the base_path is ./forecasts/hrrr/
        date:       datetime that the file is used for
        fx_hr:      forecast hour
    Returns:
        fp:         string of absolute path to the file

    """

    fmt_day = '%Y%m%d'
    base_path = os.path.abspath(base_path)

    if not isinstance(date, datetime.datetime):
        date = dateparser.parse(date)

    fx_hr = int(fx_hr)

    day = date.date()
    hr = int(date.hour)

    new_hr = hr - fx_hr

    # if we've dropped back a day, fix logic to reflect that
    if new_hr < 0:
        day = day - datetime.timedelta(days=1)
        new_hr = new_hr + 24

    # create the new path
    day_folder = 'hrrr.{}'.format(day.strftime(fmt_day))
    file_name = 'hrrr.t{:02d}z.wrfsfcf{:02d}.grib2'.format(new_hr, fx_hr)
    fp = os.path.join(base_path,
                      day_folder,
                      file_name
                      )

    return fp
