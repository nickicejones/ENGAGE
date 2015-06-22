###### MODEL LOOP DESCRIPTION #####
# The purpose of this file is to carry out all the daily processes that are required

##### VARIABLES - used in this file #####
# numpy_array_location - this is the location on the computer where hard copies of the numpy arrays can be stored.

### MODEL INPUTS ###
# precipitation_textfile - textfile containing daily precipitation
# model_start_date - date of start of the models operation
# region - region for evapotranspiration calculation - Choice of the following - ["Scotland N", "Scotland E", "Scotland W", "England E & NE", "England NW/ Wales N",
# "Midlands", "East Anglia", "England SW/ Wales S", "England SE/ Central S"] 
# precipitation_gauge_elevation - elevation of the precipiation gauge #OPTIONAL
# calculate_sediment - select whether or not the model calculates sediment

### MODEL OUTPUTS - CSV ###
# output_excel_discharge - output daily discharge at the pour point 
# output_excel_sediment - output daily sediment yeild at the pour point
# output_file_dict - dict to print out the select outputs to user

### GRAINSIZES ###
# GS_list - list of 7 grainsizes 

### OTHER MODEL INPUTS ###
# DTM - Digital terrain model of the river catchment
# land_cover - land cover of the river catchment
# land_cover_type - land cover type - LCM or CORINE
# soil - soil hydrology of the river catchment
# soil_type - soil hydrology type - HOST or FAO
# GS_1_P - grain size 1 proportion
# GS_2_P - grain size 2 proportion
# GS_3_P - grain size 3 proportion 
# GS_4_P - grain size 4 proportion 
# GS_5_P - grain size 5 proportion
# GS_6_P - grain size 6 proportion
# GS_7_P - grain size 7 proportion
# GS_P_list - list of grain size proportions / these are rasters and then converted to numpy arrays
# river_soil_depth - river soil depth, this has been taken from the BGS data
# river_catchment - polygon shapefile of the river catchment
# model_inputs_list - list of other model inputs - DTM, land cover and soil hydrology / these are rasters and then converted to numpy arrays

##### VARIABLES CREATED THROUGH MODEL PROCESSES #####
# active_layer - the top 20 metres squared of the soil in the river channel that is considered to be actively available for transport (units are in metres squared)
# inactive_layer - the remaining soil depth left in the river channel and is not considered to be avaliable for transport (units are in metres squared)
# active_layer_GS_volumes - list containing the volumes of each of the grainsizes in the active layer
# inactive_layer_GS_volumes - list containing the volumes of each of the grainsizes in the inactive layer 
# day_pcp_yr - average number of days precipitation falling in the river catchment
# active_layer_GS_P_temp - list of temporary locations on the computer to store the active layer grain size proportions
# active_layer_V_temp - list of temporary locations on the computer to store the active layer grain size volumes
# inactive_layer_GS_P_temp - list of  temporary locations on the computer to store the inactive layer grain size proportions
# inactive_layer_V_temp - list of temporary location ons the computer to store the inactive layer grain size volumes
# CN2_d - Curve number 2 for that soil hydrology type and land cover (this is at 5% slope)
# self.first_loop - true/ false statement only needed in first loop
# self.current_date - the current day of model simulation in the format d/m/yyyyy    
# self.cell_size - the cell size of the model
# self.bottom_left_corner - the bottom left hand corner of the input rasters
# self.calculate_sediment = calculate_sediment 
# self.use_dinfinity - - whether or not the user has installed taudem so they can use dinfinity flow accumulation
# self.week_day - counter for day of the week  
# self.month_day - counter for day of the month  
# self.year_day - counter for day of the year  
# self.day_of_year - counter for day of the year  





#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
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
import sediment
import rasterstonumpys
import elevation_adjustment


