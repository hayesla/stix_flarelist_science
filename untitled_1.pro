
data = READ_CSV('full_flarelist_with_paths.csv')
i=4
path_sci_file = data.FIELD20[i]
print, path_sci_file

peak_time = data.FIELD05[i]
start_time = atime(anytim(peak_time) - 20)
end_time = atime(anytim(peak_time) + 20)
time_range = [start_time, end_time]
aux_fits_file = data.FIELD19[i]
req_id = data.FIELD18[i]
flare_id = data.FIELD01[i]


get_flare_location, path_sci_file, time_range, aux_fits_file, req_id, flare_id, i, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, $
  max_bp_coord=max_bp_coord, fitsigmasout_pso=fitsigmasout_pso
