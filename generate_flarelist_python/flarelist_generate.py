import os
import logging
import pandas as pd
import numpy as np
from astropy.time import Time
from astropy import units as u
from sunpy.net import Fido, attrs as a
from sunpy.time import parse_time
from stixpy.net.client import STIXClient
from stixpy.product import Product
from stixdcpy.net import Request as jreq
from astropy.coordinates import SkyCoord
from sunpy.coordinates import frames, SphericalScreen
import astrospice
import warnings
from datetime import datetime
from sunpy.util import SunpyDeprecationWarning
import glob
import re
from datetime import datetime

from flarelist_coord_utils import is_visible
from flarelist_generate_utils import find_matching_files, search_remote_data
from stx_estimate_flare_location import stx_estimate_flare_location


def fetch_operational_flare_list(tstart, tend, save_csv=False):
    """
    Fetches the STIX flare list from the Data Center using stixdcpy.

    This flarelist is based on an automated approach from the quicklook data. 

    If save_csv=True, it will save csv with filename: stix_flare_list_tstart_tend.csv

    Parameters:
    ----------
    tstart : `~astropy.time.Time`
        Start time of query
    tend : `~astropy.time.Time`
        End time of query
    save_csv : bool, default=False
        Save the dataframe to a csv file, optional

    Return:
    ------
    pd.DataFrame of the flarelist over timerange queried

    Notes:
    -----
    The STIX Data Center has a limit of 5000 flares that can be returned from a single query.
    To ensure no flares are missed, the search is broken into intervals of <= 60 days.
    """
    logging.info('Fetching flare list from Data Center...')

    if (tend - tstart).datetime.days > 60:
        times = [tstart.datetime]
        tstart_new = tstart.copy()
        while tstart_new < tend:
            tstart_new += 60 * u.day
            times.append(tstart_new.datetime)
    else:
        times = [tstart, tend]

    times[-1] = tend
    flare_df_lists = []

    for i in range(len(times) - 1):
        flares = jreq.fetch_flare_list(times[i], times[i + 1])
        logging.info(f'Fetched {len(flares)} flares from {times[i]} to {times[i + 1]}')
        f1 = pd.DataFrame(flares)
        flare_df_lists.append(f1)

    full_flare_list = pd.concat(flare_df_lists)
    full_flare_list.drop_duplicates(inplace=True)
    full_flare_list.sort_values(by="peak_UTC", inplace=True)
    full_flare_list.reset_index(inplace=True, drop=True)
    times_flares = pd.to_datetime(full_flare_list["peak_UTC"])


    if save_csv:
        filename = f"stix_operational_list_{times_flares.min().strftime('%Y%m%d')}_{times_flares.max().strftime('%Y%m%d')}.csv"
        full_flare_list.to_csv(filename, index_label=False)
        logging.info(f'Saved flare list to {filename}')

    return full_flare_list


def filter_and_associate_files(flare_list, local_files_path, threshold_counts=1000, save_csv=False):
    """
    Filters the flare list to only include events above a certain threshold
    and attempts to associate each event with a local or remote data file.

    Parameters:
    ----------
    flare_list : pd.DataFrame
        The full flare list retrieved from the Data Center.
    local_files_path : str
        Path to the directory containing local .fits files.
    threshold_counts : float
        filter flares with counts in the 4-10keV channel above this value
        default = 1000


    Return:
    ------
    pd.DataFrame
        Filtered flare list with file paths added.

    """
    logging.info('Filtering flare list and associating data files')
    flarelist_gt_1000 = flare_list[flare_list["LC0_PEAK_COUNTS_4S"] >= threshold_counts]
    flarelist_gt_1000.reset_index(inplace=True, drop=True)

    local_files = glob.glob(f"{local_files_path}/*.fits")
    file_names = []

    for i, row in flarelist_gt_1000.iterrows():
        peak_flare = row["peak_UTC"]
        file = find_matching_files(local_files, peak_flare)
        if file is None:
            file = search_remote_data(row, path=local_files_path+"/{file}")
            if file:
                logging.info(f"Fetched remote file for flare {i+1}/{len(flarelist_gt_1000)}")
            else:
                file = "file_issue"
        file_names.append(file)
        logging.info(f"Processed flare {i + 1}/{len(flarelist_gt_1000)}")

    flarelist_gt_1000["filenames"] = file_names
    times_flares = pd.to_datetime(flarelist_gt_1000["peak_UTC"])

    if save_csv:
        filename = f"stix_operational_list_with_file_info_{times_flares.min().strftime('%Y%m%d')}_{times_flares.max().strftime('%Y%m%d')}.csv"
        flarelist_gt_1000.to_csv(filename, index=False, index_label=False)
        logging.info(f'Saved flare list to {filename}')

    return flarelist_gt_1000


