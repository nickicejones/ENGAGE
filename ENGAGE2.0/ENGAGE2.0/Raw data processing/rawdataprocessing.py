##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
import numpy as np
import grainsize_lookup
from arcpy.sa import *

### Import Script Files NJ created ###
import DTM_prep
import catchment_prep
import BNG_check
import define_extents
import landcover_prep
import soil_hydro_prep
import grain_size_proportion
import soil_depth_prep
import orgC_prep
import delete_unused_array

### ENVIRONMENT SETTINGS ###
# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Check out extensions
arcpy.CheckOutExtension("Spatial")


### GET INPUT PARAMETERS ###
# set environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Users will have to provide a rivere catchment boundry 
river_catchment = arcpy.GetParameterAsText(1)

# Check if MODEL_river_catchment exists as this is needed in the model start of the script.
if arcpy.Exists("MODEL_river_catchment"):
    river_catchment = river_catchment
else:
    arcpy.Copy_management(river_catchment, "MODEL_river_catchment")

# Digital Terrain Model
DTM = arcpy.GetParameterAsText(2)

# River network to burn in river channels
river_network = arcpy.GetParameterAsText(3)

# Land Cover Data
Land_cover_type = arcpy.GetParameterAsText(4)
land_cover = arcpy.GetParameterAsText(5)
natural_england_SPS = arcpy.GetParameterAsText(6) # optional
roads = arcpy.GetParameterAsText(7) # optional

# Soil Data
Soil_type = arcpy.GetParameterAsText(8)
soil = arcpy.GetParameterAsText(9)

# Soil grain size Data
soil_parent_material_50 = arcpy.GetParameterAsText(10) # shapefile of UK coverage

# Soil depth Data
# Uk soil parent material 
advanced_superficial_deposit = arcpy.GetParameterAsText(11) # raster of superficial deposit depth
soil_parent_material_1 = arcpy.GetParameterAsText(12) 
orgC = arcpy.GetParameterAsText(13)


### Start of data preparation ###
# Prepare the DTM.
DTM_fill, DTM_flow_direction, cell_size = DTM_prep.DTM_preparation(DTM)

# Prepare the river catchment for clipping
river_catchment_polygon = catchment_prep.catchment_preparation(river_catchment, cell_size)

# Check if river network provided and clip it to catchment
if river_network and river_network != '#':
    river_network_clip = arcpy.Clip_analysis(river_network, river_catchment_polygon, "MODEL_river_network")
                      
# Check if user is using FAO or Corine and if orgC is provided
def check_BNG_needed(Soil_type, Land_cover_type, orgC):
    if Soil_type == 'FAO':
        BNG = True
    if Land_cover_type == 'CORINE 2006':
        BNG = True
    if orgC and orgC != '#':
        BNG = True
    else:
        BNG = False

    return BNG

BNG = check_BNG_needed(Soil_type, Land_cover_type, orgC)

# Check if files need to be converted to BNG
DTM_BNG, soil_BNG, land_cover_BNG, river_catchment_BNG, orgC_BNG = BNG_check.convert_BNG(BNG, DTM_fill, soil, land_cover, orgC, river_catchment_polygon)

# Calculate a buffer catchment and the extents of the catchments
catch_extent, buffer_catchment, buffer_extent = define_extents.calculate_catchment_extents(river_catchment_BNG)

# Clip the DTM and return the cell size and bottom left corner
DTM_clip, DTM_clip_np, DTM_cell_size, bottom_left_corner = DTM_prep.DTM_clip(DTM_BNG, catch_extent, river_catchment_BNG)

# Clip the land cover to the river catchment
land_cover_clipped = landcover_prep.land_cover_clip_analysis(land_cover, Land_cover_type, DTM_clip_np, DTM_cell_size, buffer_catchment, buffer_extent, 
                                                             river_catchment_BNG, catch_extent, natural_england_SPS, roads)

# Clip the soil hydrology to the river catchment
soil_clipped = soil_hydro_prep.soil_clip_analysis(soil_BNG, Soil_type, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent)

# Calculate the distribuiton of grain sizes across the catchment
soil_grain_calculation = grain_size_proportion.grain_size_calculation(soil_parent_material_50, DTM_clip_np, DTM_cell_size, 
                                                                      buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, bottom_left_corner)

# Calculate the distribution of soil depth across the river catchment
soil_depth_calculation = soil_depth_prep.soil_depth_calc(soil_parent_material_1, advanced_superficial_deposit, DTM_clip_np, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, bottom_left_corner)

# Calculate the organic carbon in the topsoil
soil_orgC_calculation = orgC_prep.soil_orgC_calc(orgC_BNG, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, bottom_left_corner)

# Delete the unused files
delete_unused_array.delete_temp_files()

arcpy.AddMessage("Preprocessing complete")