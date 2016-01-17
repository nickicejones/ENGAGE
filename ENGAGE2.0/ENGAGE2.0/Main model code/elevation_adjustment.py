##### Description of this python file #####
# This is the file to calculate the adjusted elevation and determine whether or not slope/flow directions need to be recalculated

##### VARIABLES - Used in this file#####
# DTM - Digital terrain model of the river catchment
# active_layer - the top 20 metres squared of the soil in the river channel that is considered to be actively available for transport (units are in metres squared)
# inactive_layer - the remaining soil depth left in the river channel and is not considered to be avaliable for transport (units are in metres squared)
# cell_size - the cell size of the model
# DTM_MINUS_AL_IAL - the elevation of the catchment minus the active layer and inactive layer
#
#
#
#
#
#

#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import numpy as np
import arcpy

# Function to calculate DTM_AL_IAL at the start
def get_DTM_AL_IAL(DTM, active_layer, inactive_layer, cell_size):

    # Convert active layer and inactive layer to meters by dividing by cell size squared
    active_layer /= (cell_size*cell_size) 
    inactive_layer /= (cell_size*cell_size)
    DTM_MINUS_AL_IAL = DTM - active_layer - inactive_layer

    return DTM_MINUS_AL_IAL


# Function to calculate the updated DTM
def update_DTM_elevations(DTM_previous, DTM_MINUS_AL_IAL, active_layer, inactive_layer, cell_size):
         
    # Covert active_layer and inactive layer to meters by dividing by cell size 
    active_layer /= (cell_size*cell_size) 
    inactive_layer /= (cell_size*cell_size) 
    
    # Update the two DTMs
    DTM_current = DTM_MINUS_AL_IAL + active_layer + inactive_layer

    DTM_difference = DTM_current - DTM_previous

    B = np.logical_or(DTM_difference > 0.04, DTM_difference < -0.04)

    if np.any(B == True):
        arcpy.AddMessage("Need to recalculate elevation, slope and flow directions")
        recalculate_slope_flow = True

    else:
        recalculate_slope_flow = False

    # Convert active and inactive back to volumes by multiplying by the cell size
    inactive_layer *= (cell_size*cell_size)
    active_layer *= (cell_size*cell_size)
        
    return DTM_current, DTM_MINUS_AL_IAL, recalculate_slope_flow