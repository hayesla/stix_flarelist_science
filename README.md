# Solar Orbiter/STIX science flare list 

This is a repository for a study of the STIX flare list using the scientific pixel data.

## STIX flare list:

This repo provides a STIX flare list with the estimated flare location in the csv file: `STIX_flarelist_w_locations_20210214_20230430_version1.csv`

In this file contains:
* 'start_UTC' : start time of flare
* 'end_UTC' : end time of flare
* 'peak_UTC' : peak time of flare
* '4-10 keV' : counts in 4-10 keV energy band
* '10-15 keV' : counts in 4-10 keV energy band
* '15-25 keV' : counts in 15-25 keV energy band
* '25-50 keV' : counts in 25-50 keV energy band
* '50-84 keV' : counts in 50-84 keV energy band
* 'att_in' : Boolean on whether the attenuator was in or not 
* 'bkg 4-10 keV' : 'background counts in the 4-10 keV channel (median value for most recent quiet period)' 
* 'bkg 10-15 keV' : 'background counts in the 10-15 keV channel (median value for most recent quiet period)' 
* 'bkg 15-25 keV' : 'background counts in the 15-25 keV channel (median value for most recent quiet period)' 
* 'bkg 25-50 keV' : 'background counts in the 25-50 keV channel (median value for most recent quiet period)' 
* 'bkg 50-84 keV' " 'background counts in the 50-84 keV channel (median value for most recent quiet period)' 
* 'bkg_baseline_4-10 keV' : ' median value of the fitted baseline'
* 'hpc_x_solo' : Helioprojective X of flare in arcsec from Solar Orbiter observer location 
* 'hpc_y_solo' : Helioprojective Y of flare in arcsec from Solar Orbiter observer location 
* 'hpc_x_earth' : Helioprojective X of flare in arcsec from Earth observer location (NaN if not seen from Earth)
* 'hpc_y_earth' : Helioprojective Y of flare in arcsec from Earth observer location (NaN if not seen from Earth)
* 'visible_from_earth' : Boolean, True if flare visible from Earth observer
* 'hgs_lon' : Heliographic Stonyhurst longitude of flare in degrees 
* 'hgs_lat' : Heliographic Stonyhurst latitude of flare in degrees 
* 'hgc_lon' : Heliographic Carrington longitude of flare in degrees 
* 'hgc_lat' : Heliographic Carrington latitude of flare in degrees 
* 'solo_position_lat' : Heliographic latitude of the position of Solar Orbiter at time of flare
* 'solo_position_lon' : Heliographic longitude of the position of Solar Orbiter at time of flare
* 'solo_position_AU_distance' : Distance of Solar Orbiter to Sun in AU
* 'light_travel_time' : Light travel time shift between Earth and Solar Orbiter in seconds
* 'file_request_id_used' : File request ID of the pixel data used to estimate the flare location
* 'GOES_class_time_of_flare' : GOES class of the GOES XRS data at time of flare  *Note this is the class of GOES XRS at time of flare, not derived from STIX data. Doesnt make sense to use when the flares isn't visible to Earth
* 'GOES_flux_time_of_flare' : GOES flux of the GOES XRS data at time of flare *Note this is the class of GOES XRS at time of flare, not derived from STIX data. Doesnt make sense to use when the flares isn't visible to Earth
* 'flare_id' : ID of flare from stixdcpy 



How it was generated:
--------------------
The flarelist consists of ~6000 flares with counts above 1000 in the 4-10 keV channel over the time period of 2021-01-01 to 2023-05-01.
The flarelist was compiled from the operational STIX flarelist which is available on the [STIX datacenter](https://datacenter.stix.i4ds.net/) and accessabile through the [stixdcpy API](https://github.com/i4Ds/stixdcpy).
For each flare above 1000 counts in the 4-10 keV channel, all available pixel data for those events was quiered and for flares with pixel data, an image was created over the peak in the 4-16 keV energy band in 

In the file th
