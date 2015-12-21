##### Description of this python file #####
# This is the location for the DTM preparation module in the model.


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
from arcpy.sa import *

# Function to fill the DTM, calculate flow directions and cell size of the DTM.
def DTM_preparation(DTM):
    # Calculate some stats for the DTM
    # Fill the raster
    DTM_fill = Fill(DTM)
    arcpy.AddMessage("Filled digital terrain model")
    arcpy.AddMessage("-----------------------")
    arcpy.SetProgressorPosition(5)

    # Calculate the flow direction of the DTM
    DTM_flow_direction = FlowDirection(DTM_fill)
    arcpy.AddMessage("Calculated flow direction")
    arcpy.AddMessage("-----------------------")

    # Get the cell size 
    #Get the geoprocessing result object
    DTM_cell_size = arcpy.GetRasterProperties_management(DTM, "CELLSIZEX")
    #Get the elevation standard deviation value from geoprocessing result object
    cell_size = DTM_cell_size.getOutput(0) 
    arcpy.AddMessage("Calculated cell size")
    arcpy.AddMessage("-----------------------")

    return DTM_fill, DTM_flow_direction, cell_size

# Function to clip the DTM
def DTM_clip(DTM_BNG, catch_extent, river_catchment_BNG):
    # Clip the DTM
    DTM_clip = arcpy.Clip_management(DTM_BNG, catch_extent, "MODEL_DTM", river_catchment_BNG, "#", "ClippingGeometry")
    #DTM_Clip1 = arcpy.gp.ExtractByMask_sa(DTM_Clip, river_catchment_BNG, "MODEL_DTM1")
    arcpy.AddMessage("Digital Terrain Model (DTM) clipped to catchment")
    arcpy.AddMessage("-------------------------")

    # Convert DTM to np array
    DTM_clip_np = arcpy.RasterToNumPyArray("MODEL_DTM", '#','#','#', -9999)

    # Find the characteristics of the DTM
    # Determine cell size
    desc_DTM = arcpy.Describe(DTM_clip)
    DTM_cell_size = desc_DTM.meanCellHeight
    arcpy.AddMessage("The model is working on a cell size of " + str(DTM_cell_size) + " metres.")
    DTM_extent = desc_DTM.Extent

    # Turns the corner into a point
    bottom_left_corner = arcpy.Point(DTM_extent.XMin, DTM_extent.YMin)

    return DTM_clip, DTM_cell_size, bottom_left_corner