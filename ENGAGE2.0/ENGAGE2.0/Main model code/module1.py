import subprocess
import os
import arcpy
import time
from arcpy.sa import *
from subprocess import check_output

# Check out the ArcGIS Spatial Analyst extension license
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")

# Variables to pass into the subprocess
numpy_array_location = r"C:\Users\nickj\Desktop\Example Catchment Safe Testing\49003 - De Lank at De Lank\Other Materials"
arcpy.env.workspace = r"C:\Users\nickj\Desktop\Example Catchment Safe Testing\49003 - De Lank at De Lank\Other Materials\Processed_data_backup_slope_looping.gdb"
DTM_temp = numpy_array_location + '\DTM_temp.npy'
slope_temp = numpy_array_location + '\slope_temp.npy'
full_path = os.path.abspath('subslope.py')


DTM = "MODEL_DTM"
# Get the cell and bottom left corner
# Determine cell size
describe_elevation = arcpy.Describe(DTM)
cell_size = str(describe_elevation.meanCellHeight)

# The below text takes the input raster and calculates the bottom left corner
extent_xmin_result = arcpy.GetRasterProperties_management(DTM, "LEFT")
extent_xmin = extent_xmin_result.getOutput(0)
extent_ymin_result = arcpy.GetRasterProperties_management(DTM, "BOTTOM")
extent_ymin = extent_ymin_result.getOutput(0)

# Start the timer for the model preparation
start = time.time()

output = check_output(['python', full_path, arcpy.env.workspace, DTM_temp, slope_temp, extent_xmin, extent_ymin, cell_size])

arcpy.AddMessage("Time to complete slope is " + str(round(time.time() - start,2)) + "s. ")
