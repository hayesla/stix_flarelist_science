# Solar Orbiter/STIX science flare list 

This is a repository for a study of the STIX flare list using the scientific pixel data.
This flarelist builds upon the operational STIX flare list that is avalable through [stixdcpy API](https://github.com/i4Ds/stixdcpy).
From the events in this list with available pixel data, and with counts above 1000 in the 4-10 keV energy band an image was generated and the location of the flare estimated. 
Currently it consists of ~25150 flares over the time period of 2021-01-01 to 2025-02-28.

 ** i need to update this ** 
 
Here we provide the flare list with the coordinates of the flare estimated, and in several coordinate frames and information whether that flare was observed from Earth.
The flarelist if provided in this file: `STIX_flarelist_w_locations_20210318_20250228_version1_python.csv`

This can be read in python using `pd.read_csv`
e.g. 

```
>>> import pandas as pd
>>> stix_flarelist = pd.read_csv("STIX_flarelist_w_locations_20210318_20250228_version1_python.csv")`
```
or similary in IDL using `READ_CSV()`.

## STIX flare list:

In this file, the flarelist contains:

* `start_UTC` : start time of flare
* `end_UTC` : end time of flare
* `peak_UTC` : peak time of flare
* `4-10 keV` : counts in 4-10 keV energy band
* `10-15 keV` : counts in 4-10 keV energy band
* `15-25 keV` : counts in 15-25 keV energy band
* `25-50 keV` : counts in 25-50 keV energy band
* `50-84 keV` : counts in 50-84 keV energy band
* `att_in` : Boolean on whether the attenuator was in or not 
* `bkg 4-10 keV` : 'background counts in the 4-10 keV channel (median value for most recent quiet period)' 
* `bkg 10-15 keV` : 'background counts in the 10-15 keV channel (median value for most recent quiet period)' 
* `bkg 15-25 keV` : 'background counts in the 15-25 keV channel (median value for most recent quiet period)' 
* `bkg 25-50 keV` : 'background counts in the 25-50 keV channel (median value for most recent quiet period)' 
* `bkg 50-84 keV` " 'background counts in the 50-84 keV channel (median value for most recent quiet period)' 
* `bkg_baseline_4-10 keV` : ' median value of the fitted baseline'
* `hpc_x_solo` : Helioprojective X of flare in arcsec from Solar Orbiter observer location 
* `hpc_y_solo` : Helioprojective Y of flare in arcsec from Solar Orbiter observer location 
* `hpc_x_earth` : Helioprojective X of flare in arcsec from Earth observer location (NaN if not seen from Earth)
* `hpc_y_earth` : Helioprojective Y of flare in arcsec from Earth observer location (NaN if not seen from Earth)
* `visible_from_earth` : Boolean, True if flare visible from Earth observer
* `hgs_lon` : Heliographic Stonyhurst longitude of flare in degrees 
* `hgs_lat` : Heliographic Stonyhurst latitude of flare in degrees 
* `hgc_lon` : Heliographic Carrington longitude of flare in degrees 
* `hgc_lat` : Heliographic Carrington latitude of flare in degrees 
* `solo_position_lat` : Heliographic latitude of the position of Solar Orbiter at time of flare
* `solo_position_lon` : Heliographic longitude of the position of Solar Orbiter at time of flare
* `solo_position_AU_distance` : Distance of Solar Orbiter to Sun in AU
* `GOES_class_time_of_flare` : GOES class of the GOES XRS data at time of flare  *Note this is the class of GOES XRS at time of flare, not derived from STIX data. Doesnt make sense to use when the flares isn't visible to Earth
* `GOES_flux_time_of_flare` : GOES flux of the GOES XRS data at time of flare *Note this is the class of GOES XRS at time of flare, not derived from STIX data. Doesnt make sense to use when the flares isn't visible to Earth
* `flare_id` : ID of flare from stixdcpy 


How it was generated:
--------------------
Overview

This pipeline processes STIX flare observations from the Solar Orbiter mission, providing a complete end-to-end analysis framework to:

* Retrieve operational flare lists from the STIX Data Center.
* Filter and associate files based on intensity thresholds.
* Estimate flare locations and attenuator status using STIX imaging.
* Process positional calculations and transform coordinates to different frames.
* Check visibility of flares from Earth and save the final processed flare list to a CSV file.


