##### Description of this python file #####
# This is the file to calculate hillslope erosion using the MUSLE (Modified Universal Soil Loss Equation)

##### VARIABLES - Used in this file#####
# active_layer_GS_P_temp - list of temporary locations on the computer to store the active layer grain size proportions
# total_proportion_rock - proportion of the active layer that is rock
# GS_list - list of the 7 grainsizes used in the model
# grain_size - the grain size that is being iterated through
# active_layer_proportion_temp - the location of the temporary location for that grainsize
# active_layer_proportion - proportion of the active layer 
# CFRG - coarse Fragement factor in the MUSLE

#---------------------------------------------------------------------#
##### START OF CODE #####

# Import statements
import arcpy
import numpy as np

class hillslope_erosion_MUSLE(object):

    def __init__(self, slope, cell_size):
        self.slope = slope
        self.cell_size = cell_size

    # Function to calcultate the CRFG (Coarse Fragement) factor in the MUSLE
    def calculate_CFRG(self, GS_list, active_layer_GS_P_temp):
        
        # Empty array to store the proportion of rock in the top soil layer
        total_proportion_rock = np.zeros_like(self.slope)

        # Iterate through the layers and check if they are over a certain value add it to a running total
        for grain_size, active_layer_proportion_temp in izip(GS_list, active_layer_GS_P_temp):
                        
            # Locad the arrays from the disk
            active_layer_proportion = np.load(active_layer_proportion_temp)

            if grain_size > 0.002:
                total_proportion_rock += active_layer_proportion
        
        # Convert the proportion to %
        total_proportion_rock *= 100
        
        CFRG = np.exp(-0.053*total_proportion_rock)

        return CFRG

    # Function to calculate the LSULSE (Topographic Factor)
    def calculate_LSULSE(self, slope):

        slope_angle = np.arctan(slope)

        m = 0.6 * ( 1 - np.exp(-35.835 * slope))

        LSULSE = np.power(cell_size/22.1, m) * (65.41 * (np.power(np.sin(slope_angle), 2) + (4.56*np.sin(slope_angle)) + 0.065))

        return LSULSE

    # Function to calculate KUSLE (Soil Erodibility Factor)
    def calculate_KUSLE(self):

        return KUSLE

    # Function to calculate CUSLE (Cover and Management Factor)
    def calculate_CULSE(self):

        return CULSE

    # Function to calculate PULSE (Support Pracitce Factor)
    def calculate_PUSLE(self):

        return PUSLE
        
    # Final function to calculate the MUSLE (Modified Universal Soil Loss Equation)
    def calculate_MUSLE(self, Q_surf_np, q_peak, hru_area, KUSLE, CUSLE, PUSLE, LSULSE, CFRG):

        hillslope_sediment_erosion = 11.8 * np.power((Q_surf_np * q_peak * hru_area), 0.56) * KUSLE * CUSLE * PUSLE * LSULSE * CFRG

        return hillslope_sediment_erosion