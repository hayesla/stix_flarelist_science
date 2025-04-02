from astropy.time import Time
import pandas as pd 
from sunpy.net import Fido, attrs as a 
from sunpy.time import parse_time, TimeRange
from stixpy.net.client import STIXClient
from datetime import datetime
import re
from astropy import units as u 

def parse_file_date_range(filename: str):
    """
    Extract start and end datetime objects from the STIX cpd filename 
    using a regex pattern (i.e. times are in the filename).

    """
    pattern = r'(\d{8}T\d{6})-(\d{8}T\d{6})'
    match = re.search(pattern, filename)
    if match:
        start_str, end_str = match.groups()
        start_dt = datetime.strptime(start_str, '%Y%m%dT%H%M%S')
        end_dt = datetime.strptime(end_str, '%Y%m%dT%H%M%S')
        return start_dt, end_dt
    return None, None


def find_matching_files(files, flare_time):
    """
    Check if a flare time is within any file's date range.

    Parameters:
    ----------
    files : `list`
        List of filenames.
    flare_time : astropy.time.Time or datetime.datetime
        Time for which to find the matching file

    Returns:
    ------
    file : str or None

    """
    flare_dt = datetime.strptime(flare_time, '%Y-%m-%dT%H:%M:%S.%f')

    for file in files:
        start_dt, end_dt = parse_file_date_range(file)
        if start_dt and end_dt and start_dt <= flare_dt <= end_dt:
            return file  

    return None  

def search_remote_data(flare_row, path="/Users/laurahayes/esa_backup/flare_ana/stix_flarelists/generate_flarelist/pixel_data/{file}"):
    """
    Searches for remote data using Fido and returns the file if found, else None.

    Parameters:
    -----------
    A row in the flarelist pandas dataframe for which it has the start, peak and end times
    named start_UTC, peak_UTC, end_UTC

    Returns:
    ------
    file : str or None
        the downloaded file
    """

    start_time = Time(flare_row["start_UTC"])
    end_time = Time(flare_row["end_UTC"])
    
    # adjusting the start time to pull from day before too if before 1am.
    if int(start_time.strftime("%H")) <= 1:
        start_time = start_time - 2 * u.hour

    res_sci = Fido.search(a.Time(start_time, end_time), a.Instrument.stix, a.stix.DataProduct.sci_xray_cpd)
    
    if len(res_sci) == 0 or len(res_sci["stix"]) == 0:
        return None

    # for each file, check whether the flare peak time is in the file
    for j in range(len(res_sci["stix"])):
        file_tr = TimeRange(res_sci["stix"][j][["Start Time", "End Time"]])
        
        if parse_time(flare_row["peak_UTC"]) in file_tr:
            f = Fido.fetch(res_sci["stix"][j], path=path)

            if f:
                # there could be several files that satisfy this, but only need one. 
                return f[0]  
    

    return None