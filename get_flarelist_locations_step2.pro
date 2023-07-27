pro get_flarelist_locations_step2

flare_list = READ_CSV('stix_flarelist_with_files_lh_test.csv')


; define the file to save to
openw, 1, './flarelist_locations_idloutput_620keV.csv'
printf, 1, 'flare_id', 'timeshift', 'request_id', 'X_arcsec', 'Y_arcsec', 'X_fwdfitsigama', 'X_fwdfitsigama', $
           'max_bp_coord_x', 'max_bp_coord_y', 'max_bp_coord_stix_x', 'max_bp_coord_stix_y', $
format='(%"%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s")' 
free_lun, 1
TIC
FOR i = 0,  n_elements(flare_list.FIELD01) DO BEGIN; n_elements(flare_list.FIELD01)loop through all rows in data structure
    
    print, i
    ; identifiers of flare - unique ID and request ID of file used.
    flare_id = flare_list.FIELD01[i]
    request_id = flare_list.FIELD26[i] 

    ; peak time of flare
    peak_time = flare_list.FIELD04[i]

    ; get the integration time - here 40s
    start_time = atime(anytim(peak_time) - 20)
    end_time = atime(anytim(peak_time) + 20)
    time_range = [start_time, end_time]

    ; science pixel data to use
    path_sci_file = flare_list.FIELD25[i]
    ; auxillary data to use
    aux_fits_file = flare_list.FIELD24[i]

    CATCH, Error_status
    IF Error_status NE 0 THEN BEGIN
      PRINT, 'Error index: ', Error_status
      PRINT, 'Error message: ', !ERROR_STATE.MSG
      openw, 1, './errors_idlout_620keV.csv', /append
      printf, 1, i, !ERROR_STATE.MSG, $
        format='(%"%s,%s")'
      free_lun, 1
      Continue
    ENDIF
    

    get_flare_location, path_sci_file, time_range, aux_fits_file, request_id, flare_id, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, $
       max_bp_coord=max_bp_coord, fitsigmasout_pso=fitsigmasout_pso, stix_max_bp_coord=max_bp_coord_stix, time_shift=time_shift


    ; save the output
    openw, 1, './flarelist_locations_idloutput_620keV.csv', /append
    Printf, 1, STRTRIM(STRING(flare_id),1), time_shift, request_id, flare_loc[0], flare_loc[1], $
               fitsigmasout_pso.srcx, fitsigmasout_pso.srcy, $
               max_bp_coord[0], max_bp_coord[1], $
               max_bp_coord_stix[0], max_bp_coord_stix[1], $
               format='(%"%s,%f,%s,%f,%f,%f,%f,%f,%f,%f,%f")' 
    free_lun, 1
      


ENDFOR
TOC

end
