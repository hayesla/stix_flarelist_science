# Solar Orbiter/STIX science flare list 

This is a repository for a study of the STIX flare list using the scientific pixel data.



## How to run the code and get your own flare list with locations [status: 28-Jun-2023]

Before beginning, ensure that you have the latest version of the stixdcpy package (https://github.com/i4Ds/stixdcpy). Please note that this software must be installed directly from the Github repository and **not** with `pip install stixdcpy`. Otherwise, an older version of the software will be installed, and the code will crash.

To create your own list of flares with locations, run the following Python scripts in the specified order:

1. Run `get_flarelist_from_datacenter()` (in *get_fullflarelist_step1.py*). You can modify `tstart` and `tend` according to your needs.
2. Run `get_available_data_from_fido()` (in *get_available_datalist_stix_step2.py*). Make sure to modify the name of the CSV file, which contains time information: `stix_flares = pd.read_csv("stix_flare_list_TSTART_TEND.csv")`
3. Run `get_datacenter_table()` (in *get_sciencedatatable_datacenter_step1_5.py*). Same as step 2: rename `stix_flares = pd.read_csv("stix_flare_list_TSTART_TEND.csv")`
4. Run the notebook *download_files_from_list.ipynb*. Make sure to change the path to the CSV file in the second cell, giving the path to the csv file named "stix_big_flare_list_TSTART_TEND_with_files.csv".

At this point, you should end up with a CSV file called “full_flarelist_with_paths.csv”. Next, run IDL with the STIX-GSW (https://github.com/i4Ds/STIX-GSW) that is up-to-date and able to work with the FITS files delivered to ESA. In IDL, run the following:

1. Run *loop_files_2.pro*. This should create the following CSV file: “flare_location_output4.csv”. Additionally, the backprojection maps are stored in a folder named "bp_maps3" (which must be created manually before running the code).

That's pretty much it, for now!
