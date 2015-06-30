##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
from arcpy.sa import *

# Function to calculate the catchment extents
def calculate_catchment_extents(river_catchment_BNG):
    # Define the extents of the river catchment
    def extents(fc):
        extent = arcpy.Describe(fc).extent
        west = round(extent.XMin) 
        south = round(extent.YMin) 
        east = round(extent.XMax)
        north = round(extent.YMax) 
        return west, south, east, north

    # Obtain extents of two shapes
    XMin, YMin, XMax, YMax = extents(river_catchment_BNG)

    # Set the extent environment
    arcpy.AddMessage("The catchment extent is " + "%s %s %s %s" % (XMin, YMin, XMax, YMax))
    catch_extent = "%s %s %s %s" % (XMin, YMin, XMax, YMax)
    arcpy.AddMessage("-------------------------")

    # Buffer the catchment
    buffer_catchment = arcpy.Buffer_analysis(river_catchment_BNG, "river_buffer", "2500")
    # Describe to find characteristics of buffer clip area

    # Obtain extents of two shapes
    XMin, YMin, XMax, YMax = extents(buffer_catchment)

    # Set the extent environment
    arcpy.AddMessage("The catchment buffer extent is " + "%s %s %s %s" % (XMin, YMin, XMax, YMax))
    buffer_extent = "%s %s %s %s" % (XMin, YMin, XMax, YMax)
    arcpy.AddMessage("-------------------------")

    return catch_extent, buffer_catchment, buffer_extent