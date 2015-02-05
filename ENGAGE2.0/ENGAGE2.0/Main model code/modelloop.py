# import statements
import arcpy
import datetime
import numpy as np
import gc
import csv
import time
from arcpy.sa import *

### Import Script Files NJ created ###
import hydrology
import evapotranspiration
import sediment
import rasterstonumpys


class model_loop(object):
        
    def start_precipition(self, river_catchment_poly, precipitation_textfile, model_start_date, region, discharge_file_location, elevation_raster, CN2_d, day_pcp_yr, precipitation_gauge_elevation, cell_size, bottom_left_corner, grain_size_list, inactive_layer, remaining_soil_pro_temp_list, grain_pro_temp_list, grain_vol_temp_list, numpy_array_location, use_dinfinity):
         
        # First loop parameter
        first_loop = "True"
               
        # Set up the model start date
        current_date = datetime.datetime.strptime(model_start_date, '%d/%m/%Y')
        
        # Open the precipitation file
        precipitation_read = open(precipitation_textfile)
        
        # Set up sediment loop save location
        if discharge_file_location and discharge_file_location != "#":
            sediment_loop_time = discharge_file_location + "/loop_time.csv"
            daily_sed_loop =  open(sediment_loop_time, 'wb')
            spamwriter_sed = csv.writer(daily_sed_loop, delimiter=',')

        # Set up the discharge location
        if discharge_file_location and discharge_file_location != "#":
            discharge_file_location = discharge_file_location + "/discharge.csv"
            daily_discharge =  open(discharge_file_location, 'wb')
            spamwriter = csv.writer(daily_discharge, delimiter=',')

        arcpy.AddMessage("Starting Model...")
        for precipitation in precipitation_read:
            start = time.time()
            arcpy.AddMessage("Today's date is " + str(current_date))
            day_of_year = int(current_date.strftime('%j'))

            ### RECALULATING THE SLOPE DUE TO ELEVATION CHANGE ###
            if day_of_year == 1 or day_of_year % 30 == 0:
                arcpy.AddMessage("-------------------------") 
                arcpy.AddMessage("It is time to recalculate the elevation, slope and flow directions")
                arcpy.AddMessage("-------------------------") 
                if use_dinfinity == 'true':
                    slope, elevation, flow_direction_np, flow_direction_raster, ang = hydrology.SCSCNQsurf().calculate_slope_fraction_flow_direction_dinf(elevation_raster, numpy_array_location)

                else:
                    slope, elevation, flow_direction_np, flow_direction_raster = hydrology.SCSCNQsurf().calculate_slope_fraction_flow_direction_d8(elevation_raster)
                arcpy.AddMessage("-------------------------") 
                arcpy.AddMessage("New elevation, slope and flow directions calculated")
                arcpy.AddMessage("-------------------------") 

                # Calculate CN1_numbers and CN3_numbers adjusted for antecedent conditions
                CN2s_d, CN1s_d, CN3s_d = hydrology.SCSCNQsurf().combineSCSCN(CN2_d, slope)

            if day_of_year == 1 and first_loop == "True":
                # Set a 0 value for Sprev
                Sprev = np.zeros_like(elevation)
                         
            ### HYDROLOGY SECTION OF LOOP###
            # Calculate the daily precipitation in each grid cell
            precipitation = hydrology.SCSCNQsurf().spatial_uniform_spatial_precip(precipitation, elevation, day_pcp_yr, precipitation_gauge_elevation)
            
            # Calculate the surface runoff in each grid cell (Not fatoring in antecedent conditions
            Q_surf = hydrology.SCSCNQsurf().OldQsurf(precipitation, CN2s_d)    
            
            # Calculate the mean, max and min temperatures. The latitude and feed those into the evapotranspiration calculation
            mean_temp, max_temp, min_temp = evapotranspiration.Evapotranspiration().MinMaxMeanTemp(region, current_date)
            latitude = evapotranspiration.Evapotranspiration().UKlatituderadians(region, river_catchment_poly)
            ETo = evapotranspiration.Evapotranspiration().ReferenceEvapotranspiration(latitude, day_of_year, max_temp, min_temp, mean_temp) # need to define lat
            
            # Calculate the retention parameter (Antecedent Conditions and Evapotranspiration
            Scurr = hydrology.SCSCNQsurf().RententionParameter(precipitation, CN1s_d, CN2_d, CN2s_d, ETo, Sprev, Q_surf, first_loop)
            
            # Calculate surface runoff and then convert to raster
            Q_surf = hydrology.SCSCNQsurf().SurfSCS(precipitation, Scurr, CN2s_d)
            Q_surf_ras = arcpy.NumPyArrayToRaster(Q_surf, bottom_left_corner, cell_size, cell_size, -9999)
                                    
            # Execute Flow accumulation to work out the discharge.
            Q_dis = ((Q_surf_ras / 1000) / 86400) * (cell_size * cell_size) # convert to metres (by dividing by 1000) and then to seconds by dividing by 86400 and finally to the area of the cell by multiplying by the area of the cell. 
            
            if use_dinfinity == 'true':
                outFlowAccumulation = hydrology.SCSCNQsurf().FlowAccumulationDinf(ang, Q_dis, numpy_array_location)   
            else:
                outFlowAccumulation = FlowAccumulation(flow_direction_raster, Q_dis) 
                 
            arcpy.AddMessage("Calculated discharge")           
            Q_dis = arcpy.RasterToNumPyArray(outFlowAccumulation, '#','#','#', -9999)
            Q_max = np.amax(Q_dis)

            arcpy.AddMessage("Discharge at the outlet for today is " + str(Q_max))
            arcpy.AddMessage(" ") 

            if discharge_file_location and discharge_file_location != "#":
                spamwriter.writerow([current_date, Q_max])
                arcpy.AddMessage("Daily Discharge Written to CSV")
     
                           
