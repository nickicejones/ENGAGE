###### MODEL LOOP DESCRIPTION #####
# The purpose of this file is to calculate the mannings roughness using the landcover data

##### VARIABLES - used in this file #####

#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import numpy as np
import arcpy

# Hardcoded mannings values taken from Kalyanapu et al. and the SWAT handbook

COMBINE_SCS = {             
        
        #WOODLAND CODES
        50: "0.36", # Broad leaf woodland - Poor condition
        1 : "0.36", # Broad leaf woodland - Fair condition
        51: "0.36", # Broad leaf woodland - Good condition
            
        52: "0.32", # Coniferous woodland - Poor condition
        2: "0.32", # Coniferous woodland - Fair condition
        53: "0.32", # Coniferous woodland - Good condition

        73: "0.36", # Woods?grass combination (orchard or tree farm).- Poor condition
        74: "0.36", # Woods?grass combination (orchard or tree farm).  - Fair condition
        75: "0.36", # Woods?grass combination (orchard or tree farm).  - Good condition

        #ARABLE CODES
        3: "0.19", # Arable and horticulture - Good condition
        54: "0.09", # Arable and horticulture - Poor condition
        76: "0.0113", # Fallow - Bare soil

        #Grassland CODES
        4: "0.368", # Improved grassland - Poor condition
        55: "0.368", # Improved grassland - Fair condition
        56: "0.368", # Improved grassland - Good condition
        5: "0.368", # Rough grassland
        6: "0.368", # Neutral grassland
        7: "0.368", # Calcareous grassland
        8: "0.368", # Acid grassland (and bracken)

        #MIS CODES
        10: "0.40", # Heather
        11: "0.40", # Heather grassland
        12: "0.0", # Bog (using bespoke value)
        14: "0.0", # Inland rock (considered to be an impervious value)
        15: "0.0", # Saltwater
        16: "0.0", # Freshwater


        #URBAN CODES
        57: "0.0678", # Farmsteds - buildings, lanes, driveways and surrounding lots
        23: "0.0678", # Suburban
        22: "0.0404", # Urban
        65: "0.0404", # Commercial and buisness
        66: "0.0404", # Industrial

        #OPEN PARKS / SPACES
        58: "0.368", # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Poor
        59: "0.368", # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Fair
        60: "0.368", # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Good
            
        #IMPERVIOUS AREAS
        61: "0.0404", # Paved parking lots, roofs, driveways (Excl right of way)
        62: "0.0404", # Paved streets and roads: open ditches (incl right of way)
        63: "0.0404", # Gravel streets and roads (including right of way)
        64: "0.0404", # Dirt streets and roads (including right of way)

        #RESIDENTIAL
        67: "0.0678", # 1/8 acre or less (town houses)
        68: "0.0678", # 1/4 acre
        69: "0.0678", # 1/3 acre
        70: "0.0678", # 1/2 acre
        71: "0.0678", # 1 acre
        72: "0.0678", # 2 acres
            
                                      
        # Values not covered in Halcrow report:
        # Would this be the same as bog?
        9: "0.0", # Fen, Marsh Swamp - same as bog?
               
        # The following are coastal features which are not usually
        # incoporated into SCS curves, the following values are derived
        # from the SCS table
        21: "0.0", # Saltmarsh - same as bog?
        19: "0.0", # Littoral rock *This was included in the Halcrow report
               
        # Are these important - as far as I am concerned sand dunes arent
        # going to be feeding into the river?
        17: "0.0", # Supra-litoral rock
        18: "0.0", # Supra-litoral sediment
        20: "0.0", # Littoral sediment
               
        # Mountain habitat
        13: "0.40", # Montane habitats used - fair brush for now.

        # The unclassified
        24: "0.325", # Permanent Pasture on RDPE agri-environment scheme *
        25: "0.325", # Permanet Pasture used for dehydrated fodder*
        26: "0.325", # All other permanent pasture (including grazing woodland)*
        27: "0.368", # Temporary grass *
        28: "0.368", # temporary grass used for dehydrated fodder *
        29: "0.368", # All other temporary grass *
        30: "0.19", # All protien crops # out in 2011 - Removed *
        31: "0.19", # Almonds
        32: "0.19", # Hazelnuts or filberts
        33: "0.19", # Walnuts
        34: "0.19", # Pistachios
        35: "0.19", # Flax
        36: "0.19", # Hemp
        37: "0.19", # Hops
        38: "0.19", # Dehydrated fodder crops
        39: "0.40", # Land under woodland grant scheme *
        40: "0.40", # Forest/Woodland *
        41: "0.40", # RDPE schemes woodland *
        42: "0.40", # Forested land that was permanet pasture in 2003 *
        43: "0.19", # Land managed as set aside - removed from the data *
        44: "0.19", # Removed from the data *
        45: "0.19", # Agricultural land not in production *
        46: "0.19", # Crops *
        47: "0.19", # Crops *
        48: "0.19", # Permanent Fruit and Vegtables *
        49: "0.19", # Agri-environment land that does not fit any other catagory - Removed *

        } 

def get_mannings(land_cover):

    def get_mannings_n(a1):
        if a1 >= 0:
            return COMBINE_SCS[a1]
        else:
            return -9999

    V_get_mannings_n = np.vectorize(get_mannings_n, otypes=["O"])

    mannings_n = np.empty_like(land_cover, dtype = str)

    mannings_n = V_get_mannings_n(land_cover)
    
    # Convert str to float
    mannings_n = mannings_n.astype(np.float)
    
    # Check no data values
    mannings_n[land_cover == -9999] = -9999

    arcpy.AddMessage("Mannings N for the river catchment calculated")
    arcpy.AddMessage("-------------------------")

    return mannings_n

