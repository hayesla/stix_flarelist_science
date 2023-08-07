import pandas as pd 
import numpy as np 
from astropy import units as u 
from astropy.coordinates import SkyCoord
from astropy.time import Time
import astrospice
from sunpy.coordinates import frames
import sunpy.map

from flarelist_fns import check_bp_maps
from flarelist_coord_utils import is_visible


flarelist_step1 = pd.read_csv("stix_flarelist_with_files_1000_for_idlinput.csv")
idl_output_step2 = pd.read_csv("flarelist_locations_idloutput_416keV_1000counts_40s.csv")

full_flarelist = pd.merge(flarelist_step1, idl_output_step2,  how='inner', on="flare_id")

# Get the confidence of the back projection maps output
confidence = []
for i in range(len(full_flarelist)):
    confidence.append(check_bp_maps(full_flarelist, i))

full_flarelist["confidence"] = confidence

# Drop rows that don't pass the back projection test
flarelist = full_flarelist[full_flarelist["confidence"]=="pass"]
flarelist.reset_index(inplace=True, drop=True)
flarelist.drop(columns="confidence", inplace=True)

#full_flarelist.to_csv("full_flarelist_with_locations_1000_416keV.csv", index=False, index_label=False)
# get the position of Solar Orbiter as a function of the flare times
kernals = astrospice.registry.get_kernels("solar orbiter", "predict")
solo_coords_full = astrospice.generate_coords("SOLAR ORBITER", pd.to_datetime(flarelist["peak_UTC"])).heliographic_stonyhurst
earth_coords_full = astrospice.generate_coords("earth", pd.to_datetime(flarelist["peak_UTC"])).heliographic_stonyhurst

# make new columns for Solar Orbiter lat, lon
flarelist.loc[:, "solo_position_lat"] = solo_coords_full.lat.value
flarelist.loc[:, "solo_position_lon"] = solo_coords_full.lon.value
flarelist.loc[:, "solo_position_AU_distance"] = solo_coords_full.radius.to_value(u.AU)

# create SkyCoord objects of the X, Y arcsec from Solar Orbiter observer
flare_coords_solo_hpc = SkyCoord(flarelist["X_arcsec"].values*u.arcsec, 
                                 flarelist["Y_arcsec"].values*u.arcsec, 
                                 frame=frames.Helioprojective(observer=solo_coords_full))

# Here we're are transforming these coordinates to HPC from earth, HGS and HGC. 
# For events off limb we are assuming a spherical screen to deal with the reprojection.
with frames.Helioprojective.assume_spherical_screen(flare_coords_solo_hpc.observer, only_off_disk=True):
    flare_coords_earth_hpc = flare_coords_solo_hpc.transform_to(frames.Helioprojective(observer=earth_coords_full))
    flare_coords_hgs = flare_coords_solo_hpc.transform_to(frames.HeliographicStonyhurst)
    flare_coords_hgc = flare_coords_solo_hpc.transform_to(frames.HeliographicCarrington)

# Now, the HPC coordinates at Earth might be on the backside of the Sun - its gives you teh X, Y as 
# though you "see" through the Sun. Here we check if these coordinates are actually visible from 
# an Earth observer
visible_frame_earth = is_visible(flare_coords_earth_hpc)
flarelist.loc[:, "visible_from_earth"] = visible_frame_earth

flarelist.rename(columns={'LC0_PEAK_COUNTS_4S': '4-10 keV', 
                          'LC1_PEAK_COUNTS_4S': "10-15 keV",
                          'LC2_PEAK_COUNTS_4S': "15-25 keV", 
                          'LC3_PEAK_COUNTS_4S': "25-50 keV", 
                          'LC4_PEAK_COUNTS_4S': "50-84 keV", 
                          'LC0_BKG' : 'bkg_baseline_4-10 keV',
                          'LC0_BKG_COUNTS_4S': 'bkg 4-10 keV', 
                          'LC1_BKG_COUNTS_4S': "bkg 10-15 keV",
                          'LC2_BKG_COUNTS_4S': "bkg 15-25 keV", 
                          'LC3_BKG_COUNTS_4S': "bkg 25-50 keV", 
                          'LC4_BKG_COUNTS_4S': "bkg 50-84 keV", 
                          'req_id' : 'file_request_id_used',
                          'timeshift' : 'light_travel_time',
                          'GOES_class' : 'GOES_class_time_of_flare',
                          'GOES_flux' : 'GOES_flux_time_of_flare',
                          'X_arcsec' : 'hpc_x_solo',
                          'Y_arcsec' : 'hpc_y_solo',
                          }, inplace=True)


flarelist.loc[:, 'hpc_x_earth'] = flare_coords_earth_hpc.Tx.value
flarelist.loc[:, 'hpc_y_earth'] = flare_coords_earth_hpc.Ty.value

# set X, Y HPC earth to nan if not visible from earth
flarelist.loc[flarelist['visible_from_earth'] == False, ['hpc_x_earth', 'hpc_y_earth']] = np.nan

flarelist.loc[:, 'hgs_lon'] = flare_coords_hgs.lon.value
flarelist.loc[:, 'hgs_lat'] = flare_coords_hgs.lat.value

flarelist.loc[:, 'hgc_lon'] = flare_coords_hgc.lon.value
flarelist.loc[:, 'hgc_lat'] = flare_coords_hgc.lat.value


columns = ['start_UTC', 'end_UTC', 'peak_UTC', '4-10 keV', '10-15 keV', '10-15 keV', '15-25 keV', '25-50 keV', '50-84 keV',
           'att_in',
           'bkg 4-10 keV', 'bkg 10-15 keV', 'bkg 15-25 keV', 'bkg 25-50 keV', 'bkg 50-84 keV', 'bkg_baseline_4-10 keV',
           'hpc_x_solo', 'hpc_y_solo', 'hpc_x_earth', 'hpc_y_earth', 'visible_from_earth', 
           'hgs_lon', 'hgs_lat', 'hgc_lon', 'hgc_lat', 
           'solo_position_lat', 'solo_position_lon', 'solo_position_AU_distance', 'light_travel_time',
           'file_request_id_used', 'GOES_class_time_of_flare', 'GOES_flux_time_of_flare', 'flare_id']



final_flarelist = flarelist[columns]
final_flarelist.to_csv("STIX_flarelist_w_locations_{:s}_{:s}_version1.csv".format(pd.to_datetime(final_flarelist["start_UTC"].min()).strftime("%Y%m%d"), 
                                                                                  pd.to_datetime(final_flarelist["start_UTC"].max()).strftime("%Y%m%d")), 
                       index=False, index_label=False)
