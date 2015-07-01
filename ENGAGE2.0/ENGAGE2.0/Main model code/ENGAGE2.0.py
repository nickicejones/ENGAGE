##### Description of this python file #####
# This is the start location for the running of the model. The input files and output files are located and input into the model in this script


##### VARIABLES - Used in this file#####
# numpy_array_location - this is the location on the computer where hard copies of the numpy arrays can be stored.

### MODEL INPUTS ###
# precipitation_textfile - textfile containing daily precipitation
# baseflow_textfile - textfile containing daily baseflow
# model_start_date - date of start of the models operation
# region - region for evapotranspiration calculation - Choice of the following - ["Scotland N", "Scotland E", "Scotland W", "England E & NE", "England NW/ Wales N",
# "Midlands", "East Anglia", "England SW/ Wales S", "England SE/ Central S"] 
# precipitation_gauge_elevation - elevation of the precipiation gauge #OPTIONAL
# calculate_sediment - select whether or not the model calculates sediment
# use_dinfinity - whether or not the user has installed taudem so they can use dinfinity flow accumulation

### OUTPUT FREQUENCYS RASTERS ###
# output_surface_runoff - frequency to output surface runoff
# output_discharge - frequency to output discharge
# output_water_depth - frequency to ouput water depth
# output_spatial_precipitation - frequency to output spatial precipitation
# output_sediment_depth - frequency to output depth of sediment
# output_net_sediment_transport - frequency to output net sediment transport
# output_format_rasters - what should the format of the rasters be an average or total

### MODEL OUTPUTS - CSV ###
# output_excel_discharge - output daily discharge at the pour point 
# output_excel_sediment - output daily sediment yeild at the pour point
# output_file_dict - dict to print out the select outputs to user


### 7 GRAINSIZES ###
# GS_1 = 0.0000156 - Clay - Grain size 1
# GS_2 = 0.000354 - Sand - Grain size 2
# GS_3 = 0.004 - Fine Gravel - Grain size 3
# GS_4 = 0.0113 - Medium Gravel - Grain size 4
# GS_5 = 0.032 - Coarse Gravel - Grain size 5
# GS_6 = 0.128 - Cobble - Grain size 6
# GS_7 = 0.256 - Boulder - Grain size 7
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
# cell_size - the cell size of the model
# bottom_left_corner - the bottom left hand corner of the input rasters
# active_layer - the top 20 metres squared of the soil in the river channel that is considered to be actively available for transport (units are in metres squared)
# inactive_layer - the remaining soil depth left in the river channel and is not considered to be avaliable for transport (units are in metres squared)
# active_layer_GS_volumes - list containing the volumes of each of the grainsizes in the active layer
# inactive_layer_GS_volumes - list containing the volumes of each of the grainsizes in the inactive layer 
# day_pcp_yr - average number of days precipitation falling in the river catchment
# years_of_sim - number of years of rainfall data
# active_layer_GS_P_temp - list of temporary locations on the computer to store the active layer grain size proportions
# active_layer_V_temp - list of temporary locations on the computer to store the active layer grain size volumes
# inactive_layer_GS_P_temp - list of  temporary locations on the computer to store the inactive layer grain size proportions
# inactive_layer_V_temp - list of temporary location ons the computer to store the inactive layer grain size volumes
# CN2_d - Curve number 2 for that soil hydrology type and land cover (this is at 5% slope)
# baseflow_provided - this is a true/false statement of whether or not the user has provided baseflow


#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
import numpy as np
import tempfile
import time
import gc

### Import Script Files NJ created ###
import datapreparation
import rastercharacteristics
import rasterstonumpys
import modelloop
import CN2numbers
import maxhalfhourrain
# import manningsroughness - *** NEED TO READD TO GITHUB WHEN IN THE OFFIC ***
import Cfactor
import mergesoil
import calculate_daily_precipitation

### ENVIRONMENT SETTINGS ###
# Overwrite pre-existing files
arcpy.env.overwriteOutput = True
arcpy.env.compression = "NONE"
arcpy.AddMessage(" ") 
np.set_printoptions(suppress=True)
np.set_printoptions(precision=15)

# Start the timer for the model preparation
start = time.time()

# Check out the ArcGIS Spatial Analyst extension license
try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
        arcpy.AddMessage("Spatial Analyst license checked out")
        arcpy.AddMessage("-------------------------")
    else:
        # Raise a custom exception       
        raise LicenseError

except LicenseError:
    arcpy.AddMessage("Spatial Analyst license is unavailable, the model requires Spatial Analyst to operate")
    arcpy.AddMessage("-------------------------")

# Set a location to store the numpy array in a physical form
numpy_array_location = tempfile.mkdtemp(suffix='numpy', prefix='tmp')

### MODEL INPUTS - For StandAlone testing ###
# Set Environmental Workspace
arcpy.env.workspace = r"D:\EngageTesting\SmallCatchment_1.gdb" #r"D:\Boydd at Bitton\3by3_1.gdb" # r"D:\Boydd at Bitton\Boydd_2.gdb"

