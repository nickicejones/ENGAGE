# Import statements
import arcpy
import numpy
import tempfile
import gc

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

# Set Environmental Workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0) 

### MODEL INPUTS ###
# Textfile with precipitation on each line and textfile with the baseflow on each line
precipitation_textfile = arcpy.GetParameterAsText(1)
baseflow_textfile = arcpy.GetParameterAsText(2)

# Date of starting model operation
model_start_date = arcpy.GetParameterAsText(3)
# Important temperature regime checks
region = arcpy.GetParameterAsText(4)

# Ask the user for the elevation of the precipiation guage (if they would like to use spatial precipitation)
precipitation_gauge_elevation = float(arcpy.GetParameterAsText(5)) # Optional

# Selection of what the model calculates
calculate_sediment = arcpy.GetParameterAsText(6)

# Select the outputs and frequency
output_runoff = arcpy.GetParameterAsText(7) # Surface Runoff
output_discharge = arcpy.GetParameterAsText(8) # Discharge
output_depth = arcpy.GetParameterAsText(9) # Depth
output_spatial_precipitation = arcpy.GetParameterAsText(10) # Spatial Precipitation 
output_sediment_depth = arcpy.GetParameterAsText(11) # Sediment Depth
output_sediment_erosion_deposition = arcpy.GetParameterAsText(12) # Total erosion / depostion in each cell
output_format = arcpy.GetParameterAsText(13) # Average or Total

# Create an output frequency list of the different strings
output_file_list = {"Runoff": output_runoff, "Discharge": output_discharge, "Depth": output_depth, "Spatial precipitation": output_spatial_precipitation, "Sediment depth": output_sediment_depth, "Sediment eroision/deposition": output_sediment_erosion_deposition}

for output, output_frequency in output_file_list.iteritems():
    arcpy.AddMessage("You have selected " + str(output_frequency) + " for " + output)

# This is a series of points along the river network at which a value is saved
output_excel_discharge = arcpy.GetParameterAsText(14) 
output_excel_sediment = arcpy.GetParameterAsText(15) 

# Use Dinfinity flow directions
use_dinfinity = arcpy.GetParameterAsText(16)

# 7 Grainsizes
grain_size_1 = 0.0000156  # Clay
grain_size_2 = 0.000354 # Sand 
grain_size_3 = 0.004 # Fine Gravel
grain_size_4 = 0.0113 # Medium Gravel
grain_size_5 = 0.032 # Coarse Gravel
grain_size_6 = 0.128 # Cobble
grain_size_7 = 0.256 # Boulder
grain_size_list = [grain_size_1, grain_size_2, grain_size_3, grain_size_4, grain_size_5, grain_size_6, grain_size_7]


### INPUTS FROM PREPROCESSING SCRIPT ###
# Elevation, Land cover, soil, grain size proportions,
elevation, land_cover, land_cover_type, soil, soil_type, grain_size_1_proportion, grain_size_2_proportion, grain_size_3_proportion, grain_size_4_proportion, grain_size_5_proportion, grain_size_6_proportion, grain_size_7_proportion, river_soil_depth, river_catchment_poly = datapreparation.check_preprocessing_files()
arcpy.AddMessage("Model data from pre-processing script succesfully loaded into model")



### NUMPY TO RASTER INFORMATION FROM ELEVATION ###
cell_size, bottom_left_corner = rastercharacteristics.get_cell_size_bottom_corner(elevation)



### CONVERT ARCGIS RASTERS TO NUMPY ARRAYS ###
# List of grain size proportions
grain_size_proportions = [grain_size_1_proportion, grain_size_2_proportion, grain_size_3_proportion, grain_size_4_proportion, grain_size_5_proportion, grain_size_6_proportion, grain_size_7_proportion]

# Convert the list of grain size proportion rasters to numpy arrays
grain_size_proportions = rasterstonumpys.convert_raster_to_numpy(grain_size_proportions)
# List of other rasters to convert 
model_input_parameters = [land_cover, soil, river_soil_depth]
model_input_parameters = rasterstonumpys.convert_raster_to_numpy(model_input_parameters)



### CALCULATE ACTIVE LAYER DEPTH/REMAINING SOIL DEPTH, AVERAGE NUMBER OF DAYS PRECIPITATION PER YEAR, STARTING GRAIN SIZE VOLUMES, TEMPORARY FILE LOCATIONS ###
active_layer, inactive_layer = datapreparation.calculate_active_layer(model_input_parameters[2], cell_size)
grain_size_volumes = datapreparation.get_grain_volumes(grain_size_proportions, active_layer) # Only in the active layer
day_pcp_yr = datapreparation.average_days_rainfall(precipitation_textfile)
grain_pro_temp_list, grain_vol_temp_list, remaining_soil_pro_temp_list = datapreparation.temporary_file_locations(numpy_array_location, grain_size_proportions, grain_size_volumes)



### CONVERT LANDCOVER AND SOIL DATA TO CN2 NUMBERS ### - CHECKED 12/11/14 NJ
CN2_d = CN2numbers.SCS_CN_Number().get_SCSCN2_numbers(model_input_parameters[1], soil_type, model_input_parameters[0], land_cover_type)

# Collect garbage
del active_layer, model_input_parameters, grain_size_proportions 
collected = gc.collect()
arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 
            
arcpy.AddMessage("Model initiated") 
### MAIN MODEL CODE ###
modelloop.model_loop().start_precipition(river_catchment_poly, precipitation_textfile, baseflow_textfile, model_start_date, region, elevation, CN2_d, day_pcp_yr, precipitation_gauge_elevation, cell_size, bottom_left_corner, grain_size_list, inactive_layer, remaining_soil_pro_temp_list, grain_pro_temp_list, grain_vol_temp_list, numpy_array_location, use_dinfinity, calculate_sediment, output_file_list, output_excel_discharge, output_excel_sediment, output_format)