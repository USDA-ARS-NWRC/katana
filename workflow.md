#Draft of workflow:

1) Convert topo into usable format
1) For best use, it seems like emulating the LandFire topo structure should work best here
2) Collect HRRR file into .zip folder (or normal folder, unclear here)
3) Make sure HRRR files are copies of ours, not original
4) Trim HRRR files down to a size closer to our model domain
5) Rename HRRR files so iterator is on the forecast hour
6) Use WindNinja CLI to run for specific time period and cell sizes, exporting the 10m wind product and writing the ascii output files
7) Convert ascii output files into our wind_speed.nc, wind_direction.nc(if we want it) files
8) Make sure that the HRRR, topo, and ascii files are stored in an unmounted directory in the docker and that the netCDF files are the only ones that will ouptut
