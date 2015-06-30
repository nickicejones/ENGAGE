##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
from arcpy.sa import *

# Fuction to correct river catchment for  clipping datasets
def catchment_preparation(river_catchment, cell_size):
 
    river_catchment_raster = arcpy.FeatureToRaster_conversion(river_catchment, "OBJECTID", "MODEL_river_catchment_ras", cell_size)
    river_catchment_polygon = arcpy.RasterToPolygon_conversion(river_catchment_raster, "MODEL_river_catchment_poly", "NO_SIMPLIFY", "#")

    lst = arcpy.ListFields(river_catchment_polygon)

    SBS_exists = 'false'
    GRID_exists = 'false'

    for f in lst:        
        if f.name == "SBS_CODE":
            SBS_exists = 'true'
            arcpy.AddMessage("SBS_CODE exists")
        elif f.name == "grid_code":
            GRID_exists = 'true'
            arcpy.AddMessage("grid_code exists")

    if SBS_exists == 'false':
        arcpy.AddField_management(river_catchment_polygon, "SBS_CODE", "SHORT")
        arcpy.AddMessage("added SBS_CODE")
    if GRID_exists == 'false':    
        arcpy.AddField_management(river_catchment_polygon, "grid_code", "SHORT")
        arcpy.AddMessage("added grid_code")

            
    # Create update cursor for feature class 
    rows = arcpy.UpdateCursor(river_catchment_polygon) 

    for row in rows:
        row.SBS_CODE = 0
        row.grid_code = 0

        rows.updateRow(row)
        
    # Delete cursor and row objects to remove locks on the data 
    del row 
    del rows 
    arcpy.AddMessage("Corrected catchment")
    arcpy.AddMessage("-------------------------")

    return river_catchment_polygon