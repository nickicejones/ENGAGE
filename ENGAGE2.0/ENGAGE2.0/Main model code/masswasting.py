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

### Import Script Files NJ created ###
import active_inactive_layer_check
import elevation_adjustment

class masswasting_sediment(object):
### A function to calculate the lowest cell in a neighbour hood. This is using tanX = Opposite (Height difference) / Adjacent (Cell width) ###
    
    def calculate_slope(self, DTM, bottom_left_corner,cell_size):

        DTM = arcpy.NumPyArrayToRaster(DTM, bottom_left_corner, cell_size, cell_size, -9999)

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

    def get_cellsgreater_45degrees(self, slope, active_layer, inactive_layer):

        def is_empty(any_structure):
            if any_structure:              
                return False
            else:              
                return True

        
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
        

        # Check that if the slope is greater than 45 degrees that there is availiable sediment to move 
        final_idx = []
        for x in new_idx:
            if active_layer[x] != 0 and inactive_layer[x] != 0:
                final_idx.append(x)
       
        empty = is_empty(final_idx)

        # Now check that there are slopes greater than 45 degrees and that there is availiable sediment to move
        if np.any(slope_mask >= 45) and empty == False:
            carryout_masswasting = True
            arcpy.AddMessage("There are cells with a steep slope therefore mass wasting will be calculated.")
        else:
            carryout_masswasting = False
            arcpy.AddMessage("Mass wasting will not be calculated.")

        arcpy.AddMessage("-------------------------")

        return carryout_masswasting, final_idx

    def sediment_movement_amount(self, active_layer_proportion, new_idx, cell_size):
        
        sediment_entrainment_out = np.zeros_like(active_layer_proportion, dtype = float)

        removal_amount = 0.05 * (cell_size * cell_size)

        for i, j in new_idx:
            sediment_entrainment_out[i, j] = active_layer_proportion[i, j] * removal_amount

        return sediment_entrainment_out

    def move_sediment(self, sediment_entrainment_out, new_idx, flow_direction_np):

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
                           

        sediment_entrainment_in_fin = np.zeros_like(flow_direction_np, dtype=float)
        sediment_entrainment_in_fin = sediment_entrainment_in[1:-1, 1:-1] 
        sediment_entrainment_in_fin[flow_direction_np == -9999] = -9999

        return sediment_entrainment_in_fin

    def masswasting_loop(self, DTM, DTM_MINUS_AL_IAL, active_layer, inactive_layer, bottom_left_corner, cell_size, flow_direction_np, 
                                                            active_layer_GS_P_temp, active_layer_V_temp, 
                                                            inactive_layer_GS_P_temp, inactive_layer_V_temp):

        # First calculate the slope of the cells
        arcpy.AddMessage("Checking is any cells have a slope greater than 45 degrees and sediment is available to be transported")
        np.set_printoptions(precision=4)
        slope = self.calculate_slope(DTM, bottom_left_corner, cell_size)

        # Check if any of then are greater than 45 degrees
        conduct_masswasting, new_idx = self.get_cellsgreater_45degrees(slope, active_layer, inactive_layer)
             
        grain_size_counter = 1
        while conduct_masswasting == True:
            

            total_volume = np.zeros_like(slope, dtype = float)
            for active_layer_proportion_temp, active_layer_volume_temp in izip(active_layer_GS_P_temp, active_layer_V_temp):

                # Locad the arrays from the disk
                active_layer_proportion = np.load(active_layer_proportion_temp)
                active_layer_volume = np.load(active_layer_volume_temp)
                                
                # Calculate the amount of sediment that can be moved out of each cell
                sediment_entrainment_out = self.sediment_movement_amount(active_layer_proportion, new_idx, cell_size)
                 
                # Calculate sediment transport in for that grainsize
                sediment_entrainment_in = self.move_sediment(sediment_entrainment_out, new_idx, flow_direction_np)
                                
                # Calculate the change in sediment volume
                new_grain_volume = active_layer_volume - sediment_entrainment_out + sediment_entrainment_in               
                np.save(active_layer_volume_temp, new_grain_volume)
                                                 
                # Update the total volume
                total_volume += new_grain_volume
                           
                # Increment the grainsize by 1 for the next round of calculations
                grain_size_counter = grain_size_counter + 1

            # Collect garbage
            del sediment_entrainment_out, sediment_entrainment_in, new_grain_volume
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected))

            # Count the grainsizes as the model works through them
            grain_size_counter = 1 

            for active_layer_proportion_temp, active_layer_volume_temp in izip(active_layer_GS_P_temp, active_layer_V_temp):
                # Locad the arrays from the disk                
                active_layer_volume = np.load(active_layer_volume_temp)
                active_layer_proportion  = active_layer_volume / total_volume

                arcpy.AddMessage("Calculated new proportions after mass wasting for grainsize " + str(grain_size_counter)) 
                
                # Check for nodata and nan values and save to disk
                active_layer_proportion[total_volume == 0] = 0
                active_layer_proportion[slope == -9999] = -9999 
                np.save(active_layer_proportion_temp, active_layer_proportion) 

                # Update the counter
                grain_size_counter += 1
                if grain_size_counter == 8:
                    grain_size_counter = 1


            del active_layer_volume, active_layer_proportion

            # Collect garbage
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected))  

            # Need to update active layer and inactive layer depths if required.               
            active_layer, inactive_layer = active_inactive_layer_check.active_layer_depth(total_volume, inactive_layer, active_layer_GS_P_temp, active_layer_V_temp, 
                                                            inactive_layer_GS_P_temp, inactive_layer_V_temp, cell_size)
                        
            # Convert DTM back to a raster
            #DTM = arcpy.RasterToNumPyArray(DTM, '#', '#', '#', -9999)  
            # Need to recalculate the DTM
            ### Check if elevations need to be recalculated ###
            DTM, DTM_MINUS_AL_IAL, recalculate_slope_flow = elevation_adjustment.update_DTM_elevations(DTM, DTM_MINUS_AL_IAL, active_layer, inactive_layer, cell_size)
            
            inactive_layer *= (cell_size*cell_size)
            active_layer *= (cell_size*cell_size)
                        
            slope = self.calculate_slope(DTM, bottom_left_corner, cell_size)
            
            # Check if any of then are greater than 45 degrees
            conduct_masswasting, new_idx = self.get_cellsgreater_45degrees(slope, active_layer, inactive_layer)
            
        return DTM, DTM_MINUS_AL_IAL, recalculate_slope_flow, active_layer, inactive_layer