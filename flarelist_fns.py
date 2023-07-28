from astropy.time import Time
from sunpy.time import parse_time, TimeRange
from astropy import units as u 
from stixdcpy.net import Request as jreq
from stixpy.net.client import STIXClient
import pandas as pd
from astropy import units as u
from sunpy.net import Fido, attrs as a 



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


