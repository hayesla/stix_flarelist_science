pro test_catch



flare_list = READ_CSV('stix_flarelist_with_files_lh_test.csv')

for i = 0, 4 do begin
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

	; Catch, theError
	; IF theError NE 0 THEN BEGIN
	; void = cgErrorMsg()
	; Print, 'Bad File: ', thisFile
	; Message, /Reset
	; Continue
	; ENDIF

   CATCH, Error_status
   IF Error_status NE 0 THEN BEGIN

      PRINT, 'Error index: ', Error_status

      PRINT, 'Error message: ', !ERROR_STATE.MSG

      Continue

   ENDIF

 


	get_flare_location, path_sci_file, time_range, aux_fits_file, request_id, flare_id, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, $
   	max_bp_coord=max_bp_coord, fitsigmasout_pso=fitsigmasout_pso, stix_max_bp_coord=max_bp_coord_stix, time_shift=time_shift


	print, "hello"
	endfor
end