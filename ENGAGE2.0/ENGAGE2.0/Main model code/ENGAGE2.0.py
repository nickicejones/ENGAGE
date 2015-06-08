##### Description of this python file #####
# This is the start location for the running of the model. The input files and output files are located and input into the model in this script


##### VARIABLES #####
# numpy_array_location - this is the location on the computer where hard copies of the numpy arrays can be stored.

### MODEL INPUTS ###
# precipitation_textfile - textfile containing daily precipitation
# baseflow_textfile - textfile containing daily baseflow
# model_start_date - date of start of the models operation
# region - region for evapotranspiration calculation - Choice of the following - ["Scotland N", "Scotland E", "Scotland W", "England E & NE", "England NW/ Wales N",
# "Midlands", "East Anglia", "England SW/ Wales S", "England SE/ Central S"] 
# precipitation_gauge_elevation - elevation of the precipiation gauge #OPTIONAL
# calculate_sediment - select whether or not the model calculates sediment
# This is a series of points along the river network at which a value is saved

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

#---------------------------------------------------------------------#
##### START OF MODEL CODE #####
### Import statements - Python ###
import arcpy
import numpy
import tempfile
import gc
import time

### Import Script Files NJ created ###
import datapreparation
import rastercharacteristics
import rasterstonumpys
import modelloop
import CN2numbers


### ENVIRONMENT SETTINGS ###
# Overwrite pre-existing files
arcpy.env.overwriteOutput = True
arcpy.env.compression = "NONE"
arcpy.AddMessage(" ") 

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
arcpy.env.workspace = "D:\Boydd at Bitton\Boydd_1.gdb"

# Textfile with precipitation on each line and textfile with the baseflow on each line
precipitation_textfile = r"D:\Boydd at Bitton\rainfall.txt"
baseflow_textfile = r"D:\Boydd at Bitton\Baseflow.txt"

# Date of starting model operation
model_start_date = "01/01/1990"
# Region for the evapotranspiration calculations
region = "Midlands"

# Ask the user for the elevation of the precipiation guage (if they would like to use spatial precipitation)
precipitation_gauge_elevation = float("65.1")      # Optional

# Selection of what the model calculates
calculate_sediment = "true"

# Select the outputs and frequency
output_surface_runoff = "Daily"                # Surface Runoff
output_discharge = "Daily"                      # Discharge
output_water_depth = "Daily"                    # Depth
output_spatial_precipitation = "Daily"          # Spatial Precipitation 
output_sediment_depth = "Daily"                # Sediment Depth
output_net_sediment_transport = "Daily"         # Total erosion / depostion in each cell
output_format = "Total"                      # Average or total for the above

# This is a output that is saved at the pour point (mouth of the river)
output_excel_discharge = "D:\Boydd at Bitton\Discharge.csv"
output_excel_sediment = "D:\Boydd at Bitton\Sediment_yield.csv"

# Use Dinfinity flow directions
use_dinfinity = "false"

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
calculate_sediment = arcpy.GetParameterAsText(6)

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
DTM, land_cover, land_cover_type, soil, soil_type, GS_1_P, GS_2_P, GS_3_P, GS_4_P, GS_5_P, GS_6_P, GS_7_P, river_soil_depth, river_catchment = datapreparation.check_preprocessing_files()
GS_P_list = [GS_1_P, GS_2_P, GS_3_P, GS_4_P, GS_5_P, GS_6_P, GS_7_P]
model_inputs_list = [land_cover, soil, river_soil_depth]
arcpy.AddMessage("Model data from pre-processing script succesfully loaded into model")


### NUMPY TO RASTER INFORMATION FROM ELEVATION ###
cell_size, bottom_left_corner = rastercharacteristics.get_cell_size_bottom_corner(DTM)



### CONVERT ARCGIS RASTERS TO NUMPY ARRAYS ###
# Convert the list of grain size proportion rasters to numpy arrays
GS_P_list = rasterstonumpys.convert_raster_to_numpy(GS_P_list)
model_inputs_list = rasterstonumpys.convert_raster_to_numpy(model_inputs_list)


### CALCULATE ACTIVE LAYER DEPTH/REMAINING SOIL DEPTH, AVERAGE NUMBER OF DAYS PRECIPITATION PER YEAR, STARTING GRAIN SIZE VOLUMES, TEMPORARY FILE LOCATIONS ###
# Active / Inactive layer volumes
active_layer, inactive_layer = datapreparation.calculate_active_layer(model_inputs_list[2], cell_size) 
# Active /  Inactive layer volumes for each grainsize
active_layer_GS_volumes, inactive_layer_GS_volumes = datapreparation.get_grain_volumes(GS_P_list, active_layer, inactive_layer) 
# Calculating the number of days precipitation in the catchment per year
day_pcp_yr = datapreparation.average_days_rainfall(precipitation_textfile)
active_layer_pro_temp_list, active_layer_vol_temp_list, inactive_layer_pro_temp_list, inactive_layer_vol_temp_list = datapreparation.temporary_file_locations(numpy_array_location, grain_size_proportions, active_layer_volumes, inactive_layer_volumes)



'''### CONVERT LANDCOVER AND SOIL DATA TO CN2 NUMBERS ### - CHECKED 12/11/14 NJ
CN2_d = CN2numbers.SCS_CN_Number().get_SCSCN2_numbers(model_input_parameters[1], soil_type, model_input_parameters[0], land_cover_type)

 

# Collect garbage
del active_layer, model_input_parameters, grain_size_proportions, active_layer_volumes, inactive_layer_volumes 
collected = gc.collect()
arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 
arcpy.AddMessage("-------------------------")

arcpy.AddMessage("Time to complete model preparation is " + str(round(time.time() - start,2)) + "s. ")
arcpy.AddMessage("-------------------------")
         
arcpy.AddMessage("Model initiated") 

### MAIN MODEL CODE ###
modelloop.model_loop().start_precipition(river_catchment_poly, precipitation_textfile, baseflow_textfile, model_start_date, region, elevation, CN2_d, day_pcp_yr, precipitation_gauge_elevation, cell_size, bottom_left_corner, grain_size_list, inactive_layer, active_layer_pro_temp_list, active_layer_vol_temp_list, inactive_layer_pro_temp_list, inactive_layer_vol_temp_list, numpy_array_location, use_dinfinity, calculate_sediment, output_file_list, output_excel_discharge, output_excel_sediment, output_format)'''



'''
### Section to save rasters while testing model ###
rasterstonumpys.convert_numpy_to_raster_single(active_layer, "active_layer", bottom_left_corner, cell_size, "0")
rasterstonumpys.convert_numpy_to_raster_single(inactive_layer, "inactive_layer", bottom_left_corner, cell_size, "0") '''