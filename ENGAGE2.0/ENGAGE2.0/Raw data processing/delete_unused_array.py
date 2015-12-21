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

# Small part of code to delete the unused/not needed parts
def delete_temp_files():
    delete_list = ["Temp1", "Temp2", "Temp3", "Temp4", "Temp5", "Temp6", "Temp7", "Temp8", "Temp9", "Temp10", "Temp11", "Temp12", "Temp13", "Temp14", "Temp15", "Model_ROADS", "Model_NE_SBS",  "land_BNG", "DTM_BNG", "soil_BNG", "catchment_BNG", "river_buffer", "LCMSTAGE1", "LCMSTAGE2", "LCMSTAGE3", "LCMSTAGE4",  "MODEL_SUP_DEPTH", "MODEL_FOCAL_SUP_DEPTH", "river_raster", "orgC_BNG", "MODEL_river_catchment_poly", "MODEL_river_catchment_ras", "MODEL_roads_polygon", "Clipped_SBS", "Temp111"]
    for item in delete_list:
        if arcpy.Exists(item):
            arcpy.Delete_management(item)
   
    arcpy.AddMessage("Deleted temporary files")
    arcpy.AddMessage("-----------------------")