def estimate_flare_locations_and_attenuator(flare_list_with_files, save_csv=False):
    """
    Estimates flare locations and gets the attenuator status for each flare in the provided flare list.

    This function uses `stx_estimate_flare_location()` to estimate the flare location from the provided files,
    checks the attenuator status by examining the `rcr` column of the data, and adjusts the energy range accordingly.
    Results are appended to the input DataFrame.

    Parameters
    ----------
    flare_list_with_files : pd.DataFrame
        DataFrame containing flare information including file paths (`filenames`) to associated `.fits` files.

    """

    logging.info('Estimating flare locations and attenuator status...')
    results = {"loc_x": [], "loc_y": [], "loc_x_stix": [], "loc_y_stix": [],
               "sidelobes_ratio": [], "flare_id": [], "error": [], "attenuator": []}

    for i, row in flare_list_with_files.iterrows():
        energy_range = [4, 16] * u.keV

        # Define a 20s time range around peak time
        tstart = parse_time(row["peak_UTC"]) - 20 * u.s
        tend = parse_time(row["peak_UTC"]) + 20 * u.s
        time_range = [tstart.strftime("%Y-%m-%dT%H:%M:%S"), tend.strftime("%Y-%m-%dT%H:%M:%S")]
        cpd_file = row["filenames"]
        att = False  # Default value for attenuator

        try:
            cpd_sci = Product(cpd_file)

            # Check for attenuator status by looking for any 'rcr' data points in the time range
            # as the att_in column in the operational flarelist isnt working.
            if np.any(cpd_sci.data[(cpd_sci.data["time"] >= tstart) & (cpd_sci.data["time"] <= tend)]["rcr"]):
                att = True
                energy_range = [4, 25] * u.keV
            print(att)
            

            # Estimate flare location
            flare_loc_stix, flare_loc, sidelobe = stx_estimate_flare_location(cpd_file, time_range, energy_range)

            # Store results
            results["loc_x"].append(flare_loc.Tx.value)
            results["loc_y"].append(flare_loc.Ty.value)
            results["loc_x_stix"].append(flare_loc_stix.Tx.value)
            results["loc_y_stix"].append(flare_loc_stix.Ty.value)
            results["sidelobes_ratio"].append(sidelobe)
            results["error"].append(False)
            results["flare_id"].append(row["flare_id"])
            results["attenuator"].append(att)

        except Exception as e:
            logging.error(f"Error processing flare {i}: {e}")
            results["loc_x"].append(np.nan)
            results["loc_y"].append(np.nan)
            results["loc_x_stix"].append(np.nan)
            results["loc_y_stix"].append(np.nan)
            results["sidelobes_ratio"].append(np.nan)
            results["error"].append(True)
            results["flare_id"].append(row["flare_id"])
            results["attenuator"].append(att)

    results = pd.DataFrame(results)
    flare_list_with_locations = pd.concat([flare_list_with_files.reset_index(drop=True), results], axis=1)
    
    times_flares = pd.to_datetime(flare_list_with_locations["peak_UTC"])

    if save_csv:
        filename = f"stix_flarelist_w_locations_{times_flares.min().strftime('%Y%m%d')}_{times_flares.max().strftime('%Y%m%d')}.csv"
        flare_list_with_locations.to_csv(filename, index=False, index_label=False)
        logging.info(f'Saved flare list to {filename}')

    return flare_list_with_locations



