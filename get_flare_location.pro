;+
;
; NAME:
;   get_flare_location
;
; PURPOSE:
;   Automatic estimate of the flare location (arcsec, Helioprojective Cartesian coordinates, Solar Orbiter vantange point) and store results to a csv file, and backprojection maps to fits files
;
; CALLING SEQUENCE:
;   pro get_flare_location, path_sci_file, time_range, path_aux_file, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, max_bp_coord=max_cp_coord, fitsigmasout_pso=fitsigmasout_pso

;
; INPUTS:
;   path_sci_file: string containing the path of the science L1 fits file of the event
;
;   time_range: string array containing the selected start and the end time (around thermal peak time)
;
;   aux_data: auxiliary data structure corresponding to the selected time range
;
;
;
; KEYWORDS:
;   flare_loc: output, estimate of the flare location (arcsec, Helioprojective Cartesian coordinates,
;                      Solar Orbiter vantange point)
;
;   vis_fwd_fit_pso_map: fwdfit map structure
;   
;   bp_nat_map: backprojection map structure with natural weighting
;   
;   max_bp_coord: coordinate of max pixel in backprojection map in HPC
;   
;   fit_sigmas_out: sigma values of fwd_fit_pso fit parameters

;
; HISTORY: May 2023, Collier H. FHNW
; July 2023, Hayes, L.A. Updated to remove saving, and return the variables.
; 
; CONTACT:
;   hannah.collier@fhnw.ch
;-
;.r stx_map2fits_test
pro get_flare_location, path_sci_file, time_range, path_aux_file, req_id, flare_id, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, $
  max_bp_coord=max_bp_coord, fitsigmasout_pso=fitsigmasout_pso, stix_max_bp_coord=max_bp_coord_stix, time_shift=time_shift



  aux_data = stx_create_auxiliary_data(path_aux_file, time_range, /silent)

  stx_estimate_flare_location_flare_list, path_sci_file, time_range, aux_data, flare_loc=flare_loc, vis_fwdfit_pso_map=vis_fwdfit_pso_map,  bp_nat_map=bp_nat_map, max_bp_coord=max_bp_coord, stix_max_bp_coord = max_bp_coord_stix, $
    fitsigmasout_pso=fitsigmasout_pso, silent=1

  stx_get_header_corrections, path_sci_file, time_shift = time_shift 
  
  filename_fits = 'bp_nat_map-' + STRTRIM(STRING(req_id),1) + '.fits' 

  save_path = './bp_maps3/' + filename_fits ; can change the path depending on your setup

  stx_map2fits, bp_nat_map, save_path, path_sci_file
  
  ;filename_csv = 'flare_location_output' + time_range[0].Substring(0,10) + 'T' + time_range[0].Substring(12,13) + time_range[0].Substring(15,16) + time_range[0].Substring(18,19) + '-' + time_range[1].Substring(12,13) + time_range[1].Substring(15,16)  + time_range[1].Substring(18,19) + '-flare_location' + '.csv'

  ; handle normal errors
  catch, error
  if error ne 0 then begin
      catch, /cancel
      print, 'A normal error occured: ' + !error_state.msg
      
  endif
  
end


FUNCTION TESTY, path_sci_file, time_range, path_aux_file, time_shift=time_shift
   aux_data = stx_create_auxiliary_data(path_aux_file, time_range, /silent)
   stx_get_header_corrections, path_sci_file, time_shift = time_shift 
    CATCH, Error_status    
    IF Error_status NE 0 THEN BEGIN
        PRINT, 'Error index: ', Error_status
        PRINT, 'Error message: ', !ERROR_STATE.MSG
        CATCH
     ENDIF
  return, aux_data
end