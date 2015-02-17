# import statements
import arcpy
import datetime
import numpy as np
import gc
import csv
import time
from arcpy.sa import *
from itertools import izip

### Import Script Files NJ created ###
import hydrology
import evapotranspiration
#import sediment
import rasterstonumpys


class model_loop(object):
        
    def start_precipition(self, river_catchment_poly, precipitation_textfile, baseflow_textfile, model_start_date, region, elevation_raster, CN2_d, day_pcp_yr, precipitation_gauge_elevation, cell_size, bottom_left_corner, grain_size_list, inactive_layer, remaining_soil_pro_temp_list, grain_pro_temp_list, grain_vol_temp_list, numpy_array_location, use_dinfinity, calculate_sediment, output_file_list, output_excel_discharge, output_excel_sediment, output_format):
         
        # First loop parameter
        first_loop = "True"
        week_day = 0    
        month_day = 0
        year_day = 0
        
        # Set up the discharge location
        if discharge_file_location and discharge_file_location != "#":
            discharge_file_location = discharge_file_location + "/discharge.csv"
            daily_discharge =  open(discharge_file_location, 'wb')
            spamwriter = csv.writer(daily_discharge, delimiter=',')

        # Set up the model start date
        current_date = datetime.datetime.strptime(model_start_date, '%d/%m/%Y')
        
        # Open the precipitation file
        precipitation_read = open(precipitation_textfile)
        arcpy.AddMessage("Temporary files will be located here" + str(numpy_array_location))

        # Check if the user has provided a baseflow textfile and if so combine the data into a new file
        if baseflow_textfile and baseflow_textfile != '#':
           arcpy.AddMessage("Baseflow data detected")
           baseflow_read = open(baseflow_textfile)
           combined_precipitation = open(numpy_array_location + "\combined_precipitation.txt", 'w')

           for precipitation, baseflow in izip(precipitation_read, baseflow_read):
               precipitation = precipitation.strip()
               baseflow = baseflow.strip()
               combined_precipitation.write(precipitation + " " + baseflow + "\n")
           
           # Close the file 
           combined_precipitation.close()

           # Open as the standard precipitation
           precipitation_read = open(numpy_array_location + "\combined_precipitation.txt")
                        
        arcpy.AddMessage("Starting Model...")
        for precipitation in precipitation_read:
            start = time.time()
            arcpy.AddMessage("Today's date is " + str(current_date))
            day_of_year = int(current_date.strftime('%j'))

            if baseflow_textfile and baseflow_textfile != '#':
                precipitation_split = precipitation.split()
                precipitation = precipitation_split[0]
                arcpy.AddMessage("Today precipitation is " + str(precipitation))

                baseflow = precipitation_split[1]
                arcpy.AddMessage("Baseflow is " + str(baseflow))

            ### RECALULATING THE SLOPE DUE TO ELEVATION CHANGE ###
            if day_of_year == 1 or day_of_year % 30 == 0:
                arcpy.AddMessage("-------------------------") 
                arcpy.AddMessage("It is time to recalculate the elevation, slope and flow directions")
                arcpy.AddMessage("-------------------------") 
                if use_dinfinity == 'true':
                    slope, elevation, flow_direction_np, flow_direction_raster, ang = hydrology.SCSCNQsurf().calculate_slope_fraction_flow_direction_dinf(elevation_raster, numpy_array_location)

                else:
                    slope, elevation, flow_direction_np, flow_direction_raster = hydrology.SCSCNQsurf().calculate_slope_fraction_flow_direction_d8(elevation_raster)

                    if baseflow_textfile and baseflow_textfile != '#':
                        # Calculate flow accumulation
                        flow_accumulation = FlowAccumulation(flow_direction_raster)
                        arcpy.AddMessage("Calculated flow accumulation")

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
            
            if baseflow_textfile and baseflow_textfile != '#':  
                baseflow_raster = hydrology.SCSCNQsurf().BaseflowCalculation(baseflow, flow_accumulation)    
                                    
            # Execute Flow accumulation to work out the discharge.
            Q_dis = ((Q_surf_ras / 1000) / 86400) * (cell_size * cell_size) # convert to metres (by dividing by 1000) and then to seconds by dividing by 86400 and finally to the area of the cell by multiplying by the area of the cell. 
            
            if use_dinfinity == 'true':
                outFlowAccumulation = hydrology.SCSCNQsurf().FlowAccumulationDinf(ang, Q_dis, numpy_array_location)   
            else:
                outFlowAccumulation = FlowAccumulation(flow_direction_raster, Q_dis) 
                 
            arcpy.AddMessage("Calculated discharge")   
            
            if baseflow_textfile and baseflow_textfile != '#':
                Q_dis = outFlowAccumulation + baseflow_raster
                    
            Q_dis = arcpy.RasterToNumPyArray(Q_dis, '#','#','#', -9999)

            Q_max = np.amax(Q_dis)
            arcpy.AddMessage("Discharge at the outlet for today is " + str(Q_max))
            arcpy.AddMessage(" ") 
                           
            if calculate_sediment == 'true':
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
            
            # Save date for various layers
            #save_date = str(current_date.strftime('%d_%m_%Y'))
            #outFlowAccumulation.save("Q_surf_dis_" + save_date)
            #baseflow_raster.save("Baseflow_" + save_date)
            
            #total_discharge = outFlowAccumulation + baseflow_raster
            #total_discharge.save("total_q" + save_date)
            ### PEICE OF CODE TO CHECK VALUES COMING OUT OF THE ABOVE PROCESS BY CONVERTING THEM TO RASTERS###
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
            

            ### Check  what needs to be output from the model ###
            # Create a format which says what todays date is
            daily_save_date = str(current_date.strftime('%d_%m_%Y'))
            monthly_save_date = str(current_date.strftime('%m_%Y'))  
            year_save_date = str(current_date.strftime('%Y')) 
            tomorrow = current_date + datetime.timedelta(days=1)
            tomorrow_day = int(tomorrow.strftime('%d'))
            tomorrow_month = int(tomorrow.strftime('%m'))

                            
            if discharge_file_location and discharge_file_location != "#":
                spamwriter.writerow([current_date, Q_max])
                arcpy.AddMessage("Daily Discharge Written to CSV")

            if first_loop == 'True':
                arcpy.AddMessage("First day of operation checking average output rasters")
                for output_type, output_frequency in output_file_list.iteritems():
                    # Check if empty arrays need to be created
                        if str(output_frequency) != 'No output' and str(output_frequency) != 'Daily':                       
                            if output_type == "Runoff": 
                                Q_surf_avg = np.zeros_like(Q_surf)
                                arcpy.AddMessage(output_type + " raster created")
                            if output_type == "Discharge": 
                                Q_dis_avg = np.zeros_like(Q_surf)
                                arcpy.AddMessage(output_type + " raster created")
                            if output_type == "Depth": 
                                depth_avg = np.zeros_like(Q_surf)
                                arcpy.AddMessage(output_type + " raster created")
                            if output_type == "Spatial precipitation": 
                                precipitation_avg = np.zeros_like(Q_surf)
                                arcpy.AddMessage(output_type + " raster created")
                            if output_type == "Sediment depth": 
                                sed_depth_avg = np.zeros_like(Q_surf)
                                arcpy.AddMessage(output_type + " raster created")
                            if output_type ==  "Sediment eroision/deposition": 
                                sed_erosion_deposition_avg = np.zeros_like(Q_surf)
                                arcpy.AddMessage(output_type + " raster created")

            # Add one onto the weekly/monthly/yearly day counter
            week_day = week_day + 1
            month_day = month_day + 1
            year_day = year_day + 1

            for output_type, output_frequency in output_file_list.iteritems():
                # What to do if the output is daily
                if output_frequency == 'Daily':
                    if output_type == "Runoff": 
                        rasterstonumpys.convert_numpy_to_raster_single(Q_surf, output_type, bottom_left_corner, cell_size, daily_save_date)
                    if output_type == "Discharge": 
                        rasterstonumpys.convert_numpy_to_raster_single(Q_dis, output_type, bottom_left_corner, cell_size, daily_save_date)
                    if output_type == "Depth": 
                        rasterstonumpys.convert_numpy_to_raster_single(depth_recking, output_type, bottom_left_corner, cell_size, daily_save_date)
                    if output_type == "Spatial precipitation": 
                        rasterstonumpys.convert_numpy_to_raster_single(precipitation, output_type, bottom_left_corner, cell_size, daily_save_date)
                    if output_type == "Sediment depth": 
                        rasterstonumpys.convert_numpy_to_raster_single(Q_surf, output_type, bottom_left_corner, cell_size, daily_save_date) # Need to change output
                    if output_type ==  "Sediment eroision/deposition": 
                        rasterstonumpys.convert_numpy_to_raster_single(Q_surf, output_type, bottom_left_corner, cell_size, daily_save_date) # Need to change output
                
                # What happens if the output is weekly
                if output_frequency == 'Weekly':                   
                    if output_type == "Runoff":
                        arcpy.AddMessage("Runoff added to weekly average")
                        Q_surf_avg = Q_surf_avg + Q_surf

                    if output_type == "Discharge":
                        arcpy.AddMessage("Discharge added to weekly average")
                        Q_dis_avg = Q_dis_avg + Q_dis

                    if output_type == "Depth":
                        arcpy.AddMessage("Depth added to weekly average")
                        depth_avg = depth_avg + depth_recking

                    if output_type == "Spatial precipitation":
                        arcpy.AddMessage("Spatial precipitation added to weekly average")
                        precipitation_avg = precipitation_avg + precipitation

                    if output_type == "Sediment depth":
                        arcpy.AddMessage("Sediment depth added to weekly average")
                        sed_depth_avg = sed_depth_avg + Q_surf # need to change Q_surf

                    if output_type == "Sediment eroision/deposition":
                        arcpy.AddMessage("Sediment eroision/deposition added to weekly average")
                        sed_erosion_deposition_avg = sed_erosion_deposition_avg + Q_surf # need to change Q_surf

                    if week_day == 7:
                        if output_format == 'Daily average':
                            arcpy.AddMessage("Weekly average selected")
                            if output_type == "Runoff": 
                                arcpy.AddMessage("Saving weekly runoff average")
                                Q_surf_avg = Q_surf_avg / 7
                                Q_surf_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                                Q_surf_avg = np.zeros_like(Q_surf_avg)

                            if output_type == "Discharge": 
                                arcpy.AddMessage("Saving weekly discharge average")
                                Q_dis_avg = Q_dis_avg / 7
                                Q_dis_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                                Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                            if output_type == "Depth": 
                                arcpy.AddMessage("Saving weekly depth average")
                                depth_avg = depth_avg / 7
                                depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                depth_avg = np.zeros_like(depth_avg)

                            if output_type == "Spatial precipitation": 
                                arcpy.AddMessage("Saving weekly spatial precipitation average")
                                precipitation_avg = precipitation_avg / 7
                                precipitation_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, save_date)
                                precipitation_avg = np.zeros_like(precipitation_avg)

                            if output_type == "Sediment depth": 
                                arcpy.AddMessage("Saving weekly sediment depth average")
                                sed_depth_avg = sed_depth_avg / 7
                                sed_depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_depth_avg = np.zeros_like(sed_depth_avg)

                            if output_type ==  "Sediment eroision/deposition": 
                                arcpy.AddMessage("Saving weekly sediment eroision/deposition average")
                                sed_erosion_deposition_avg = sed_erosion_deposition_avg / 7
                                sed_erosion_deposition_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)

                        elif output_format == 'Total':
                            arcpy.AddMessage("Weekly total selected")
                            if output_type == "Runoff": 
                                arcpy.AddMessage("Saving weekly runoff total")
                                Q_surf_avg = Q_surf_avg
                                Q_surf_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                                Q_surf_avg = np.zeros_like(Q_surf_avg)

                            if output_type == "Discharge": 
                                arcpy.AddMessage("Saving weekly discharge total")
                                Q_dis_avg = Q_dis_avg
                                Q_dis_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                                Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                            if output_type == "Depth": 
                                arcpy.AddMessage("Saving weekly depth total")
                                depth_avg = depth_avg
                                depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                depth_avg = np.zeros_like(depth_avg)

                            if output_type == "Spatial precipitation": 
                                arcpy.AddMessage("Saving weekly spatial precipitation total")
                                precipitation_avg = precipitation_avg
                                precipitation_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, save_date)
                                precipitation_avg = np.zeros_like(precipitation_avg)

                            if output_type == "Sediment depth": 
                                arcpy.AddMessage("Saving weekly sediment depth total")
                                sed_depth_avg = sed_depth_avg
                                sed_depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_depth_avg = np.zeros_like(sed_depth_avg)

                            if output_type ==  "Sediment eroision/deposition": 
                                arcpy.AddMessage("Saving weekly sediment eroision/deposition total")
                                sed_erosion_deposition_avg = sed_erosion_deposition_avg
                                sed_erosion_deposition_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)


                # What happens if the output is monthly
                if output_frequency == 'Monthly':
                    arcpy.AddMessage("Tomorrow will be day " + str(tomorrow_day))                   
                    if output_type == "Runoff":
                        arcpy.AddMessage("Runoff added to monthly average")
                        Q_surf_avg = Q_surf_avg + Q_surf

                    if output_type == "Discharge":
                        arcpy.AddMessage("Discharge added to monthly average")
                        Q_dis_avg = Q_dis_avg + Q_dis

                    if output_type == "Depth":
                        arcpy.AddMessage("Depth added to monthly average")
                        depth_avg = depth_avg + depth_recking

                    if output_type == "Spatial precipitation":
                        arcpy.AddMessage("Spatial precipitation added to monthly average")
                        precipitation_avg = precipitation_avg + precipitation

                    if output_type == "Sediment depth":
                        arcpy.AddMessage("Sediment depth added to monthly average")
                        sed_depth_avg = sed_depth_avg + Q_surf # need to change Q_surf

                    if output_type == "Sediment eroision/deposition":
                        arcpy.AddMessage("Sediment eroision/deposition added to monthly average")
                        sed_erosion_deposition_avg = sed_erosion_deposition_avg + Q_surf # need to change Q_surf
                    
                    if tomorrow_day == 1:
                        if output_format == 'Daily average':
                            arcpy.AddMessage("Monthly average selected")
                            if output_type == "Runoff": 
                                arcpy.AddMessage("Saving monthly runoff average")
                                Q_surf_avg = Q_surf_avg / month_day
                                Q_surf_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, save_date)
                                Q_surf_avg = np.zeros_like(Q_surf_avg)

                            if output_type == "Discharge": 
                                arcpy.AddMessage("Saving monthly discharge average")
                                Q_dis_avg = Q_dis_avg / month_day
                                Q_dis_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, save_date)
                                Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                            if output_type == "Depth": 
                                arcpy.AddMessage("Saving monthly depth average")
                                depth_avg = depth_avg / month_day
                                depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                depth_avg = np.zeros_like(depth_avg)

                            if output_type == "Spatial precipitation": 
                                arcpy.AddMessage("Saving spatial precipitation average")
                                precipitation_avg = precipitation_avg / month_day
                                precipitation_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, save_date)
                                precipitation_avg = np.zeros_like(precipitation_avg)

                            if output_type == "Sediment depth": 
                                arcpy.AddMessage("Saving monthly sediment depth average")
                                sed_depth_avg = sed_depth_avg / month_day
                                sed_depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_depth_avg = np.zeros_like(sed_depth_avg)

                            if output_type ==  "Sediment eroision/deposition": 
                                arcpy.AddMessage("Saving monthly sediment eroision/deposition average")
                                sed_erosion_deposition_avg = sed_erosion_deposition_avg / month_day
                                sed_erosion_deposition_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)
                        
                        elif output_format == 'Total':
                            arcpy.AddMessage("Monthly total selected")
                            if output_type == "Runoff": 
                                arcpy.AddMessage("Saving monthly runoff total")
                                Q_surf_avg = Q_surf_avg 
                                Q_surf_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, save_date)
                                Q_surf_avg = np.zeros_like(Q_surf_avg)

                            if output_type == "Discharge": 
                                arcpy.AddMessage("Saving monthly discharge total")
                                Q_dis_avg = Q_dis_avg 
                                Q_dis_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, save_date)
                                Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                            if output_type == "Depth": 
                                arcpy.AddMessage("Saving monthly depth total")
                                depth_avg = depth_avg 
                                depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                depth_avg = np.zeros_like(depth_avg)

                            if output_type == "Spatial precipitation": 
                                arcpy.AddMessage("Saving spatial precipitation total")
                                precipitation_avg = precipitation_avg 
                                precipitation_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, save_date)
                                precipitation_avg = np.zeros_like(precipitation_avg)

                            if output_type == "Sediment depth": 
                                arcpy.AddMessage("Saving monthly sediment depth total")
                                sed_depth_avg = sed_depth_avg 
                                sed_depth_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_depth_avg = np.zeros_like(sed_depth_avg)

                            if output_type ==  "Sediment eroision/deposition": 
                                arcpy.AddMessage("Saving monthly sediment eroision/deposition total")
                                sed_erosion_deposition_avg = sed_erosion_deposition_avg 
                                sed_erosion_deposition_avg[CN2_d == -9999] = -9999
                                rasterstonumpys.convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, save_date)
                                sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)


                    # What happens if the output is yearly
                    if output_frequency == 'Yearly':
                        arcpy.AddMessage("Tomorrow will be day " + str(tomorrow_day) + "and month will be " + str(tomorrow_month))                   
                    
                        if output_type == "Runoff":
                            arcpy.AddMessage("Runoff added to yearly average")
                            Q_surf_avg = Q_surf_avg + Q_surf

                        if output_type == "Discharge":
                            arcpy.AddMessage("Discharge added to yearly average")
                            Q_dis_avg = Q_dis_avg + Q_dis

                        if output_type == "Depth":
                            arcpy.AddMessage("Depth added to yearly average")
                            depth_avg = depth_avg + depth_recking

                        if output_type == "Spatial precipitation":
                            arcpy.AddMessage("Spatial precipitation added to yearly average")
                            precipitation_avg = precipitation_avg + precipitation

                        if output_type == "Sediment depth":
                            arcpy.AddMessage("Sediment depth added to yearly average")
                            sed_depth_avg = sed_depth_avg + Q_surf # need to change Q_surf

                        if output_type == "Sediment eroision/deposition":
                            arcpy.AddMessage("Sediment eroision/deposition added to yearly average")
                            sed_erosion_deposition_avg = sed_erosion_deposition_avg + Q_surf # need to change Q_surf
                    
                        if tomorrow_day == 1 and tomorrow_month == 1:
                            if output_format == 'Daily average':
                                arcpy.AddMessage("Yearly average selected")
                                if output_type == "Runoff": 
                                    arcpy.AddMessage("Saving Yearly runoff average")
                                    Q_surf_avg = Q_surf_avg / year_day
                                    Q_surf_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    Q_surf_avg = np.zeros_like(Q_surf_avg)

                                if output_type == "Discharge": 
                                    arcpy.AddMessage("Saving Yearly discharge average")
                                    Q_dis_avg = Q_dis_avg / year_day
                                    Q_dis_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                                if output_type == "Depth": 
                                    arcpy.AddMessage("Saving Yearly depth average")
                                    depth_avg = depth_avg / year_day
                                    depth_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    depth_avg = np.zeros_like(depth_avg)

                                if output_type == "Spatial precipitation": 
                                    arcpy.AddMessage("Saving spatial precipitation Yearly average")
                                    precipitation_avg = precipitation_avg / year_day
                                    precipitation_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    precipitation_avg = np.zeros_like(precipitation_avg)

                                if output_type == "Sediment depth": 
                                    arcpy.AddMessage("Saving Yearly sediment depth average")
                                    sed_depth_avg = sed_depth_avg / year_day
                                    sed_depth_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    sed_depth_avg = np.zeros_like(sed_depth_avg)

                                if output_type ==  "Sediment eroision/deposition": 
                                    arcpy.AddMessage("Saving Yearlysediment eroision/deposition average")
                                    sed_erosion_deposition_avg = sed_erosion_deposition_avg / year_day
                                    sed_erosion_deposition_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)

                            elif output_format == 'Total':
                                arcpy.AddMessage("Yearly total selected")
                                if output_type == "Runoff": 
                                    arcpy.AddMessage("Saving yearly runoff total")
                                    Q_surf_avg = Q_surf_avg 
                                    Q_surf_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    Q_surf_avg = np.zeros_like(Q_surf_avg)

                                if output_type == "Discharge": 
                                    arcpy.AddMessage("Saving yearly discharge total")
                                    Q_dis_avg = Q_dis_avg 
                                    Q_dis_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                                if output_type == "Depth": 
                                    arcpy.AddMessage("Saving yearly depth total")
                                    depth_avg = depth_avg 
                                    depth_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    depth_avg = np.zeros_like(depth_avg)

                                if output_type == "Spatial precipitation": 
                                    arcpy.AddMessage("Saving yearly precipitation total")
                                    precipitation_avg = precipitation_avg 
                                    precipitation_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    precipitation_avg = np.zeros_like(precipitation_avg)

                                if output_type == "Sediment depth": 
                                    arcpy.AddMessage("Saving yearly sediment depth total")
                                    sed_depth_avg = sed_depth_avg 
                                    sed_depth_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    sed_depth_avg = np.zeros_like(sed_depth_avg)

                                if output_type ==  "Sediment eroision/deposition": 
                                    arcpy.AddMessage("Saving yearly sediment eroision/deposition total")
                                    sed_erosion_deposition_avg = sed_erosion_deposition_avg 
                                    sed_erosion_deposition_avg[CN2_d == -9999] = -9999
                                    rasterstonumpys.convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                                    sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)

            # Counter resets
            if week_day == 7:
                week_day = 0
                arcpy.AddMessage("Week complete resetting output counter")

            if tomorrow_day == 1:
                month_day = 0
                arcpy.AddMessage("Month complete resetting output counter")
            
            if tomorrow_day == 1 and tomorrow_month == 1:
                year_day = 0
                arcpy.AddMessage("Year complete resetting output counter")


            ### VARIABLES / PARAMETERS THAT CHANGE AT END OF LOOP ###
            # Scurr becomes Sprev
            Sprev = Scurr
            first_loop = "False"

            # Increment the date and day by 1
            current_date = current_date + datetime.timedelta(days=1)
            day_of_year += 1
            arcpy.AddMessage("Time to complete today is " + str(round(time.time() - start,2)) + "s. Note that on day 1 and every 30 days the timestep will take longer.")
            arcpy.AddMessage("-------------------------") 
            gc.collect()



            ### UNUSED CODE TO READD LATER ###
            # Set up sediment loop save location
            '''if discharge_file_location and discharge_file_location != "#":
                sediment_loop_time = discharge_file_location + "/loop_time.csv"
                daily_sed_loop =  open(sediment_loop_time, 'wb')
                spamwriter_sed = csv.writer(daily_sed_loop, delimiter=',')

            )'''