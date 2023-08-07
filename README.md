# Solar Orbiter/STIX science flare list 

This is a repository for a study of the STIX flare list using the scientific pixel data.
This flarelist builds upon the operational STIX flare list that is avalable through [stixdcpy API](https://github.com/i4Ds/stixdcpy).
From the events in this list with available pixel data, and with counts above 1000 in the 4-10 keV energy band an image was generated and the location of the flare estimated. 
Currently it consists of ~6000 flares over the time period of 2021-01-01 to 2023-05-01.

Here we provide the flare list with the coordinates of the flare estimated, and in several coordinate frames and information whether that flare was observed from Earth.
The flarelist if provided in this file: `STIX_flarelist_w_locations_20210214_20230430_version1.csv`

This can be read in python using `pd.read_csv`
e.g. 

```
>>> import pandas as pd
>>> stix_flarelist = pd.read_csv("STIX_flarelist_w_locations_20210214_20230430_version1.csv")`
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
* `light_travel_time` : Light travel time shift between Earth and Solar Orbiter in seconds
* `file_request_id_used` : File request ID of the pixel data used to estimate the flare location
* `GOES_class_time_of_flare` : GOES class of the GOES XRS data at time of flare  *Note this is the class of GOES XRS at time of flare, not derived from STIX data. Doesnt make sense to use when the flares isn't visible to Earth
* `GOES_flux_time_of_flare` : GOES flux of the GOES XRS data at time of flare *Note this is the class of GOES XRS at time of flare, not derived from STIX data. Doesnt make sense to use when the flares isn't visible to Earth
* `flare_id` : ID of flare from stixdcpy 


How it was generated:
--------------------
The code used to generate this flarelist `STIX_flarelist_w_locations_20210214_20230430_version1.csv` is available in the `generate_flarelist` directory. 
Its currently in three steps (python, idl, python).

The flarelist was compiled from the operational STIX flarelist which is available on the [STIX datacenter](https://datacenter.stix.i4ds.net/) and accessabile through the [stixdcpy API](https://github.com/i4Ds/stixdcpy).
From this:

1. Choose only flares with counts in the 4-10 keV energy band >= 1000
2. For each of these flares, query the database to find any available pixel data around peak of flare
3. For events with pixel data, use the IDL procedure `stx_estimate_flare_location.pro` to create an image of full disk over peak of flare in the 4-16 keV energy band with an integration time of 40s.
4. `stx_estimate_flare_location` creates a backprojection map from the visibilities and then use VIS_FWDFIT of gaussian to find more accurate location of flare maximum.
5.  For each event, the quality of the location is determined by analysing the backprojection maps. If other maximia in the map is > 90% of flare location, then the quality fails and we do not use those flares in this list.
6. Coordinate information:  For the flares with quality flare location, the coordinates of the flares are calculated and transformed into other coordinate frames useful for the user, and also tested whether the coordinate from solar Orbiter field of view is seen from Earth. These are all given in the flarelist:
    * Helioprojective X, Y, at Solar Orbiter
    * Helioprojective X, Y, at Earth (NaNs if not seen from Earth)
    * Heliographic Stonyhurst
    * Heliographic Carrington
    * The Solar Orbiter position is also included in the list.


