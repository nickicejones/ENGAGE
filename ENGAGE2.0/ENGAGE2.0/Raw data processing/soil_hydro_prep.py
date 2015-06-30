##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
import numpy as np
from arcpy.sa import *

# Clip the land cover to the river catchment 
def soil_clip_analysis(soil_BNG, Soil_type, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent):
    # Check the soil type
    desc_soil = arcpy.Describe(soil_BNG)
    soil_raster_feature = desc_soil.datasetType
    arcpy.AddMessage("The soil is a " + soil_raster_feature)

    if soil_raster_feature == 'FeatureClass':

        soil_clip = arcpy.Clip_analysis(soil_BNG, river_catchment_BNG)
   
        if Soil_type == 'UK HOST':
            arcpy.AddMessage("UK HOST soil data selected")
            soil_clipped = arcpy.FeatureToRaster_conversion(soil_clip, "HOST", "Temp7", DTM_cell_size)          
            soil_clip_raster = arcpy.Clip_management(soil_clipped, catch_extent, "MODEL_Soil_HOST", river_catchment_BNG, "#", "ClippingGeometry")
            #soil_clip_raster = arcpy.gp.ExtractByMask_sa(soil_clipped, river_catchment_BNG, "MODEL_Soil_HOST")

        elif Soil_type == 'FAO':
            arcpy.AddMessage("FAO soil data selected")
 
            soil_clipped = arcpy.FeatureToRaster_conversion(soil_BNG, "SNUM", "Temp8", DTM_cell_size)
            soil_clip_raster = arcpy.gp.ExtractByMask_sa(soil_clipped, river_catchment_polygon, "MODEL_Soil_FAO")
            #soil_clip_raster = arcpy.Clip_management(Soil_clip, extent, "MODEL_Soil_FAO", River_catchment_poly, "#", "ClippingGeometry")
            
    else:
        if Soil_type == 'UK HOST':
            Soil_clip = arcpy.Clip_management(soil_BNG, catch_extent, "MODEL_Soil_HOST", river_catchment_BNG, "#","ClippingGeometry")
        
        elif Soil_type == 'FAO':
            Soil_clip = arcpy.Clip_management(soil_BNG, catch_extent, "MODEL_Soil_FAO", river_catchment_BNG, "#","ClippingGeometry")
                                 
    arcpy.AddMessage("Soil clipped to catchment")
    arcpy.AddMessage("-------------------------")