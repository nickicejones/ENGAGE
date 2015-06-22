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

### Import Script Files NJ created ###


class masswasting_sediment(object):
### A function to calculate the lowest cell in a neighbour hood. This is using tanX = Opposite (Height difference) / Adjacent (Cell width) ###
    
    def calculate_slope(self, DTM, cell_size):
        
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
        
        return slope

    def get_cellsgreater_45degrees(self, slope):

        # The follow code is adapted from the peice of code that moves sediment through the system
        slope_mask = np.zeros_like(slope, dtype = float)
        slope_threshold = 45

        # Get indices with great enough slope to intiate mass wasting    
        # - this only gets the cells with great enough slope for sediment movemnet to occur by mass wasting 
        np.putmask(slope_mask, slope >= 45, slope)
      
        # Get the indices where the sediment transport is greater than 0 
        sort_idx = np.flatnonzero(slope_mask)

        # Now return those indices as a list
        new_idx = zip(*np.unravel_index(sort_idx[::-1], slope.shape))

        if np.any(slope_mask >= 45):
            carryout_masswasting = True
            arcpy.AddMessage("There are cells with a steep slope therefore masswasting will be calculated.")
        else:
            carryout_masswasting = False
            arcpy.AddMessage("Mass wasting will not be calculated.")

        return carryout_masswasting, new_idx

    def sediment_movement_amount(self, GS_P, GS_V, cell_size):
        
        sediment_entrainment_out = np.zeros_like(DTM, dtype = float)

    def move_sediment(self, new_idx, flow_direction_np):

        # Get the rows and columns of the slope file
        nrows, ncols = flow_direction_np.shape
                
        # Pads the array with zeros to prevent negative indexing
        tmp = np.zeros((nrows+2, ncols+2), dtype = float) 
        tmp[1:-1, 1:-1] = sediment_entrainment_out
        sediment_entrainment_out = tmp
            
        # Create empty array for the moved sediment
        sediment_entrainment_in = np.zeros_like(sediment_entrainment_out, dtype = float)
                       
        lookup = {32: (-1, -1), 
                    16: (0, -1), 
                    8:(1, -1), 
                    4:(1,  0),             
                    64: (-1,  0),             
                    128:(-1,  1),             
                    1:   (0,  1),             
                    2:   (1,  1)}

        for i, j in new_idx:
        # Need to take into account the offset in the "padded_transport"
            r, c = i + 1, j + 1
            # This also allows for flow_direction values not listed above...
            dr, dc = lookup.get(flow_direction_np[i, j], (0,0)) # Gets the flow direction for that cell
        #if grain_transport_mask[r, c] <= grain_size_active_layer_mask[r, c]: # this adds in a check to make sure that there is sufficient sediment in the active layer to transport it. 
            sediment_entrainment_in[r + dr, c + dc] += sediment_entrainment_out[r, c] # move the sediment in the downstream direction by one timestep.
                           

        sediment_entrainment_in_fin = np.zeros_like(slope, dtype=float)
        sediment_entrainment_in_fin = sediment_entrainment_in[1:-1, 1:-1] 
        sediment_entrainment_in_fin[slope == -9999] = -9999

    def masswasting_loop(self, DTM, DTM_MINUS_AL_IAL, active_layer, inactive_layer, cell_size, flow_direction_np, 
                                                            active_layer_GS_P_temp, active_layer_V_temp, 
                                                            inactive_layer_GS_P_temp, inactive_layer_V_temp):

        # First calculate the slope of the cells
        arcpy.AddMessage("Checking is any cells have a slope greater than 45 degrees and sediment is available to be transported")
        slope = self.calculate_slope(DTM, cell_size)
        print slope

        # Check if any of then are greater than 45 degrees
        conduct_masswasting, new_idx = self.get_cellsgreater_45degrees(slope)
        print conduct_masswasting
        print new_idx


         ### ~~~ GOT TO HERE ~~~ ###
        for active_layer_proportion_temp, active_layer_volume_temp, inactive_layer_proportion_temp, inactive_layer_volume_temp in izip(active_layer_GS_P_temp,
                                                                                                                                    active_layer_V_temp,
                                                                                                                                    inactive_layer_GS_P_temp, 
                                                                                                                                    inactive_layer_V_temp):
            # Locad the arrays from the disk
            active_layer_proportion = np.load(active_layer_proportion_temp)
            active_layer_volume = np.load(active_layer_volume_temp)
            inactive_layer_proportion = np.load(inactive_layer_proportion_temp)
            inactive_layer_volume = np.load(inactive_layer_volume_temp)
            arcpy.AddMessage("Loaded arrays for grain size " + str(grain_size_counter))

            sediment_entrainment_out = self.sediment_movement_amount(GS_P, GS_V, cell_size)
     

                
                                        
        # Increment the grainsize by 1 for the next round of calculations
        grain_size_counter = grain_size_counter + 1

    # Count the grainsizes as the model works through them
    grain_size_counter = 1 