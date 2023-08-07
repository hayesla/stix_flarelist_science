from astropy.time import Time
from sunpy.time import parse_time, TimeRange
from astropy import units as u 
from stixdcpy.net import Request as jreq
from stixpy.net.client import STIXClient
import pandas as pd
from astropy import units as u
from sunpy.net import Fido, attrs as a 
import sunpy.map
import numpy as np 


def get_flarelist_from_datacenter(tstart, tend, save_csv=False):
    """
    Function to get the STIX flarelist from the https://datacenter.stix.i4ds.net/
    using stixdcpy.

    This flarelist is based on an automated appraoch from the quicklook
    data. 

    If save_csv=True, it will save csv with filename: stix_flare_list_tstart_tend.csv

    Parameters
    ----------
    tstart : `~astropy.time.Time`
        start time of query
    tend : `~astropy.time.Time`
        end time of query
    save_csv : bool, default=False
        save the dataframe to a csv file, optional

    Return
    ------
    pd.DataFrame of the flarelist over timerange queried

    """

    # theres a limit of 5000 flares that will be returned
    # from the stixdcpy API, so to take make sure we dont miss some
    # we'll break up the times into intervals and make several searches and the
    # concatentae together

    # check if the time between start and end times is > 60 days
    if (tend - tstart).datetime.days > 60:
        times = [tstart.datetime]
        tstart_new = tstart.copy()
        while tstart_new<tend:
            tstart_new += 60*u.day
            times.append(tstart_new.datetime)
    else:
        times = [tstart, tend]

    times[-1] = tend

    flare_df_lists = []
    for i in range(len(times)-1):
        flares=jreq.fetch_flare_list(times[i], times[i+1])
        f1 = pd.DataFrame(flares)
        flare_df_lists.append(f1)


    full_flare_list = pd.concat(flare_df_lists)

    full_flare_list.drop_duplicates(inplace=True)
    full_flare_list.sort_values(by="peak_UTC", inplace=True)
    full_flare_list.reset_index(inplace=True, drop=True)

    if save_csv:
        full_flare_list.to_csv("stix_operational_flare_list_{:s}_{:s}.csv".format(tstart.strftime("%Y%m%d"), 
            tend.strftime("%Y%m%d")), index_label=False)
    
    return full_flare_list


def get_available_data_from_fido(flarelist, save_csv=False):
    """
    Query Fido to get all available request IDs for each flare.

    Saves a new csv with the input dataframe with extra columns for Request IDs and number of files.

    Parameters
    ----------
    flarelist " `pd.DataFrame`
        dataframe of flarelist. Needs columns "start_UTC", "peak_UTC" and "end_UTC"

    saves new csv
    """

    # query the dataserver for available data over the timeranges of each flare event
    # only looking for pixel data (CPD) data, however could be several products available
    # for each flare. 
    fido_res = []
    for i in range(len(flarelist)):
        # some pixel data can start from day before (i.e. close to 00UT, so
        # need this check)
        start_time = Time(flarelist["start_UTC"].iloc[i])
        end_time = Time(flarelist["end_UTC"].iloc[i])
        if int(start_time.strftime("%H"))<=1:
            start_time = start_time - 2*u.hour

        res_sci = Fido.search(a.Time(start_time, end_time), a.Instrument.stix, 
                          a.stix.DataProduct.sci_xray_cpd)
        fido_res.append(res_sci)


    # for each flare - see if files were available, and if so
    # add the unique request IDs as a list. 
    # only return the files for which the peak time lies within the file timerange.
    # also create a list of the number of unique files for each flare
    available_files = []
    number_unique_files = []
    for i in range(len(flarelist)):
        files_ids = []
        for j in range(len(fido_res[i]["stix"])):
            file_tr = TimeRange(fido_res[i]["stix"][j][["Start Time", "End Time"]])
            if parse_time(flarelist["peak_UTC"].iloc[i]) in file_tr:
                files_ids.append(fido_res[i]["stix"][j]["Request ID"])
        available_files.append(files_ids)
        number_unique_files.append(len(files_ids))
    #add these to the flarelist
    flarelist["number_available_files"] = number_unique_files
    flarelist["available_file_request_IDs"] = available_files
    #save new csv with these columns appended
    if save_csv:
        flarelist.to_csv("stix_operational_list_with_file_info_{:s}_{:s}.csv".format(pd.to_datetime(flarelist["start_UTC"].min()).strftime("%Y%m%d"), 
                                                                                pd.to_datetime(flarelist["start_UTC"].max()).strftime("%Y%m%d")), 
                          index=False, index_label=False)

    return flarelist