class model_loop(object):
  
    def __init__(self, model_start_date, cell_size, bottom_left_corner, calculate_sediment, use_dinfinity):
        self.first_loop = True
        self.current_date = datetime.datetime.strptime(model_start_date, '%d/%m/%Y')       
        self.cell_size = cell_size
        self.bottom_left_corner = bottom_left_corner
        self.calculate_sediment = calculate_sediment 
        self.use_dinfinity = use_dinfinity
        self.week_day = 0    
        self.month_day = 0
        self.year_day = 0
        self.day_of_year = 0
        
    def start_precipition(self, river_catchment, DTM, region, precipitation_textfile, 
                          baseflow_provided, day_pcp_yr, precipitation_gauge_elevation, 
                          CN2_d, GS_list, active_layer, inactive_layer, 
                          active_layer_GS_P_temp, active_layer_V_temp, 
                          inactive_layer_GS_P_temp, inactive_layer_V_temp, 
                          numpy_array_location, output_file_dict, output_format, 
                          output_excel_discharge, output_excel_sediment):
                          
        # Check to see if the user wants to output discharge / sediment loss from the system
        discharge_spamwriter, sediment_spamwriter = rasterstonumpys.save_discharge_or_sediment_csv(output_excel_discharge, output_excel_sediment)
        
        # Open the precipitation file
        precipitation_read = open(precipitation_textfile)
        
        ### Set to default for the first loop ###
        recalculate_slope_flow = True

        ##### Daily loop start #####     
        arcpy.AddMessage("Starting Model...")
        for precipitation in precipitation_read:
            start = time.time()
            arcpy.AddMessage("Today's date is " + str(self.current_date))
            self.day_of_year = int(self.current_date.strftime('%j'))
            
            
            ### CHECK TO SEE IF BASEFLOW NEEDS TO BE SEPERATED ###
            precipitation, baseflow = hydrology.SCSCNQsurf().check_baseflow(precipitation, baseflow_provided)
            

            ### CHECK TO SEE IF THE SLOPE NEEDS TO BE CALCULATED ###
            
            if recalculate_slope_flow == True and self.first_loop == False: 
                arcpy.AddMessage("Recalculating variables due to degree of elevation change")
                print DTM
                print flow_direction_np
                print slope
                                 
                                                               
                slope, DTM, flow_direction_np, flow_direction_raster, flow_accumulation, CN2s_d, CN1s_d, CN3s_d, ang = hydrology.SCSCNQsurf().check_slope_flow_directions(self.first_loop, self.use_dinfinity, self.day_of_year, CN2_d, DTM, baseflow_provided, numpy_array_location)   
                            
            if self.first_loop == True:
                arcpy.AddMessage("Calculating variables for the first loop")
                                               
                slope, DTM, flow_direction_np, flow_direction_raster, flow_accumulation, CN2s_d, CN1s_d, CN3s_d, ang = hydrology.SCSCNQsurf().check_slope_flow_directions(self.first_loop, self.use_dinfinity, self.day_of_year, CN2_d, DTM, baseflow_provided, numpy_array_location)  
                DTM_MINUS_AL_IAL = elevation_adjustment.get_DTM_AL_IAL(DTM, active_layer, inactive_layer, self.cell_size) 
                # change the inactive layer to m3
                inactive_layer *= (self.cell_size*self.cell_size) 

                
                


            flow_np = rasterstonumpys.convert_raster_to_numpy([flow_accumulation])

            print flow_np
            print DTM
            print flow_direction_np
            print slope
                                                                          
            ##### HYDROLOGY SECTION OF LOOP #####
            # Calculate the daily precipitation in each grid cell
            precipitation = hydrology.SCSCNQsurf().spatial_uniform_spatial_precip(precipitation, DTM, day_pcp_yr, precipitation_gauge_elevation)
            
            # Calculate the surface runoff in each grid cell (Not fatoring in antecedent conditions
            Q_surf = hydrology.SCSCNQsurf().OldQsurf(precipitation, CN2s_d)    
            
            # Calculate the mean, max and min temperatures. The latitude and feed those into the evapotranspiration calculation ~~~~~~##### GOT HERE #####~~~~~~#
            mean_temp, max_temp, min_temp = evapotranspiration.Evapotranspiration().MinMaxMeanTemp(region, self.current_date)
            latitude = evapotranspiration.Evapotranspiration().UKlatituderadians(region, river_catchment)
            ETo = evapotranspiration.Evapotranspiration().ReferenceEvapotranspiration(latitude, self.day_of_year, max_temp, min_temp, mean_temp) # need to define lat
            
            # Check if this is the first loop of the models operation
            if self.first_loop == True:
                
                # Set a 0 value for Sprev
                Sprev = np.zeros_like(DTM)

            # Calculate the retention parameter (Antecedent Conditions and Evapotranspiration)
            Scurr = hydrology.SCSCNQsurf().RententionParameter(precipitation, CN1s_d, CN2_d, CN2s_d, ETo, Sprev, Q_surf, self.first_loop)
                      
            # Calculate surface runoff and then convert to raster
            Q_surf_np = hydrology.SCSCNQsurf().SurfSCS(precipitation, Scurr, CN2s_d)
            Q_surf = arcpy.NumPyArrayToRaster(Q_surf_np, self.bottom_left_corner, self.cell_size, self.cell_size, -9999)
                                                                    
            # Execute Flow accumulation to work out the discharge.
            Q_dis = ((Q_surf / 1000) / 86400) * (self.cell_size * self.cell_size) # convert to metres (by dividing by 1000) and then to seconds by dividing by 86400 and finally to the area of the cell by multiplying by the area of the cell. 
            

            if self.use_dinfinity == True:
                Q_dis = hydrology.SCSCNQsurf().FlowAccumulationDinf(ang, Q_dis, numpy_array_location)   
            else:
                Q_dis = FlowAccumulation(flow_direction_raster, Q_dis)                                          
            arcpy.AddMessage("Calculated discharge")   
            
            if baseflow_provided == True:
                baseflow_raster = hydrology.SCSCNQsurf().BaseflowCalculation(baseflow, flow_accumulation)                                  
                Q_dis = Q_dis + baseflow_raster
                                                
            Q_dis = arcpy.RasterToNumPyArray(Q_dis, '#','#','#', -9999)
            
            Q_max = np.amax(Q_dis)
            arcpy.AddMessage("Discharge at the outlet for today is " + str(Q_max))
            arcpy.AddMessage(" ") 

            # If the user has selected to output the daily discharge value at the bottom of the catchment write that value to the excel               
            rasterstonumpys.output_discharge_csv(self.current_date, discharge_spamwriter, Q_max)
            
            # Scurr becomes Sprev
            Sprev = Scurr

            ### HYDROLOGY GARBAGE COLLECTION ###
            del flow_direction_raster, flow_accumulation, CN2s_d, CN1s_d, CN3s_d, baseflow_raster, Scurr
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 


            ###SEDIMENT TRANSPORT SECTION OF LOOP###                         
            if self.calculate_sediment == True: 
                arcpy.AddMessage("Starting to calculate sediment transport...")              
                # Calculate d50, d84, Fs
                d50, d84, Fs, active_layer_GS_P_list = sediment.sedimenttransport().d50_d84_Fs_grain(GS_list, active_layer_GS_P_temp)
                                            
                # Calculate depth using the recking parameters and the indexs of the cells with a depth greater than the threshold (cell_size / 1000)
                depth_recking = sediment.sedimenttransport().depth_recking(Q_dis, slope, d84, self.cell_size)
                            
                # Calculate the timestep of the sediment transport using the maximum rate of entrainment in all the cells
                sediment_time_step_seconds = sediment.sedimenttransport().SedimentEntrainmentQmax(slope, depth_recking, Fs, d50, 
                                                                                                  self.cell_size, GS_list, active_layer_GS_P_list)
            
                if sediment_time_step_seconds >= 86400:
                    sediment_time_step_seconds = 86400

                sediment_time_step_seconds = 86400 #*********************************NEED TO TURN OFF******************************#
                ### Piece of code to record the timestep ###
                arcpy.AddMessage("Sediment timestep for today is  " + str(sediment_time_step_seconds))
                
                        
                # Collect garbage
                del d50, d84, Fs, active_layer_GS_P_list
                collected = gc.collect()
                arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 
                daily_save_date = str(self.current_date.strftime('%d_%m_%Y'))
            
                         
                # Calculate sediment transport for each timestep based on the above calculation 
                inactive_layer, DTM, DTM_MINUS_AL_IAL, recalculate_slope_flow = sediment.sedimenttransport().sediment_loop(sediment_time_step_seconds, GS_list, 
                                                                                                                           Q_dis, slope,
                                                                                                                           self.cell_size, flow_direction_np, 
                                                                                                                           self.bottom_left_corner, daily_save_date, 
                                                                                                                           active_layer_GS_P_temp, active_layer_V_temp, 
                                                                                                                           inactive_layer_GS_P_temp, 
                                                                                                                           inactive_layer_V_temp, inactive_layer, 
                                                                                                                           DTM, DTM_MINUS_AL_IAL)
                Sed_max = " "


                # Check if the user would like to save sediment transport at the outlet
                rasterstonumpys.output_sediment_csv(self.current_date, sediment_spamwriter, Sed_max)

            else:
                sediment_depth = 0
                depth_recking = 0
                net_sediment = 0
                

            sediment_depth = 0
            net_sediment = 0 
            ### Check  what needs to be output from the model ###
            self.week_day, self.month_day, self.year_day = rasterstonumpys.raster_outputs(self.week_day, self.month_day, self.year_day, self.current_date, self.first_loop, output_file_dict, output_format, self.bottom_left_corner, self.cell_size, Q_surf_np, Q_dis, depth_recking, precipitation, sediment_depth, net_sediment)
        
                
            ### VARIABLES / PARAMETERS THAT CHANGE AT END OF LOOP ###
            
            self.first_loop = False

            # Increment the date and day by 1
            self.current_date = self.current_date + datetime.timedelta(days=1)
            self.day_of_year += 1
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