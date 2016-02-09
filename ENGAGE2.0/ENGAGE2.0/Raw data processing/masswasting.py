##### Description of this python file #####
# This is the file to calculate the adjusted elevation and determine whether or not slope/flow directions need to be recalculated

##### VARIABLES - Used in this file#####
# DTM - Digital terrain model of the river catchment
# cell_size - the cell size of the model
# nbr - area of search in ArcGIS
# lowest_cell - raster containing the value of the minimum surrounding elevation
# height_difference - difference between the elevation of each cell and the surrounding cell
# slope - the slope of the river catchment in degrees
# slope_threshold - a value which must be exceeded for mass wasting to take place.
#
#

#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import numpy as np
import arcpy
from arcpy.sa import *
from itertools import izip
import gc

class masswasting_sediment(object):

    def calculate_slope_fraction_raster_in(self, DTM, bottom_left_corner, cell_size):
                
        # Set local variables
        nbr = NbrRectangle(3, 3, "CELL")

        # Execute BlockStatistics to find the minimum surrounding cell
        lowest_cell = FocalStatistics(DTM, nbr, "MINIMUM", "DATA")

        # Calculate the difference between the DTM and the lowest surrounding cell
        height_difference = DTM - lowest_cell  
        
        # Calculate the slope between cells
        # First calculate opposite over adjacent
        height_difference /= cell_size
        
        # Then use inverse tan to calculate the slope
        slope = ATan(height_difference) * (180/np.pi)

        # Convert slope to numpy to check if any cells are greater than 45 degrees
        slope = arcpy.RasterToNumPyArray(slope, '#', '#', '#', -9999)    

        # Convert slope to fraction of slope rather than degrees or radians
        np.radians(slope)
        np.tan(slope)

        # Catch statement for areas with 0 slope
        slope[slope == 0] = 0.0001 
        arcpy.AddMessage("Slope calculated")
        arcpy.AddMessage("-------------------------")

        return slope

    def calculate_slope_fraction(self, DTM_ras, bottom_left_corner, cell_size, save_date):

        # Convert the DTM to a raster
        #DTM_ras = arcpy.NumPyArrayToRaster(DTM, bottom_left_corner, cell_size, cell_size, -9999)
        #DTM_ras.save("ele_" + save_date)

        # Set local variables
        nbr = NbrRectangle(3, 3, "CELL")

        # Execute BlockStatistics to find the minimum surrounding cell
        lowest_cell = FocalStatistics(DTM_ras, nbr, "MINIMUM", "DATA")

        # Calculate the difference between the DTM and the lowest surrounding cell
        height_difference = DTM_ras - lowest_cell  
        
        # Calculate the slope between cells
        # First calculate opposite over adjacent
        height_difference /= cell_size
        
        # Then use inverse tan to calculate the slope
        slope = ATan(height_difference) * (180/np.pi)

        ### SAVE A COPY OF THE SLOPE and DTM FOR TESTING PURPOSE ONLY ### 
        #slope.save("slope" + save_date)

        # Convert slope to numpy to check if any cells are greater than 45 degrees
        slope_np = arcpy.RasterToNumPyArray(slope, '#', '#', '#', -9999)    

        # Convert slope to fraction of slope rather than degrees or radians
        np.radians(slope_np)
        np.tan(slope_np)

        # Clean up after DTM
        arcpy.Delete_management(DTM_ras)
        arcpy.Delete_management(lowest_cell)
        del slope, DTM_ras, height_difference

        # Catch statement for areas with 0 or negative slope
        slope_np[slope_np == 0] = 0.0001 
        slope_np[slope_np < 0] = 0.0001 
        arcpy.AddMessage("Slope calculated")
        arcpy.AddMessage("-------------------------")

        return slope_np