def get_pixel_data(tstart, tend, request_id):
    """
    Function to download STIX pixel data given a timerange and a request ID
    
    Parameters
    ----------
    tstart : start time of flare
    tend : end time of flare
    request_id : Request ID of the observation

    Returns
    -------
    path to file if downloaded

    """
    start_time = Time(tstart)
    end_time = Time(tend)
    if int(start_time.strftime("%H"))<=1:
        start_time = start_time - 2*u.hour    

    res = Fido.search(a.Time(start_time, end_time), a.Instrument.stix, a.stix.DataProduct.sci_xray_cpd)
    res = res["stix"][res["stix"]["Request ID"] == int(request_id)]
    f = Fido.fetch(res, path="./pixel_data/{file}")
    if len(f)>0:
        return "./"+f[0]
    else:
        return ''

def get_aux_data(tstart, tend):
    """
    Function to download STIX auxillary data given a timerange
    
    Parameters
    ----------
    tstart : start time of flare
    tend : end time of flare

    Returns
    -------
    path to file if downloaded
    """
    res = Fido.search(a.Time(tstart, tend), a.Instrument.stix, a.stix.DataProduct.aux_ephemeris)
    f = Fido.fetch(res, path="./aux_data/{file}")
    if len(f)>0:
        return "./"+f[0]
    else:
        return ''


def check_bp_maps(full_flarelist, i, rootdir='./bp_maps_416', plot=False):
    """
    Function to check the back-projection maps generated through the location estimatation. 
    Here, this is done by checking the fits file of the map, and then removing the pixels surrounding 
    the brightest pixel and then checkign if the next brightest pixel is 90% of the max. 
    If it is, then we say that its not a good "map", and that the value of the flare location 
    isn't trustworthy. 

    Here, you pass the index of the `full_flarelist` dataframe.

    Parameters:
    ----------
    full_flarelist : `pd.DataFrame`
        pandas DataFrame of flarelist with columns, `req_id` and `flare_id`
    i : int, 
        index of the `full_flarelist` dataframe
    root_dir : `str`, directory of where map fits are saved
        default to `./bp_maps416`
    plot : Boolean, optional
        If True, then plots the map with the brightest pixel as a cross and shows the
        marked out pixels

    Returns:
    --------
    `str` : `pass` or `fail` 

    """
    file = rootdir+'/bp_nat_map-{:d}_{:d}.fits'.format(full_flarelist["req_id"].iloc[i],
                                                       full_flarelist["flare_id"].iloc[i])
    map_test = sunpy.map.Map(file)
    map_max_val = np.max(map_test.data)
    x, y = np.where(map_test.data == map_max_val)
    new_data = map_test.data.copy()
    new_data[x[0]-20:x[0]+20, y[0]-20:y[0]+20]=0
    
    new_max_val = np.max(new_data)
    if new_max_val < 0.9*map_max_val:
        confidence = "pass"

    else:
        confidence = "fail"
    
    if plot:
        new_map = sunpy.map.Map(new_data, map_test.meta)
        fig = plt.figure(figsize=(9, 4))
        ax1 = fig.add_subplot(1, 2, 1, projection=map_test)
        ax2 = fig.add_subplot(1, 2, 2, projection=new_map)
        map_test.plot(axes=ax1, vmin=0, vmax=map_max_val, cmap="viridis")
        map_test.draw_limb(axes=ax1)
        new_map.plot(axes=ax2, vmin=0, vmax=map_max_val, cmap="viridis")
        new_map.draw_limb(axes=ax2)
    
    return confidence

