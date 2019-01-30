[![GitHub version](https://badge.fury.io/gh/USDA-ARS-NWRC%2Fkatana.svg)](https://badge.fury.io/gh/USDA-ARS-NWRC%2Fkatana)
[![Docker Build Status](https://img.shields.io/docker/build/usdaarsnwrc/katana.svg)](https://hub.docker.com/r/usdaarsnwrc/katana/)
[![Docker Automated build](https://img.shields.io/docker/automated/usdaarsnwrc/katana.svg)](https://hub.docker.com/r/usdaarsnwrc/katana/)
[![Build Status](https://travis-ci.org/USDA-ARS-NWRC/katana.svg?branch=master)](https://travis-ci.org/USDA-ARS-NWRC/katana)
[![Coverage Status](https://coveralls.io/repos/github/USDA-ARS-NWRC/katana/badge.svg?branch=master)](https://coveralls.io/github/USDA-ARS-NWRC/katana?branch=master)

# katana
A project for bringing [WindNinja] Data into the AWSM system.

[WindNinja]: https://github.com/firelab/windninja

## Current Status
The project being in its most early stages is a command line Python program used to
generate and convert data to be used in the AWSM system. The software is rapidly changing
and will eventually be fully developed package to be used as an API.

Currently, Katana will crop grib2 files and select the necessary variables for WindNinja,
generate a WindNinja configuration file, and run the WindNinja program. It generally follows
the AWSM file format.

The examples give scripts showing how to setup and run
the docker conatiner from a python script so that the inputs do not have to be given in the command line.

## Inputs

 - start_date
 - end_date
 - water_year_start date
 - input_directory
 - output_directory
 - WindNinja desired config path
 - topo NetCDF file
 - UTM zone number
 - UTM zone letter
 - desired domain buffer in meters
 - number of threads for WindNinja
 - desired WindNinja grid resolution
 - log lvel
 - log file
