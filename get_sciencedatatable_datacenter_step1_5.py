import pandas as pd 
from stixdcpy.net import Request as jreq

stix_flares = pd.read_csv("stix_flare_list_20210101_20230701.csv")
big_flares = stix_flares[stix_flares["LC0_PEAK_COUNTS_4S"]>=5e2]
big_flares["peak_UTC"] = pd.to_datetime(big_flares["peak_UTC"])
big_flares.sort_values(by="peak_UTC", inplace=True)
big_flares.reset_index(inplace=True, drop=True)

def get_datacenter_table(big_flares):
	
	# query the STIX datacenter for available data on the science data table
	# Here only looking for the cpd data.
	stixpy_results = []
	for i in range(0, len(big_flares)):
	    
	    test_stixdcpy = jreq.query_science(big_flares["start_UTC"].iloc[i], big_flares["end_UTC"].iloc[i], request_type='xray-cpd')
	    stixpy_results.append(test_stixdcpy)

	# merge dataframes into one big dataframe
	stix_res_df = [f.dataframe() for f in stixpy_results]

	# want to add original flare id as column (could have several results from one flare for example)
	for i in range(len(stix_res_df)):
		len_df = len(stix_res_df[i])
		flare_id_vals = [big_flares.iloc[i]["flare_id"]]*len_df
		stix_res_df[i]["flare_id_orig"] = flare_id_vals

	# concatenate them together (probs a nicer way to do this ..)
	stix_df = stix_res_df[0]
	i = 1
	while i<len(stix_res_df):
	    stix_df = pd.concat((stix_df, stix_res_df[i]))
	    i = i+1

	# save to a csv
	stix_df["flare_id_orig"] = stix_df["flare_id_orig"].astype(int)
	# stix_df.to_csv("stix_queryscience_api_{:s}_{:s}_bigflares.csv".format(pd.to_datetime(big_flares["start_UTC"].min()).strftime("%Y%m%d"), 
	# 	 																  pd.to_datetime(big_flares["start_UTC"].max()).strftime("%Y%m%d")), 
	#    			   index=False, index_label=False)
	stix_df.to_csv("stix_queryscience_api_{:s}_{:s}_allflares.csv".format(pd.to_datetime(big_flares["start_UTC"].min()).strftime("%Y%m%d"), 
		 																  pd.to_datetime(big_flares["start_UTC"].max()).strftime("%Y%m%d")), 
	   			   index=False, index_label=False)

get_datacenter_table(big_flares)
