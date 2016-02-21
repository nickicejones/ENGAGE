# Test of a sub process call of the slope
import numpy as np
import arcpy
import sys
from arcpy.sa import *

### ENVIRONMENT SETTINGS ###
# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

print "Calculating slope in a subprocess to avoid excess memory use"

# Get the system arguements
arcpy.env.workspace = sys.argv[1]
DTM_temp = sys.argv[2]
slope_temp = sys.argv[3]
extent_xmin = sys.argv[4]
extent_ymin = sys.argv[5]
cell_size_slope = float(sys.argv[6])

# Check out the ArcGIS Spatial Analyst extension license
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension("Spatial")
   
# Turns the corner into a point
bottom_left_corner = arcpy.Point(float(extent_xmin), float(extent_ymin))

# Load the latest version of the DTM from the saved numpy array
DTM = np.load(DTM_temp)

# Convert the DTM to a raster
DTM_ras = arcpy.NumPyArrayToRaster(DTM, bottom_left_corner, cell_size_slope, cell_size_slope, -9999)

# Set local variables
nbr = NbrRectangle(3, 3, "CELL")

# Execute BlockStatistics to find the minimum surrounding cell
lowest_cell = FocalStatistics(DTM_ras, nbr, "MINIMUM", "DATA")

# Calculate the difference between the DTM and the lowest surrounding cell
height_difference = DTM_ras - lowest_cell  
        
# Calculate the slope between cells
# First calculate opposite over adjacent
height_difference /= cell_size_slope
        
# Then use inverse tan to calculate the slope
slope = ATan(height_difference) * (180/np.pi)
slope_np = arcpy.RasterToNumPyArray(slope, '#', '#', '#', -9999)   

# Convert slope to fraction of slope rather than degrees or radians
np.radians(slope_np)
np.tan(slope_np)

# Catch statement for areas with 0 or negative slope
slope_np[slope_np == 0] = 0.000001 
slope_np[slope_np < 0] = 0.000001 
slope_np[DTM == -9999] = -9999 #Readd the no data cells!

# Convert slope to numpy to check if any cells are greater than 45 degrees 
np.save(slope_temp, slope_np)