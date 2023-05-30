from astropy.time import Time
from astropy import units as u 
from stixdcpy.net import Request as jreq
import pandas as pd


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


	flare_df_lists = []
	for i in range(len(times)-1):
	    flares=jreq.fetch_flare_list(times[i], times[i+1])
	    f1 = pd.DataFrame(flares)
	    flare_df_lists.append(f1)


	full_flare_list = pd.concat(flare_df_lists)

	full_flare_list.drop_duplicates(inplace=True)
	full_flare_list.reset_index(inplace=True, drop=True)

	if save_csv:
		full_flare_list.to_csv("stix_flare_list_{:s}_{:s}.csv".format(tstart.strftime("%Y%m%d"), 
			tend.strftime("%Y%m%d")), index_label=False)
	
	return full_flare_list



tstart = Time("2021-11-01")
tend = Time("2023-03-31")
get_flarelist_from_datacenter(tstart, tend, save_csv=True)
