# Import Required Modules
import arcpy
import numpy as np
from arcpy.sa import *

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Check out extensions
arcpy.CheckOutExtension("Spatial")
arcpy.AddMessage("Spatial analyst extension checked out")
arcpy.AddMessage("-----------------------")

# Get input parameters
# set environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Digital Terrain Model
DTM = arcpy.GetParameterAsText(1)

# Users will have to choose to use either the catchment boundry or pour point
pour_point = arcpy.GetParameterAsText(2) 

# Check if used wants to snap the pour point
snap_pour = arcpy.GetParameterAsText(3)

# Check what distance the user wants to look for the river channel - Maximum distance, in map units, to search for a cell of higher accumulated flow.
snap_distance = arcpy.GetParameterAsText(4)

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
    out_snap_pour = SnapPourPoint(pour_point, out_flow_accumulation, snap_distance)
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
if snap_pour != 'false':
    snapped_pour_point = snap_pour_point(pour_point, DTM_flow_direction)

river_catchment_polygon = catchment_pour(snapped_pour_point, DTM_flow_direction)
