# katana

[![GitHub version](https://badge.fury.io/gh/USDA-ARS-NWRC%2Fkatana.svg)](https://badge.fury.io/gh/USDA-ARS-NWRC%2Fkatana)
[![Docker Build Status](https://img.shields.io/docker/build/usdaarsnwrc/katana.svg)](https://hub.docker.com/r/usdaarsnwrc/katana/)
[![Docker Automated build](https://img.shields.io/docker/automated/usdaarsnwrc/katana.svg)](https://hub.docker.com/r/usdaarsnwrc/katana/)
[![Build Status](https://travis-ci.com/USDA-ARS-NWRC/katana.svg?branch=master)](https://travis-ci.com/USDA-ARS-NWRC/katana)
[![Coverage Status](https://coveralls.io/repos/github/USDA-ARS-NWRC/katana/badge.svg?branch=master)](https://coveralls.io/github/USDA-ARS-NWRC/katana?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/02c98487a2fdd524e6e9/maintainability)](https://codeclimate.com/github/USDA-ARS-NWRC/katana/maintainability)

A project for bringing [WindNinja] simulations into the AWSM system.

[WindNinja]: https://github.com/firelab/windninja

The function of Katana is to deal with the data editing and data flow required to run WindNinja over large areas and long periods of time, as well as actually running WindNinja. The power of Katana is that it organizes all of the necessary software (WindNinja, GDAL, wgrib2) into an easy to use docker.

The steps that Katana takes are as follows:

1. Create topo ascii for use in WindNinja
2. Crop grib2 files to a small enough domain to actually run WindNinja as we cannot read in the full CONUS domain
3. Extract the necessary variables from the grib2 files
4. Organize the new, smaller grib2 files into daily folders
5. Create WindNinja config
6. Run WindNinja (one run per day)

- [katana](#katana)
- [Input Forcing Files](#input-forcing-files)
  - [High Resolution Rapid Refresh (HRRR)](#high-resolution-rapid-refresh-hrrr)
  - [Weather Research and Forecasting (WRF) Model](#weather-research-and-forecasting-wrf-model)
    - [WRF Surface Files](#wrf-surface-files)
- [Using Katana](#using-katana)
  - [Installing Katana Locally](#installing-katana-locally)
  - [Command Line Usage](#command-line-usage)
  - [Running Katana in Docker](#running-katana-in-docker)
  - [Outputs](#outputs)
    - [Ingesting into SMRF](#ingesting-into-smrf)
- [Wind Ninja](#wind-ninja)
  - [Using with NOMADS HRRR](#using-with-nomads-hrrr)
  - [Using with WRF](#using-with-wrf)
  - [Threading in WindNinja](#threading-in-windninja)

# Input Forcing Files

The input files for `katana` and WindNinja are gridded atmospheric weather models.

## High Resolution Rapid Refresh (HRRR)

The [High Resolution Rapid Refresh (HRRR)](https://rapidrefresh.noaa.gov/hrrr/) is produced operationally by NOAA. It is a real time 3-km product that is updated hourly with data assimilation. Each hour has a 18 hour forecast with extension of 36 hour every 6 hours.

To obtain HRRR simulations, we recommend [`weather_forecast_retrieval`](https://github.com/USDA-ARS-NWRC/weather_forecast_retrieval) that will download HRRR files from either [NOMADS](http://nomads.ncep.noaa.gov/) or [University of Utah HRRR archive](http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/cgi-bin/hrrr_download.cgi). The important aspect is that the folder and file structure from `weather_forecast_retrieval` is what WindNinja requires for it's simulation.

The folder structure is grouped into days with the `hrrr.YYYYMMDD` format. Each file is labeled with the initialization hour `**IH**` and the forecast hour `**FH**`.

```bash
hrrr/
    hrrr.<YYYYMMDD>/
        hrrr.t<IH>z.wrfsfcf<FH>.grib2
```

## Weather Research and Forecasting (WRF) Model

The [Weather Research and Forecasts (WRF)](https://www.mmm.ucar.edu/weather-research-and-forecasting-model) model is a mesoscale numerical weather prediction system that is the foundation of many research and operational application (like HRRR). WRF output files, or `wrfout` files, are the standard output files produced by WRF. WindNinja has the ability to load 2 types of `wrfout` files, the surface files and 3D files. In most cases, Katana will be used with the surface files that have a wind vectors at some height above the surface. The standard output of `wrfout` files are netCDF which is the only file type that WindNinja can open for WRF.

### WRF Surface Files

For WindNinja to identify the use of the surface files, the global netCDF attribute `TITLE` must have the word `WRF` in the netCDF title. Therefore, it will be best practice for Katana to keep all the global attributes of the original netCDF file if there are requirements to remove variables or crop the domain.

The variables that WindNinja requires from the `wrfout` files are the following:

1. `T2` - air temperature at 2 meters
2. `V10` - V component of wind at 10 meters
3. `U10` - U component of wind at 10 meters
4. `QCLOUD` - cloud water mixing ratio

# Using Katana

## Installing Katana Locally

The `katana` dependancies are:

- WindNinja, see [install here](https://github.com/firelab/windninja/wiki)
  - Includes `GDAL` and `PROJ`
- [wgrib2](https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/)
  
To install `katana` locally, run `pip install -r requirements_dev.txt`.

## Command Line Usage

`katana` provides a command line interface called `run_katana`. The only argument to `run_katana` is the path to the configuration file. For example, to run the test configuration

```bash
run_katana tests/config.ini
```

> **NOTE** This requires that WindNinja is installed locally

## Running Katana in Docker

`run_katana` is the default entrypoint to the `katana` docker image.

```bash
docker run --rm  -v </path/to/topo/folder>:/data/topo -v </path/to/input/data>:/data/input   -v </path/to/output>:/data/output  --user 1008:4 usdaarsnwrc/katana /data/topo/katana_config.ini
```

## Outputs

There are three types of files generated from Katana:

- **An ascii topo**: This is an ascii version of the dem for SMRF. This will only be generated if it does not exist.
- **grib2 files**: Katana will generate the cropped HRRR files with only the necessary variables and put them in the wind_ninja_data folder inside your run specific data directory.
- **ascii outputs**: Currently Katana is set up to run WindNinja, letting WindNinja output ascii files for wind speed, direction, and cloud cover. There are more output data types available, but this makes the most sense for AWSM modeling.

### Ingesting into SMRF

SMRF has the ability to read in the WindNinja output ascii wind speed and direction and interpolate them onto the SMRF grid. Here is what that looks like in the `[wind]` section of the SMRF config.

```bash
wind_ninja_dir: </path/to/input/data>
wind_ninja_dxy: 200
wind_ninja_topo_suffix: _windninja_topo
wind_ninja_tz: UTC
```

When Katana outputs the ascii topo, it will append `wind_ninja_topo_suffix` to the original name of the topo NetCDF. This `wind_ninja_topo_suffix` config option is everything before the date, grid resolution, and ***.asc*** that WindNinja adds to the topo name. For instance, this example is for the file pattern of `topo_windninja_topo_10-01-2018_0900_200m_vel.asc`. Notice the `wind_ninja_dxy` of 200 matches the `200m` in the WindNinja output file name.

# Wind Ninja

WindNinja is a computationally efficient wind solver developed for on-site predictions of wind when firefighting. It is a great tool for our real-time modeling efforts. There two ways to run WindNinja and multiple types of input data. We use the HRRR grib2 files, and run it using the command line interface (CLI).

Wind Ninja can use two different types of solvers: a mass solver or a mass and momentum solver. The mass and momentum solver will be more accurate, but is considerably slower and requires install of some OpenFOAM utilities. This would be a great tool for research, but doesn't fit with our near real-time runs. As such, we use the mass solver.

## Using with NOMADS HRRR

HRRR forecast files used in `katana` are through WindNinja [NOMADS](http://nomads.ncep.noaa.gov/) support. WindNinja has the ability to download the HRRR forecasts for you but this is not the use case for `katana`. The HRRR surface file (`wrfsfc`) files are downloaded externally from NOMADS and kept in their file structure. WindNinja can read the directory of these files and perform simulations.

WindNinja can take another type of HRRR data from NCEP but this requires a more rigid file format and is not the preferred way for `katana`.

## Using with WRF

WRF produces `wrfout` files that WindNinja can read. These files can have multiple time steps in the file but WindNinja does not provide a method to subset the time. Instead, all time steps in the file will be ran with WindNinja. Katana deals with this by outputing all WRF WindNinja simulations to a temporary directory then organizes them into day folders afterwards. Any outputs that aren't between Katana's start and end date will deleted.

## Threading in WindNinja

Threading in WindNinja is not achieved on a time step basis, meaning that a single simulation will not employ multiple threads. The speed increase through threading is achived by running multiple simulations at once for WindNinja. To utilize multiple cores, the files must be provided in a directory struture with multiple files (like NOMADS HRRR) or multiple time steps in a netCDF file.
