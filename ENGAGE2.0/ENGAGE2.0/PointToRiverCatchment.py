#Import Required Modules
import arcpy
import numpy as np
from arcpy.sa import *

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# check out extensions
arcpy.CheckOutExtension("Spatial")

# Get input parameters
# set environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Cell size
cell_size = arcpy.GetParameterAsText(1)

# Digital Terrain Model
DTM = arcpy.GetParameterAsText(2)

# Users will have to choose to use either the catchment boundry or pour point
pour_point = arcpy.GetParameterAsText(3) 

# Calculate some stats for the DTM
# Fill the raster
DTM_fill = Fill(DTM)
arcpy.AddMessage("Filled digital terrain model")
arcpy.AddMessage("-----------------------")

# Calculate the flow direction of the DTM
DTM_flow_direction = FlowDirection(DTM_fill)
arcpy.AddMessage("Calculated flow direction")
arcpy.AddMessage("-----------------------")

def snap_pour_point(pour_point, DTM_flow_direction):
    # This part of the scripts checks if the users wants to snap the pour point (which is recomended).
    arcpy.AddMessage("Snapping pour point")  
    arcpy.AddMessage("-----------------------")       
    out_flow_accumulation = FlowAccumulation(DTM_flow_direction)
    arcpy.AddMessage("Calculated flow accumulation")
    arcpy.AddMessage("-----------------------")
    out_snap_pour = SnapPourPoint(pour_point, out_flow_accumulation, 1)
    arcpy.AddMessage("Pour point snapped")
    arcpy.AddMessage("-----------------------")
    out_snap_pour
    return out_snap_pour

def catchment_pour(pour_point, DTM_flow_direction):               
    # Execute Watershed
    River_catchment = Watershed(DTM_flow_direction, pour_point, '#')
    arcpy.AddMessage("Calculated river catchment")
    arcpy.AddMessage("-----------------------")

    # Execute RasterToPolygon
    river_catchment_polygon = arcpy.RasterToPolygon_conversion(River_catchment, "MODEL_river_catchment", "NO_SIMPLIFY", "#")
    return river_catchment_polygon

# Check if the pour point needs snapping and calculate the river catchment.
snapped_pour_point = snap_pour_point(pour_point, DTM_flow_direction)
river_catchment_polygon = catchment_pour(snapped_pour_point, DTM_flow_direction)
