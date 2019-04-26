[![GitHub version](https://badge.fury.io/gh/USDA-ARS-NWRC%2Fkatana.svg)](https://badge.fury.io/gh/USDA-ARS-NWRC%2Fkatana)
[![Docker Build Status](https://img.shields.io/docker/build/usdaarsnwrc/katana.svg)](https://hub.docker.com/r/usdaarsnwrc/katana/)
[![Docker Automated build](https://img.shields.io/docker/automated/usdaarsnwrc/katana.svg)](https://hub.docker.com/r/usdaarsnwrc/katana/)
[![Build Status](https://travis-ci.org/USDA-ARS-NWRC/katana.svg?branch=master)](https://travis-ci.org/USDA-ARS-NWRC/katana)
[![Coverage Status](https://coveralls.io/repos/github/USDA-ARS-NWRC/katana/badge.svg?branch=master)](https://coveralls.io/github/USDA-ARS-NWRC/katana?branch=master)

# katana
A project for bringing [WindNinja] Data into the AWSM system.

[WindNinja]: https://github.com/firelab/windninja

The function of Katana is to deal with the data editing and data flow required to run WindNinja over large areas and long
periods of time, as well as actually running WindNinja. The power of Katana is that it organizes all of the necessary software
(WindNinja, GDAL, wgrib2) into an easy to use docker.

## Basic outline
The steps that Katana takes are as follows:

1. Create topo ascii for use in WindNinja
2. Crop grib2 files to a small enough domain to actually run WindNinja as we cannot read in the full CONUS domain
3. Extract the necessary variables from the grib2 files
4. Organize the new, smaller grib2 files into daily folders
5. Create WindNinja config
6. Run WindNinja (one run per day)

### Running Katana
There is a command line script called run_katana that takes a lot of arguments. Moving these arguments to a config file will make things a bit easier. Using the Katana docker will make things easier as well. Currently we are on version 0.3.1. You can type run_katana --help to get a description of the inputs. Here is an example of what a docker call for katana might look like right now:

```
docker run --rm  -v /home/ops/wy2019/sanjoaquin/topo:/data/topo -v /data/snowpack/forecasts/hrrr:/data/input   -v /data/blizzard/sanjoaquin/ops/wy2019/ops/data:/data/output  --user 1008:4 usdaarsnwrc/katana:0.3.1 --start_date 20190214-00-00 --end_date 20190215-00-00 --input_directory /data/input --output_directory /data/output --wn_cfg /data/output/windninjarun.cfg --topo /data/topo/topo.nc --zn_number 11 --zn_letter N --buff 6000 --nthreads 12 --nthreads_w 1 --dxy 200 --loglevel info --logfile /data/output/log_test_20190214-00-00.txt
```

As evident from this call, the docker images are stored on [DockerHub](https://cloud.docker.com) under the container name ```usdaarsnwrc/katana```.

### Inputs
 - start_date: start date for run
 - end_date: end date for run
 - input_directory: input directory where ```hrrr.<date>``` files are located
 - output_directory: directory where output will be stored. katana will make a ```data<date>/wind_ninja_data/``` here and store the data in that directory
 - wn_cfg: config file path for WindNinja. The config will be created here
 - topo: path to smrf topo netcdf
 - zn_number: UTM zone number for input topo
 - zn_letter: UTM zone letter for input topo
 - buff: buffer around SMRF domain for WindNinja input
 - nthreads: number of WindNinja threads
 - nthreads_w: number of threads for wgrib2 commands
 - dxy: grid spacing of WindNinja simulation
 - log_level: level of info printed out in the logs
 - logfile: file where log will be written. default is None and will print to screen
 - have_gribs: don't make gribs because we did that already

### Outputs
There are three types of files generated from Katana:
 - **An ascii topo**: This is an ascii version of the dem for SMRF. This will only be generated if it does not exist.
 - **grib2 files**: Katana will generate the cropped HRRR files with only the necessary variables and put them in the wind_ninja_data folder inside your run specific data directory.
 - **ascii outputs**: Currently Katana is set up to run WindNinja, letting WindNinja output ascii files for wind speed, direction, and cloud cover. There are more output data types available, but this makes the most sense for AWSM modeling.

### Ingesting into SMRF
SMRF has the ability to read in the WindNinja output ascii wind speed and direction and interpolate them onto the SMRF grid. Here is what that looks like in the ```[wind]``` section of the SMRF config.

```
wind_ninja_dir: /data/output/sanjoaquin/ops/wy2019/ops/data
wind_ninja_dxy: 200
wind_ninja_pref: topo_windninja_topo
wind_ninja_tz: UTC
```

When Katana outputs the ascii topo, it will append ```windninja_topo``` to the original name of the topo NetCDF. This ```wind_ninja_pref``` config option is everything before the date, grid resolution, and ***.asc*** that WindNinja adds to the topo name. For instance, this example is for the file pattern of ```topo_windninja_topo_10-01-2018_0900_200m_vel.asc```. Notice the ```wind_ninja_dxy``` of 200 matches the ```200m``` in the WindNinja output file name.

## Wind Ninja
WindNinja is a computationally efficient wind solver developed for on-site predictions of wind when firefighting. It is a great tool for our real-time modeling efforts. There two ways to run WindNinja and multiple types of input data. We use the HRRR grib2 files, and run it using the command line interface (CLI).

Wind Ninja can use two different types of solvers: a mass solver or a mass and momentum solver. The mass and momentum solver will be more accurate, but is considerably slower and requires install of some OpenFOAM utilities. This would be a great tool for research, but doesn't fit with our near real-time runs. As such, we use the mass solver.

## Needed imporvements
  - One improvement that is already written, just not implemented. This using config files rather than command line arguments.
  - Addition of WRF file compatibility when it becomes available in WindNinja
  - Functionality to run WindNinja with station data rather than gridded data (this exists in WindNinja, but not Katana)
