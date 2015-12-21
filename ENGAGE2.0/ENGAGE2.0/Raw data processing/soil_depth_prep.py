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


# Function to calculate the depth of soil in the river and on the hillslopes
def soil_depth_calc(soil_parent_material_1, advanced_superficial_deposit, DTM_clip_np, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, bottom_left_corner):

    adaquate_soil_data_provided = False
    if soil_parent_material_1 and soil_parent_material_1 != '#':
        if advanced_superficial_deposit and advanced_superficial_deposit  != '#':
            arcpy.AddMessage("Adequate soil information provided")
            adaquate_soil_data_provided = True

    if soil_parent_material_1 and soil_parent_material_1 != '#':
        # Check the soil parent type
        desc_soil_depth = arcpy.Describe(soil_parent_material_1)
        soil_depth_raster_feature = desc_soil_depth.datasetType
        arcpy.AddMessage("The soil depth dataset is a " + soil_depth_raster_feature)

        # process the soil parent material for entry into the model.

        if soil_depth_raster_feature == 'FeatureClass':
            
            soil_parent_material_1_clip = arcpy.Clip_analysis(soil_parent_material_1, river_catchment_BNG)
                        
            arcpy.AddField_management(soil_parent_material_1_clip, "R_DEPTH", "FLOAT")

            arcpy.AddMessage("Added new fields to the table")
            
            # Create update cursor for feature class 
            rows = arcpy.UpdateCursor(soil_parent_material_1_clip) 

            for row in rows:
                if row.SOIL_DEPTH == "DEEP":
                    row.R_DEPTH = 2.0

                elif row.SOIL_DEPTH == "DEEP-INTERMEDIATE":
                    row.R_DEPTH = 1.5

                elif row.SOIL_DEPTH == "INTERMEDIATE":
                    row.R_DEPTH = 1.0

                elif row.SOIL_DEPTH == "INTERMEDIATE-SHALLOW":
                    row.R_DEPTH = 0.5

                elif row.SOIL_DEPTH == "SHALLOW":
                    row.R_DEPTH = 0.25

                elif row.SOIL_DEPTH == "NA":
                    row.R_DEPTH = 0.0

                else:
                    row.R_DEPTH = 0.0

                rows.updateRow(row) 

            # Delete cursor and row objects to remove locks on the data 
            del row 
            del rows

            soil_depth_raster = arcpy.FeatureToRaster_conversion(soil_parent_material_1_clip, "R_DEPTH", '#', DTM_cell_size)
                  
            soil_depth_raster_clip = arcpy.Clip_management(soil_depth_raster, catch_extent, "MODEL_BGS_SOIL_DEPTH", river_catchment_BNG, "#","ClippingGeometry")  
            arcpy.AddMessage("Soil depth field converted to raster and clipped")

        else:
            Soil_clip = arcpy.Clip_management(soil_depth, catch_extent, "MODEL_BGS_SOIL_DEPTH", river_catchment_BNG, "#","ClippingGeometry")

    # Process and clip the advanced superficial deposit data ready to go into the model.
    if advanced_superficial_deposit and advanced_superficial_deposit  != '#':
        # Check superficial type
        desc_advanced_superficial_deposit = arcpy.Describe(advanced_superficial_deposit)
        advanced_superficial_deposit_raster_feature = desc_advanced_superficial_deposit.datasetType
        arcpy.AddMessage("The advanced superficial deposit is a " + advanced_superficial_deposit_raster_feature)

        # Check land cover cell size
        advanced_superficial_deposit_cell_size = desc_advanced_superficial_deposit.meanCellHeight
        arcpy.AddMessage("The advanced superficial deposit cell size is " + str(advanced_superficial_deposit_cell_size))

        if advanced_superficial_deposit_cell_size != DTM_cell_size:
 
            arcpy.AddMessage("The cell size of the advanced superficial deposit you have provided is different to the DTM")
            advanced_superficial_deposit_clip = arcpy.Clip_management(advanced_superficial_deposit, buffer_extent, "Temp11", buffer_catchment, "#","ClippingGeometry")
            arcpy.AddMessage("Advanced superficial deposit clipped to enlarged catchment")
            advanced_superficial_deposit_correct_cell = arcpy.Resample_management(advanced_superficial_deposit_clip, "Temp12", DTM_cell_size, "NEAREST")
            arcpy.AddMessage("Cell size of advanced superficial deposit converted to same as DTM")
            #advanced_superficial_deposit_final_clip = arcpy.Clip_management(advanced_superficial_deposit_correct_cell, catch_extent, "MODEL_SUP_DEPTH", river_catchment_BNG, "#", "ClippingGeometry")
            advanced_superficial_deposit_final_clip = arcpy.gp.ExtractByMask_sa(advanced_superficial_deposit_correct_cell, river_catchment_BNG, "MODEL_SUP_DEPTH")
            arcpy.AddMessage("Advanced superficial deposit correct cell clipped to catchment")

        else:
            advanced_superficial_deposit_final_clip = arcpy.gp.ExtractByMask_sa(advanced_superficial_deposit, river_catchment_BNG, "MODEL_SUP_DEPTH")

        neighborhood = NbrRectangle(200, 200, "Map")

        # Execute FocalStatistics
        focal_advanced_superficial_deposit = FocalStatistics("MODEL_SUP_DEPTH", neighborhood, "MEAN", "")
        #focal_advanced_superficial_deposit_final_clip = arcpy.Clip_management(focal_advanced_superficial_deposit, catch_extent, "MODEL_FOCAL_SUP_DEPTH", river_catchment_BNG, "#", "ClippingGeometry")
        focal_advanced_superficial_deposit_final_clip = arcpy.gp.ExtractByMask_sa(focal_advanced_superficial_deposit, river_catchment_BNG, "MODEL_FOCAL_SUP_DEPTH")
        arcpy.AddMessage("Focal statistics calculated")

        # Convert the soil depth rasters to numpys
        advanced_superficial_deposit_np = arcpy.RasterToNumPyArray("MODEL_SUP_DEPTH", '#','#','#', 0)        
        focal_advanced_superficial_deposit_np = arcpy.RasterToNumPyArray("MODEL_FOCAL_SUP_DEPTH", '#','#','#', 0)        
        final_depth = np.zeros_like(DTM_clip_np, dtype = float)
              
        np.putmask(final_depth, np.logical_and(focal_advanced_superficial_deposit_np > 0, final_depth >= 0), focal_advanced_superficial_deposit_np)
        np.putmask(final_depth, np.logical_and(advanced_superficial_deposit_np > 0, advanced_superficial_deposit_np > final_depth), advanced_superficial_deposit_np)
      
        final_depth[DTM_clip_np == -9999] = -9999

        soil_depth_raster = arcpy.NumPyArrayToRaster(final_depth, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        soil_depth_raster.save("MODEL_ASD_soil_depth")
                
                
    # Soil depth data
    if adaquate_soil_data_provided == False:
        arcpy.AddMessage("No soil depth or particaldata has been provided therefore a default depth of 1m will be used for missing areas")
        soil_depth = np.empty_like(DTM_clip_np, dtype = float)
        soil_depth[:] = 1.0
        soil_depth[DTM_clip_np == -9999] = -9999
        soil_depth_raster = arcpy.NumPyArrayToRaster(soil_depth, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        soil_depth_raster = arcpy.Clip_management(soil_depth_raster, catch_extent, "MODEL_general_soil_depth", river_catchment_BNG, "#","ClippingGeometry")
        
    arcpy.AddMessage("Soil depth calculated")
    arcpy.AddMessage("-------------------------")