##### Description of this python file #####
# This is the file to calculate hillslope erosion using the MUSLE (Modified Universal Soil Loss Equation)

##### VARIABLES - Used in this file#####
# self.cell_size - the cell size of the model
# self.slope - the slope of the cell in the model - rise / run
# active_layer_GS_P_temp - list of temporary locations on the computer to store the active layer grain size proportions
# total_proportion_rock - proportion of the active layer that is rock
# GS_list - list of the 7 grainsizes used in the model
# grain_size - the grain size that is being iterated through
# active_layer_proportion_temp - the location of the temporary location for that grainsize
# active_layer_proportion - proportion of the active layer 
# CFRG - coarse Fragement factor in the MUSLE
# slope_angle - the angle of the slope - degrees
# Fcsand - factor to give low erodibility for soils with high coarse-sand contents and highvalues for soils with little sand
# Fcl_si - gives low erodibility for soils with high lay to silt ratios
# ForgC - factor that reduces soil erodibility for soils with high organic carbon content
# Fhisand - factor that reduces soil erodibility for soils with extremely high sand contents
# Msand - percent sand content (0.05 - 2mm)
# Msilt - percent silt content (0.002-0.05mm)
# Mclay - percent clay content ( <0.002mm)

#---------------------------------------------------------------------#
##### START OF CODE #####

# Import statements
import arcpy
import numpy as np
from itertools import izip

class hillslope_erosion_MUSLE(object):

    def __init__(self, slope, cell_size, GS_list, active_layer_GS_P_temp):
        self.slope = slope
        self.cell_size = cell_size
        self.GS_list = GS_list
        self.active_layer_GS_P_temp = active_layer_GS_P_temp

    # Function to calculate KUSLE (Soil Erodibility Factor)
    def calculate_KUSLE(self, orgC):
        
        ### Calculate Msand, Mclay and Msilt ###
        Msand = np.zeros_like(self.slope)
        Msilt = np.zeros_like(self.slope) 
        Mclay = np.zeros_like(self.slope)

        # Function to calculate Msand, Msilt and Mclay
        def calculate_MsandMsiltMclay(Msand, Msilt, Mclay, grain_proportion, grain_size):
            if grain_size > 0.00005 and grain_size <= 0.002:                
                Msand += grain_proportion
            if grain_size > 0.000002 and grain_size <= 0.00005: 
                Msilt += grain_proportion
            if grain_size < 0.000002: 
                Mclay += grain_proportion
                             
            return Msand, Msilt, Mclay

        # Iterate through the layers and check if they are over a certain value add it to a running total
        for grain_size, active_layer_proportion_temp in izip(self.GS_list, self.active_layer_GS_P_temp):
                        
            # Locad the arrays from the disk
            grain_proportion = np.load(active_layer_proportion_temp)

            Msand, Msilt, Mclay = calculate_MsandMsiltMclay(Msand, Msilt, Mclay, grain_proportion, grain_size)
        
        # Check no data values
        Msand[self.slope == -9999] = -9999
        Msilt[self.slope == -9999] = -9999
        Mclay[self.slope == -9999] = -9999

        # Calculate Fsand - factor to give low erodibility for soils with high coarse-sand contents
        Fcsand = (0.2 + 0.3 * np.exp(-2.56 * Msand * (1 - (Msilt/100))))

        # Calcualte Fcl_si - gives low erodibility for soils with high lay to silt ratios
        Fcl_si = np.power((Msilt / (Mclay + Msilt)), 0.3)

        # Calculate ForgC - factor that reduces soil erodibility for soils with high organic carbon content
        ForgC = (1 - ((0.25 * orgC)/(orgC + np.exp(3.72 - (2.95 * orgC)))))

        # Calculate Fhisand - factor that reduces soil erodibility for soils with extremely high sand contents
        Fhisand = (1 - (0.7 * (1 - (Msand / 100))/((1 - (Msand / 100) + np.exp(-5.51 + 22.9 * (1 - (Msand / 100)))))))

        # Calculate KUSLE (Soil Erodibility Factor)
        KUSLE = Fcsand * Fcl_si * ForgC * Fhisand

        # Check nodata values
        KUSLE[self.slope == -9999] = -9999

        return KUSLE

    # Function to calculate PULSE (Support Pracitce Factor) - this is only applicable to arable land cover and will need more research
    def calculate_PUSLE(self):

        PUSLE = 0.95 # This is a constant calculated by Panagos for the UK using european data and uses the assumption that farmers are following european practices, this can be adapted at a later date to increase complexity and accuracy of the calculated value.

        return PUSLE

    # Function to calculate the LSULSE (Topographic Factor)
    def calculate_LSULSE(self):

        slope_angle = np.arctan(self.slope)

        m = 0.6 * ( 1 - np.exp(-35.835 * self.slope))

        LSULSE = np.power(self.cell_size/22.1, m) * (65.41 * (np.power(np.sin(slope_angle), 2) + (4.56*np.sin(slope_angle)) + 0.065))
        
        # Check nodata values
        LSULSE[self.slope == -9999] = -9999

        return LSULSE

    # Function to calcultate the CRFG (Coarse Fragement) factor in the MUSLE
    def calculate_CFRG(self):
        
        # Empty array to store the proportion of rock in the top soil layer
        total_proportion_rock = np.zeros_like(self.slope)

        # Iterate through the layers and check if they are over a certain value add it to a running total
        for grain_size, active_layer_proportion_temp in izip(self.GS_list, active_layer_GS_P_temp):
                        
            # Locad the arrays from the disk
            active_layer_proportion = np.load(active_layer_proportion_temp)

            if grain_size > 0.002:
                total_proportion_rock += active_layer_proportion
        
        # Convert the proportion to %
        total_proportion_rock *= 100
        
        CFRG = np.exp(-0.053*total_proportion_rock)
        CFRG[self.slope == -9999] = -9999

        return CFRG
        
    # Final function to calculate the MUSLE (Modified Universal Soil Loss Equation)
    def calculate_MUSLE(self, Q_surf_np, q_peak, orgC, CUSLE):

        KUSLE = self.calculate_KUSLE(orgC)
        PUSLE = self.calculate_PUSLE()
        LSULSE = self.calculate_LSULSE()
        CFRG = self.calculate_CFRG()

        hru_area = (self.cell_size * self.cell_size)

        hillslope_sediment_erosion = 11.8 * np.power((Q_surf_np * q_peak * hru_area), 0.56) * KUSLE * CUSLE * PUSLE * LSULSE * CFRG

        # Check no data cell
        hillslope_sediment_erosion[self.slope == -9999] = -9999
        return hillslope_sediment_erosion