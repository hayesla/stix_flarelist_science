import pandas as pd 
import numpy as np 
from astropy import units as u 
from astropy.coordinates import SkyCoord
from astropy.time import Time
import astrospice
from sunpy.coordinates import frames
import time
import sunpy.map

flarelist_step1 = pd.read_csv("stix_flarelist_with_files_1000_for_idlinput.csv")
idl_output_step2 = pd.read_csv("flarelist_locations_idloutput_416keV_1000counts_40s.csv")

full_flarelist = pd.merge(flarelist_step1, idl_output_step2,  how='inner', on="flare_id")



def check_bp_maps(i, rootdir='./bp_maps_416', plot=False):
    """
    Function to check the back-projection maps generated through the location estimatation. 
    Here, this is done by checking the fits file of the map, and then removing the pixels surrounding 
    the brightest pixel and then checkign if the next brightest pixel is 90% of the max. 
    If it is, then we say that its not a good "map", and that the value of the flare location 
    isn't trustworthy. 

    Here, you pass the index of the `full_flarelist` dataframe.

    Parameters:
    ----------
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

t1 = time.time()
confidence = []
for i in range(len(full_flarelist)):
    confidence.append(check_bp_maps(i))

t2 = time.time()
print(t2-t1)
full_flarelist["confidence"] = confidence


full_flarelist.to_csv("full_flarelist_with_locations_1000_416keV.csv", index=False, index_label=False)
