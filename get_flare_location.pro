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
; 
; CONTACT:
;   hannah.collier@fhnw.ch
;-


pro get_flare_location, path_sci_file, time_range, path_aux_file, req_id, i, flare_loc=flare_loc, vis_fwdfit_pso_map, bp_nat_map=bp_nat_map, $
  max_bp_coord=max_cp_coord, fitsigmasout_pso=fitsigmasout_pso

  aux_data = stx_create_auxiliary_data(path_aux_file, time_range, /silent)

  stx_estimate_flare_location_flare_list, path_sci_file, time_range, aux_data, flare_loc=flare_loc, vis_fwdfit_pso_map=vis_fwdfit_pso_map,  bp_nat_map=bp_nat_map,max_bp_coord=max_bp_coord, $
    fitsigmasout_pso=fitsigmasout_pso, silent=1

  
  filename_fits = 'bp_nat_map-' + STRTRIM(STRING(req_id),1) + '.fits' 

  save_path = './bp_maps/' + filename_fits ; can change the path depending on your setup
  
  stx_map2fits, bp_nat_map, save_path, path_sci_file
  
  filename_csv = 'flare_location_output' + time_range[0].Substring(0,10) + 'T' + time_range[0].Substring(12,13) + time_range[0].Substring(15,16) + time_range[0].Substring(18,19) + '-' + time_range[1].Substring(12,13) + time_range[1].Substring(15,16)  + time_range[1].Substring(18,19) + '-flare_location' + '.csv'
  
  if (i EQ 0) then begin
    write_csv, './flare_location_output.csv', STRTRIM(STRING(req_id),1), flare_loc[0], flare_loc[1], fitsigmasout_pso.srcx, fitsigmasout_pso.srcy, max_bp_coord[0], max_bp_coord[1], header = ['request ID', 'X flare loc', 'Y flare loc', 'FWDFIT X SIGMA', 'FWDFIT Y SIGMA', 'MAX X COORD BP', 'MAX Y COORD BP']
  endif else begin
    openw, 1, './flare_location_output.csv', /append
  
    Printf, 1, STRTRIM(STRING(req_id),1), flare_loc[0], flare_loc[1], fitsigmasout_pso.srcx, fitsigmasout_pso.srcy, max_bp_coord[0], max_bp_coord[1], $
      format='(%"%s, %f, %f, %f, %f, %f, %f")' 
  
    Free_lun, 1
  endelse
  
end

