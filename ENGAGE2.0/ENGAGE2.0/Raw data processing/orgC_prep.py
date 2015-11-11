##### Description of this python file #####
# This is the start location for preprocessing script for calculating Organic Content prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
import numpy as np
from arcpy.sa import *

# Function to calculate the organic carbon in the topsoil
def soil_orgC_calc(orgC_BNG, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, bottom_left_corner):

    if orgC_BNG and orgC_BNG != '#':
        # Check the soil parent type
        desc_soil_orgC = arcpy.Describe(orgC_BNG)
        soil_orgC_raster_feature = desc_soil_orgC.datasetType
        arcpy.AddMessage("The soil orgC dataset is a " + soil_orgC_raster_feature)

        # process the soil parent material for entry into the model.
        if soil_orgC_raster_feature == 'FeatureClass':
            
            soil_orgC_clip = arcpy.Clip_analysis(orgC_BNG, river_catchment_BNG)
                        
            arcpy.AddField_management(soil_orgC_clip, "orgC_PER", "FLOAT")
            arcpy.AddMessage("Added new fields to the table")
            
            # Create update cursor for feature class 
            rows = arcpy.UpdateCursor(soil_orgC_clip) 

            #H(igh): > 6.0%
            #M(edium): 2.1-6.0%
            #L(ow): 1.1-2.0%
            #V(ery) L(ow): < 1.0%

            for row in rows:
                if row.OC_TOP == "H":
                    row.orgC_PER = 10.0

                elif row.OC_TOP == "M":
                    row.orgC_PER = 4.0

                elif row.OC_TOP == "L":
                    row.orgC_PER = 1.5

                elif row.OC_TOP == "V":
                    row.orgC_PER = 0.5

                else:
                    row.orgC_PER = 0.0

                rows.updateRow(row) 

            # Delete cursor and row objects to remove locks on the data 
            del row 
            del rows

            soil_orgC_raster = arcpy.FeatureToRaster_conversion(soil_orgC_clip, "orgC_PER", 'Temp15', DTM_cell_size)

            #soil_clip_raster = arcpy.gp.ExtractByMask_sa(soil_orgC_raster, river_catchment_BNG, "MODEL_orgC")     

            soil_depth_raster_clip = arcpy.Clip_management(soil_orgC_raster, catch_extent, "MODEL_orgC", river_catchment_BNG, "#","ClippingGeometry")  
            arcpy.AddMessage("Soil orgC field converted to raster and clipped")

        else:
            arcpy.AddMessage("Soil orgC not provided")
        

    arcpy.AddMessage("Soil orgC calculated")
    arcpy.AddMessage("-------------------------")