# Textfile with precipitation on each line and textfile with the baseflow on each line
precipitation_textfile = "#"
precipitation_hour_textfile = r"D:\EngageTesting\rainfall_hour.txt" # Going to have to work out the best way to do this! - maybe do the same option as with SWAT
baseflow_textfile = '#' #r"D:\Boydd at Bitton\Baseflow.txt"

# Check if the user has provided daily rainfall or only hourly.
if precipitation_textfile and precipitation_textfile == '#':
    precipitation_textfile = calculate_daily_precipitation.convert_precipitation(precipitation_hour_textfile)

# Date of starting model operation
model_start_date = "01/09/1998"
# Region for the evapotranspiration calculations
region = "Midlands"

# Ask the user for the elevation of the precipiation guage (if they would like to use spatial precipitation)
precipitation_gauge_elevation = float("100.1")      # Optional

# Selection of what the model calculates
calculate_sediment_erosion_hillslope = True
calculate_sediment_transport = True

# Select the outputs and frequency
output_surface_runoff = "Daily"                # Surface Runoff
output_discharge = "Daily"                      # Discharge
output_water_depth = "No output"                    # Depth
output_spatial_precipitation = "No output"          # Spatial Precipitation 
output_sediment_depth = "No output"                # Sediment Depth
output_net_sediment_transport = "No output"         # Total erosion / depostion in each cell
output_format = "Daily average"                      # Average or total for the above

# This is a output that is saved at the pour point (mouth of the river)
output_excel_discharge = r"D:\Boydd at Bitton"
output_excel_sediment = r"D:\Boydd at Bitton"

# Use Dinfinity flow directions
use_dinfinity = False

'''### MODEL INPUTS - For ArcGIS 10.1 ###
# Set Environmental Workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0) 

# Textfile with precipitation on each line and textfile with the baseflow on each line
precipitation_textfile = arcpy.GetParameterAsText(1)
baseflow_textfile = arcpy.GetParameterAsText(2)

# Date of starting model operation
model_start_date = arcpy.GetParameterAsText(3)
# Region for the evapotranspiration calculations
region = arcpy.GetParameterAsText(4)

# Ask the user for the elevation of the precipiation guage (if they would like to use spatial precipitation)
precipitation_gauge_elevation = float(arcpy.GetParameterAsText(5))      # Optional

# Selection of what the model calculates
calculate_sediment_transport = arcpy.GetParameterAsText(6)

# Select the outputs and frequency
output_surface_runoff = arcpy.GetParameterAsText(7)                 # Surface Runoff
output_discharge = arcpy.GetParameterAsText(8)                      # Discharge
output_water_depth = arcpy.GetParameterAsText(9)                    # Depth
output_spatial_precipitation = arcpy.GetParameterAsText(10)         # Spatial Precipitation 
output_sediment_depth = arcpy.GetParameterAsText(11)                # Sediment Depth
output_net_sediment_transport = arcpy.GetParameterAsText(12)        # Total erosion / depostion in each cell
output_format = arcpy.GetParameterAsText(13)                        # Average or total for the above

# This is a series of points along the river network at which a value is saved
output_excel_discharge = arcpy.GetParameterAsText(14) 
output_excel_sediment = arcpy.GetParameterAsText(15) 

# Use Dinfinity flow directions
use_dinfinity = arcpy.GetParameterAsText(16)'''


### INTIATION OF MODEL ###
# Create a dict of the output rasters
output_file_dict = datapreparation.output_raster_types(output_surface_runoff, 
                                                       output_discharge, output_water_depth, output_spatial_precipitation, 
                                                       output_sediment_depth, output_net_sediment_transport)

# 7 Grainsizes - for input into the model
GS_1 = 0.0000156        # Clay - Grain size 1
GS_2 = 0.000354         # Sand - Grain size 2 
GS_3 = 0.004            # Fine Gravel - Grain size 3
GS_4 = 0.0113           # Medium Gravel - Grain size 4
GS_5 = 0.032            # Coarse Gravel - Grain size 5
GS_6 = 0.128            # Cobble - Grain size 6
GS_7 = 0.256            # Boulder - Grain size 7
GS_list = [GS_1, GS_2, GS_3, GS_4, GS_5, GS_6, GS_7]


### INPUTS FROM PREPROCESSING SCRIPT ###
# Elevation, Land cover, soil, grain size proportions,
DTM, land_cover, land_cover_type, soil, soil_type, GS_1_P, GS_2_P, GS_3_P, GS_4_P, GS_5_P, GS_6_P, GS_7_P, ASD_soil_depth, BGS_soil_depth, general_soil_depth, river_catchment, orgC = datapreparation.check_preprocessing_files()
GS_P_list = [GS_1_P, GS_2_P, GS_3_P, GS_4_P, GS_5_P, GS_6_P, GS_7_P]
model_inputs_list = [land_cover, soil, ASD_soil_depth, BGS_soil_depth, general_soil_depth, orgC]
arcpy.AddMessage("Model data from pre-processing script succesfully loaded into model")