'''
            ###SEDIMENT TRANSPORT SECTION OF LOOP###
            # Calculate d50, d84, Fs
            d50, d84, Fs = sediment.sedimenttransport().d50_d84_Fs_grain(grain_size_list, grain_pro_temp_list)
            
            # Calculate depth using the recking parameters and the indexs of the cells with a depth greater than the threshold (cell_size / 1000)
            depth_recking, new_idx = sediment.sedimenttransport().depth_recking(Q_dis, slope, d84, cell_size)

            # Calculate the timestep of the sediment transport using the maximum rate of entrainment in all the cells
            sediment_time_step_seconds = sediment.sedimenttransport().SedimentEntrainmentQmax(new_idx, slope, depth_recking, Fs, d50, cell_size, grain_size_list, grain_pro_temp_list)
            
            if sediment_time_step_seconds >= 86400:
                sediment_time_step_seconds = 86400

            ### Piece of code to record the timestep ###
            arcpy.AddMessage("Sediment timestep for today is  " + str(sediment_time_step_seconds))

            #if sediment_loop_time and sediment_loop_time != "#":
                #spamwriter_sed.writerow([current_date, sediment_time_step_seconds])
                #arcpy.AddMessage("Daily sediment timestep written to CSV")
                        
            # Collect garbage
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 
            
            
            # Save date for various layers
            save_date = str(current_date.strftime('%d_%m_%Y'))
                         
            # Calculate sediment transport for each timestep based on the above calculation
            sediment.sedimenttransport().sediment_loop(sediment_time_step_seconds, grain_size_list, Q_dis, slope, cell_size, flow_direction_np, bottom_left_corner, save_date, grain_pro_temp_list, grain_vol_temp_list, inactive_layer, remaining_soil_pro_temp_list)
            


            ### PEICE OF CODE TO CHECK VALUES COMING OUT OF THE ABOVE PROCESS BY CONVERTING THEM TO RASTERS###
            # Save date for various layers
            save_date = str(current_date.strftime('%d_%m_%Y'))

            #list_of_grain_volumes = {"total_volume": total_volume, "total_change": total_change}
            #list_of_hydrology_numpys = {"CN2_d": CN2_d, "precipitation": precipitation, "slope": slope, "CN2s_d": CN2s_d, "CN1s_d": CN1s_d, "CN3s_d": CN3s_d, "Q_surf": Q_surf, "Scurr": Scurr, "Q_dis": Q_dis}
            #list_of_other_layers = {"active_layer": active_layer, "inactive_layer": inactive_layer}
            #list_of_sediment_timestep_numpys = {"d50": d50, "d84": d84, "Fs": Fs, "depth": depth_recking}
            #list_grain_volumes = {"grain_vol_1": grain_size_volumes[0], "grain_vol_2": grain_size_volumes[1], "grain_vol_3": grain_size_volumes[2], "grain_vol_4": grain_size_volumes[3], "grain_vol_5": grain_size_volumes[4], "grain_vol_6": grain_size_volumes[5], "grain_vol_7": grain_size_volumes[6]}
            #list_grain_pro = {"grain_pro_1": grain_size_proportions[0], "grain_pro_2": grain_size_proportions[1], "grain_pro_3": grain_size_proportions[2], "grain_pro_4": grain_size_proportions[3], "grain_pro_5": grain_size_proportions[4], "grain_pro_6": grain_size_proportions[5], "grain_pro_7": grain_size_proportions[6]}
            #rasterstonumpys.convert_numpy_to_raster(list_of_hydrology_numpys, bottom_left_corner, cell_size, save_date)
            #rasterstonumpys.convert_numpy_to_raster(list_of_sediment_timestep_numpys, bottom_left_corner, cell_size, save_date)
            #rasterstonumpys.convert_numpy_to_raster(list_of_other_layers, bottom_left_corner, cell_size, save_date)
            #rasterstonumpys.convert_numpy_to_raster(list_grain_volumes, bottom_left_corner, cell_size, save_date)
            #rasterstonumpys.convert_numpy_to_raster(list_grain_pro, bottom_left_corner, cell_size, save_date)
            #rasterstonumpys.convert_numpy_to_raster(list_of_grain_volumes, bottom_left_corner, cell_size, save_date)
            
            ### VARIABLES / PARAMETERS THAT CHANGE AT END OF LOOP ###
            # Scurr becomes Sprev
            Sprev = Scurr
            first_loop = "False"

            # Increment the date and day by 1
            current_date = current_date + datetime.timedelta(days=1)
            day_of_year += 1
            arcpy.AddMessage("Time to complete today is " + str(round(time.time() - start,2)) + "s. Note that on day 1 and every 30 days the timestep will take longer.")
            arcpy.AddMessage("-------------------------") 
            gc.collect()'''