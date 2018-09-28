# katana
A project for bringing WindNinja Data into the AWSM system

# Current Status
The project being in its most early stages is being used to store scripts required to convert
data to be used in the AWSM system. With time, the project will take on more of a 
fully developed package to be used as an API.

## Additions
 - cropping of grib files from CONUS HRRR to the 4 needed variables and a smaller domain
 - Dockerfile for wgrib2 and WindNinja_cli

## Needed
 - config file
 - Python wrapped calls for WindNinja_cli
 - conversion from WindNinja output to netcdf
 - interpolation of output wind field from 10m above canopy to whatever height we want
 - conversion of our topo files to the correct format for WindNinja
 - more robust finding of bands within grib file (names not numbers)
 - streamlined process from dates and basin input to full Katana workflow