### NUMPY TO RASTER INFORMATION FROM ELEVATION ###
cell_size, bottom_left_corner = rastercharacteristics.get_cell_size_bottom_corner(DTM)

### CONVERT INCOMMING ARCGIS STRING BOOLEANS TO ACTUAL BOOLS ###
arcpy.AddMessage("Checking calculate sediment hillslope erosion is a boolean...")
calculate_sediment_erosion_hillslope = datapreparation.convert_to_boolean(calculate_sediment_erosion_hillslope)
arcpy.AddMessage("Checking calculate sediment erosion in channel is a boolean...")
calculate_sediment_transport = datapreparation.convert_to_boolean(calculate_sediment_transport)
arcpy.AddMessage("Checking use dinfinity is a boolean...")
use_dinfinity = datapreparation.convert_to_boolean(use_dinfinity)
arcpy.AddMessage("-------------------------")


### CONVERT ARCGIS RASTERS TO NUMPY ARRAYS ###
# Convert the list of grain size proportion rasters to numpy arrays
GS_P_list = rasterstonumpys.convert_raster_to_numpy(GS_P_list)
model_inputs_list = rasterstonumpys.convert_raster_to_numpy(model_inputs_list)

### Merge the soil depths and check the soil depth based on the land cover depths ###
soil_depth = mergesoil.calculate_soil_depth(model_inputs_list[0], land_cover_type, model_inputs_list[2], model_inputs_list[3], model_inputs_list[4])

### CALCULATE ACTIVE LAYER DEPTH/REMAINING SOIL DEPTH, AVERAGE NUMBER OF DAYS PRECIPITATION PER YEAR, STARTING GRAIN SIZE VOLUMES, TEMPORARY FILE LOCATIONS ###
# Active / Inactive layer volumes
active_layer, inactive_layer = datapreparation.calculate_active_layer(soil_depth, cell_size) 
# Active /  Inactive layer volumes for each grainsize
active_layer_GS_volumes, inactive_layer_GS_volumes = datapreparation.get_grain_volumes(GS_P_list, active_layer, inactive_layer) 
# Calculating the number of days precipitation in the catchment per year
day_pcp_yr, years_of_sim, total_day_month_precip, total_avg_month_precip = datapreparation.average_days_rainfall(model_start_date, precipitation_textfile)
max_30min_rainfall_list = maxhalfhourrain.max_30min_rainfall(precipitation_hour_textfile, model_start_date) 
# Create temporary locations to store numpy arrays on the computers hardrive
arcpy.AddMessage("Temporary files will be located here " + str(numpy_array_location))
arcpy.AddMessage("-------------------------")
active_layer_GS_P_temp, active_layer_V_temp, inactive_layer_GS_P_temp, inactive_layer_V_temp = datapreparation.temporary_file_locations(numpy_array_location, GS_P_list, active_layer_GS_volumes, inactive_layer_GS_volumes)
# Combine baseflow if provided
precipitation_textfile, baseflow_provided = datapreparation.combined_precipitation(numpy_array_location, precipitation_textfile, baseflow_textfile)


### CONVERT LANDCOVER AND SOIL DATA TO CN2 NUMBERS, Mannings n and CUSLE (C factor) ### - CHECKED 12/11/14 NJ
CN2_d = CN2numbers.SCS_CN_Number().get_SCSCN2_numbers(model_inputs_list[1], soil_type, model_inputs_list[0], land_cover_type)
mannings_n =  '#' # manningsroughness.get_mannings(model_inputs_list[0]) - need to change back when in UNI
CULSE = Cfactor.get_Cfactor(model_inputs_list[0])

arcpy.AddMessage("Time to complete model preparation is " + str(round(time.time() - start,2)) + "s. ")
arcpy.AddMessage("-------------------------")

### MAIN MODEL CODE ###
arcpy.AddMessage("Model initiated")
 
modelloop.model_loop(model_start_date, cell_size, bottom_left_corner, 
                     calculate_sediment_transport, calculate_sediment_erosion_hillslope, use_dinfinity).start_precipition(river_catchment, DTM, region, 
                                                                          precipitation_textfile, baseflow_provided, day_pcp_yr, years_of_sim, 
                                                                          total_day_month_precip, total_avg_month_precip, max_30min_rainfall_list, 
                                                                          mannings_n, CULSE, orgC, precipitation_gauge_elevation, 
                                                                          CN2_d, GS_list, active_layer, inactive_layer, 
                                                                          active_layer_GS_P_temp, active_layer_V_temp, 
                                                                          inactive_layer_GS_P_temp, inactive_layer_V_temp, 
                                                                          numpy_array_location, 
                                                                          output_file_dict, output_format, 
                                                                          output_excel_discharge, output_excel_sediment)
                                                                                           
