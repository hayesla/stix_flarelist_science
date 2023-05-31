pro loop_through_files
    
  data = READ_CSV('/Users/hannahcollier/Documents/solo/data/stx_catalogue_pipeline/test_folder/test_df_new.csv') ; change path depending on setup.. csv file output from flare list with paths to sci files
    
  for i = 0,n_elements(data.field1) do begin   ;loop through all rows in data structure
    
    path_sci_file = data.FIELD9[i]
    peak_time = data.FIELD3[i]
    start_time = atime(anytim(peak_time) - 5)
    end_time = atime(anytim(peak_time) + 5)
    time_range = [start_time, end_time]
    aux_fits_file = data.FIELD8[i]
    req_id = data.FIELD7[i]
 
    get_flare_location, path_sci_file, time_range, aux_fits_file, req_id, i, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, $
       max_bp_coord=max_cp_coord, fitsigmasout_pso=fitsigmasout_pso

  endfor

end