def merge_and_process_data(flare_list_with_locations, save_csv=False):
    """
    Merges flare list with additional processing and visibility calculation.

    Parameters:
    ----------
    flare_list_with_locations : pd.DataFrame
        Flare list with associated files and estimated locations.

    Return:
    ------
    pd.DataFrame
        Fully processed flare list with positional information and visibility calculation.
    """
    logging.info('Merging and processing flare data...')

    # Load kernels for Solar Orbiter position calculations
    kernels = astrospice.registry.get_kernels("solar orbiter", "predict")
    solo_coords_full = astrospice.generate_coords("SOLAR ORBITER", pd.to_datetime(flare_list_with_locations["peak_UTC"])).heliographic_stonyhurst
    earth_coords_full = astrospice.generate_coords("earth", pd.to_datetime(flare_list_with_locations["peak_UTC"])).heliographic_stonyhurst

    # Add Solar Orbiter position information
    flare_list_with_locations.loc[:, "solo_position_lat"] = solo_coords_full.lat.value
    flare_list_with_locations.loc[:, "solo_position_lon"] = solo_coords_full.lon.value
    flare_list_with_locations.loc[:, "solo_position_AU_distance"] = solo_coords_full.radius.to_value(u.AU)

    # Create SkyCoord objects from Solar Orbiter observer's perspective
    flare_coords_solo_hpc = SkyCoord(flare_list_with_locations["loc_x"].values * u.arcsec, 
                                     flare_list_with_locations["loc_y"].values * u.arcsec, 
                                     frame=frames.Helioprojective(observer=solo_coords_full))

    # Here we're are transforming these coordinates to HPC from earth, HGS and HGC. 
    # For events off limb we are assuming a spherical screen to deal with the reprojection.
    with SphericalScreen(flare_coords_solo_hpc.observer, only_off_disk=True):
        flare_coords_earth_hpc = flare_coords_solo_hpc.transform_to(frames.Helioprojective(observer=earth_coords_full))
        flare_coords_hgs = flare_coords_solo_hpc.transform_to(frames.HeliographicStonyhurst)
        flare_coords_hgc = flare_coords_solo_hpc.transform_to(frames.HeliographicCarrington)

    # Visibility check from Earth
    visible_frame_earth = is_visible(flare_coords_earth_hpc)
    flare_list_with_locations.loc[:, "visible_from_earth"] = visible_frame_earth

    # Add transformed coordinates
    flare_list_with_locations.loc[:, 'hpc_x_earth'] = flare_coords_earth_hpc.Tx.value
    flare_list_with_locations.loc[:, 'hpc_y_earth'] = flare_coords_earth_hpc.Ty.value
    flare_list_with_locations.loc[:, 'hgs_lon'] = flare_coords_hgs.lon.value
    flare_list_with_locations.loc[:, 'hgs_lat'] = flare_coords_hgs.lat.value
    flare_list_with_locations.loc[:, 'hgc_lon'] = flare_coords_hgc.lon.value
    flare_list_with_locations.loc[:, 'hgc_lat'] = flare_coords_hgc.lat.value

    # Set X, Y HPC earth to NaN if not visible from Earth
    flare_list_with_locations.loc[flare_list_with_locations['visible_from_earth'] == False, ['hpc_x_earth', 'hpc_y_earth']] = np.nan

    # Column renaming for final output
    flare_list_with_locations.rename(columns={'LC0_PEAK_COUNTS_4S': '4-10 keV', 
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
                                              # 'timeshift' : 'light_travel_time',
                                              'GOES_class' : 'GOES_class_time_of_flare',
                                              'GOES_flux' : 'GOES_flux_time_of_flare',
                                              'loc_x' : 'hpc_x_solo',
                                              'loc_y' : 'hpc_y_solo',
                                              }, inplace=True)

    # overwrite the attenuator keyword to correct one from files.
    flare_list_with_locations["att_in"] = flare_list_with_locations["attenuator"]


    columns = ['start_UTC', 'end_UTC', 'peak_UTC', '4-10 keV', '10-15 keV', '15-25 keV', '25-50 keV', '50-84 keV',
               'bkg 4-10 keV', 'bkg 10-15 keV', 'bkg 15-25 keV', 'bkg 25-50 keV', 'bkg 50-84 keV', 'bkg_baseline_4-10 keV',
               'hpc_x_solo', 'hpc_y_solo', 'hpc_x_earth', 'hpc_y_earth', 'visible_from_earth', 
               'hgs_lon', 'hgs_lat', 'hgc_lon', 'hgc_lat', 
               'solo_position_lat', 'solo_position_lon', 'solo_position_AU_distance', 
               'GOES_class_time_of_flare', 'GOES_flux_time_of_flare', 'att_in', 'flare_id', 'sidelobes_ratio', 'error']
    flarelist_final = flare_list_with_locations[columns]
    # Save final processed list
    times_flares = pd.to_datetime(flarelist_final["peak_UTC"])

    if save_csv:
        filename = f"stix_flarelist_w_locations_{times_flares.min().strftime('%Y%m%d')}_{times_flares.max().strftime('%Y%m%d')}.csv"
        flarelist_final.to_csv(filename, index=False, index_label=False)
        logging.info(f'Saved flare list to {filename}')

    return flare_list_with_locations




def get_flares(tstart, tend, local_files_path):
    """
    Fetches and returns a fully processed flare list with locations included.

    Parameters:
    ----------
    tstart : str or `~astropy.time.Time`
        Start time of the query in ISO format or as an Astropy Time object.
    tend : str or `~astropy.time.Time`
        End time of the query in ISO format or as an Astropy Time object.
    local_files_path : str
        Path to the directory containing local .fits files.

    Return:
    ------
    pd.DataFrame
        A fully processed DataFrame containing the list of flares with locations.

    Example Usage:
    -------------
    >>> from flarelist_generate import get_flares
    >>> flares = get_flares('2023-01-01', '2023-02-01', '/path/to/local/files')
    >>> print(flares)
    """
    if isinstance(tstart, str):
        tstart = Time(tstart)
    if isinstance(tend, str):
        tend = Time(tend)

    logging.info(f'Retrieving and processing flares between {tstart} and {tend}')

    # step 1: Fetch the operational flare list
    flare_list = fetch_operational_flare_list(tstart, tend)

    # step 2: filter to counts about 100 and get list of cpd files associated with each
    flare_list_with_files = filter_and_associate_files(flare_list, local_files_path)

    # step 3: estimate flare locations and get attenuator status
    flare_list_with_locations = estimate_flare_locations_and_attenuator(flare_list_with_files)

    # step 4: get more coordinate information and tidy
    final_flarelist_with_locations = merge_and_process_data(flare_list_with_locations)

    logging.info('Flare processing completed successfully.')

    return final_flarelist_with_locations


