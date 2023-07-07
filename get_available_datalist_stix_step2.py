from sunpy.net import Fido, attrs as a 
from stixpy.net.client import STIXClient
import time
import pandas as pd 
from sunpy.time import parse_time, TimeRange

stix_flares = pd.read_csv("stix_flare_list_20221109_20221115.csv")
big_flares = stix_flares[stix_flares["LC0_PEAK_COUNTS_4S"]>=5*1e2]
big_flares["peak_UTC"] = pd.to_datetime(big_flares["peak_UTC"])
big_flares.sort_values(by="peak_UTC", inplace=True)
big_flares.reset_index(inplace=True, drop=True)


def get_available_data_from_fido(big_flares):
	"""
	Query Fido to get all available request IDs for each flare.

	Saves a new csv with the input dataframe with extra columns for Request IDs and number of files.

	Parameters
	----------
	big_flares " `pd.DataFrame`
		dataframe of flarelist. Needs columns "start_UTC", "peak_UTC" and "end_UTC"

	saves new csv
	"""

	# query the dataserver for available data over the timeranges of each flare event
	# only looking for pixel data (CPD) data, however could be several products available
	# for each flare. 
	t1 = time.time()
	fido_res = []
	for i in range(len(big_flares)):
	    res_sci = Fido.search(a.Time(big_flares["start_UTC"].iloc[i], big_flares["end_UTC"].iloc[i]), a.Instrument.stix, 
	                      a.stix.DataProduct.sci_xray_cpd)
	    fido_res.append(res_sci)

	t2 = time.time()

	# for each flare - see if files were available, and if so
	# add the unique request IDs as a list. 
	# only return the files for which the peak time lies within the file timerange.
	# also create a list of the number of unique files for each flare
	available_files = []
	number_unique_files = []
	for i in range(len(big_flares)):
	    files_ids = []
	    for j in range(len(fido_res[i]["stix"])):
	        file_tr = TimeRange(fido_res[i]["stix"][j][["Start Time", "End Time"]])
	        if parse_time(big_flares["peak_UTC"].iloc[i]) in file_tr:
	           	files_ids.append(fido_res[i]["stix"][j]["Request ID"])
	    available_files.append(files_ids)
	    number_unique_files.append(len(files_ids))
	#add these to the flarelist
	big_flares["number_available_files"] = number_unique_files
	big_flares["available_file_request_IDs"] = available_files
	#save new csv with these columns appended
	big_flares.to_csv("stix_all_flare_list_{:s}_{:s}_with_files.csv".format(pd.to_datetime(big_flares["start_UTC"].min()).strftime("%Y%m%d"), 
		 																    pd.to_datetime(big_flares["start_UTC"].max()).strftime("%Y%m%d")), 
					  index=False, index_label=False)


get_available_data_from_fido(big_flares)