##### Description of this python file #####
# This is the file to calculate the active and inactive layer distributions

##### VARIABLES - Used in this file#####
# active_layer_upper_volume_limit - the upper limit volume in the active layer in m3
# active_layer_lower_volume_limit - the lower limit volume in the active layer in m3
# active_layer_GS_P_temp - list of temporary locations on the computer to store the active layer grain size proportions
# active_layer_V_temp - list of temporary locations on the computer to store the active layer grain size volumes
# inactive_layer_GS_P_temp - list of  temporary locations on the computer to store the inactive layer grain size proportions
# inactive_layer_V_temp - list of temporary location ons the computer to store the inactive layer grain size volumes
# cell_size - the cell size of the model
# new_active_layer_total - the new total depth in m3 for the active layer
# new_inactive_layer_total  - the new total depth in m3 for the inactive layer

#---------------------------------------------------------------------#
##### START OF CODE #####

# Import statements
import arcpy
import numpy as np
from itertools import izip

# Function to check and recalculate the depths of the incoming layers.
def active_layer_depth(active_layer, inactive_layer, 
                       active_layer_GS_P_temp, active_layer_V_temp, 
                       inactive_layer_GS_P_temp, inactive_layer_V_temp, cell_size):
            
    
    # Calculate the lower and upper limits for the volume of the active layer
    active_layer_upper_volume_limit = float(0.3 * cell_size * cell_size)
    arcpy.AddMessage("Upper active layer limit set at " + str(active_layer_upper_volume_limit))
    active_layer_lower_volume_limit = float(0.05 * cell_size * cell_size) 
    arcpy.AddMessage("Lower active layer limit set at " + str(active_layer_lower_volume_limit))
    removal_amount = 0.2 * cell_size * cell_size     

    # Count the grainsizes as the model works through them
    grain_size_counter = 1    
         
    # Set up some empty arrays to hold the new values 
    new_active_layer_total = np.zeros_like(active_layer)
    new_inactive_layer_total = np.zeros_like(inactive_layer)
                                                   
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

        new_active_layer_total, new_inactive_layer_total = check_depth(active_layer, inactive_layer, active_layer_proportion, active_layer_volume,
                                                                       inactive_layer_proportion, inactive_layer_volume, 
                                                                       new_active_layer_total, new_inactive_layer_total, 
                                                                       active_layer_upper_volume_limit, active_layer_lower_volume_limit, removal_amount,
                                                                       active_layer_volume_temp, inactive_layer_volume_temp)
        

                                        
        # Increment the grainsize by 1 for the next round of calculations
        grain_size_counter = grain_size_counter + 1

    # Count the grainsizes as the model works through them
    grain_size_counter = 1 

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
                
        active_layer_proportion = active_layer_volume / new_active_layer_total 
        active_layer_proportion[active_layer_volume == 0] = 0
        inactive_layer_proportion =  inactive_layer_volume / new_inactive_layer_total
        inactive_layer_proportion[inactive_layer_volume == 0] = 0      

        np.save(active_layer_proportion_temp, active_layer_proportion)
        np.save(inactive_layer_proportion_temp, inactive_layer_proportion)

        # Increment the grainsize by 1 for the next round of calculations
        grain_size_counter = grain_size_counter + 1

    arcpy.AddMessage("Change to proportions saved to disk")
    arcpy.AddMessage("-------------------------")

    return new_active_layer_total, new_inactive_layer_total

def check_depth(active_layer, inactive_layer, active_layer_proportion, active_layer_volume, inactive_layer_proportion, inactive_layer_volume, new_active_layer_total, new_inactive_layer_total, active_layer_upper_volume_limit, active_layer_lower_volume_limit,removal_amount, active_layer_volume_temp, inactive_layer_volume_temp):  
        # Check the depth of the active layer is not to large or too small
          
        # Array B contains True/False for the condition and is subsequently 
        # used as Boolean index.
        
        B = (active_layer >= active_layer_upper_volume_limit)
        C = active_layer - removal_amount           
        inactive_layer_volume[B] += C[B] * active_layer_proportion[B]
        active_layer_volume[B] = (active_layer[B] - C[B]) * active_layer_proportion[B]
        
        # The "not B" does the "else" part of the elif statement it replaces
        B = ~B & (active_layer < active_layer_lower_volume_limit) & (inactive_layer >= (removal_amount * inactive_layer_proportion))
        
        active_layer_volume[B] += removal_amount * inactive_layer_proportion[B]                      
        inactive_layer_volume[B] -= removal_amount * inactive_layer_proportion[B]

        # The "not B" does the "else" part of the elif statement it replaces
        B = ~B & (active_layer < active_layer_lower_volume_limit) & (inactive_layer < (removal_amount * inactive_layer_proportion))
        active_layer_volume[B] += inactive_layer[B] * inactive_layer_proportion[B]                      
        inactive_layer_volume[B] -= inactive_layer[B] * inactive_layer_proportion[B]

        # The final case where no sediment is present in either layer
        B = ~B & (active_layer == 0) & (inactive_layer == 0)
        active_layer_volume[B] = 0
        inactive_layer_volume[B] = 0      
                                              
        # Add the new calculated volumes to a running total array
        new_active_layer_total += active_layer_volume
        new_inactive_layer_total += inactive_layer_volume
        
        np.save(active_layer_volume_temp, active_layer_volume)
        np.save(inactive_layer_volume_temp, inactive_layer_volume)
        arcpy.AddMessage("Saved updated active and inactive layer volumes")
        arcpy.AddMessage("-------------------------")
                
        # Check the nodata values                          
        new_active_layer_total[active_layer == -9999] = -9999
        new_inactive_layer_total[inactive_layer == -9999] = -9999
        
        return new_active_layer_total, new_inactive_layer_total