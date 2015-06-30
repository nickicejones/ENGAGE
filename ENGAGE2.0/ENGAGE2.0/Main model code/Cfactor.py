###### MODEL LOOP DESCRIPTION #####
# The purpose of this file is to calculate the C-factor using values taken from Panagos et al 2015

##### VARIABLES - used in this file #####

#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import numpy as np
import arcpy

# Hardcoded mannings values taken from Kalyanapu et al. and the SWAT handbook
COMBINE_SCS = {             
        
        #WOODLAND CODES
        50: "0.0003", # Broad leaf woodland - Poor condition T
        1 : "0.0002", # Broad leaf woodland - Fair condition T
        51: "0.0001", # Broad leaf woodland - Good condition T
            
        52: "0.0003", # Coniferous woodland - Poor condition T
        2: "0.0002", # Coniferous woodland - Fair condition T
        53: "0.0001", # Coniferous woodland - Good condition T

        73: "0.3", # Woods?grass combination (orchard or tree farm).- Poor condition T
        74: "0.2", # Woods?grass combination (orchard or tree farm).  - Fair condition T
        75: "0.1", # Woods?grass combination (orchard or tree farm).  - Good condition T

        #ARABLE CODES
        3: "0.12", # Arable and horticulture - Good condition T
        54: "0.3", # Arable and horticulture - Poor condition T
        76: "0.5", # Fallow - Bare soil T

        #Grassland CODES
        4: "0.4", # Improved grassland - Poor condition T
        55: "0.30", # Improved grassland - Fair condition T
        56: "0.15", # Improved grassland - Good condition T
        5: "0.035", # Rough grassland T
        6: "0.035", # Neutral grassland T
        7: "0.035", # Calcareous grassland T
        8: "0.035", # Acid grassland (and bracken) T

        #MIS CODES
        10: "0.40", # Heather T
        11: "0.40", # Heather grassland T
        12: "0.0", # Bog (using bespoke value) T
        14: "0.0", # Inland rock (considered to be an impervious value) T
        15: "0.0", # Saltwater T
        16: "0.0", # Freshwater T


        #URBAN CODES
        57: "0.002", # Farmsteds - buildings, lanes, driveways and surrounding lots  T
        23: "0.002", # Suburban T
        22: "0.0003", # Urban T
        65: "0.0003", # Commercial and buisness T
        66: "0.0003", # Industrial T

        #OPEN PARKS / SPACES
        58: "0.003", # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Poor T
        59: "0.003", # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Fair T
        60: "0.003", # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Good T
            
        #IMPERVIOUS AREAS
        61: "0.0", # Paved parking lots, roofs, driveways (Excl right of way) T
        62: "0.0", # Paved streets and roads: open ditches (incl right of way) T
        63: "0.003", # Gravel streets and roads (including right of way) T
        64: "0.003", # Dirt streets and roads (including right of way) T

        #RESIDENTIAL
        67: "0.002", # 1/8 acre or less (town houses) T
        68: "0.002", # 1/4 acre T
        69: "0.002", # 1/3 acre T
        70: "0.002", # 1/2 acre T
        71: "0.002", # 1 acre T
        72: "0.002", # 2 acres T
            
                                      
        # Values not covered in Halcrow report:
        # Would this be the same as bog?
        9: "0.0", # Fen, Marsh Swamp - same as bog? T
               
        # The following are coastal features which are not usually
        # incoporated into SCS curves, the following values are derived
        # from the SCS table
        21: "0.0", # Saltmarsh - same as bog? T
        19: "0.0", # Littoral rock *This was included in the Halcrow report T
               
        # Are these important - as far as I am concerned sand dunes arent
        # going to be feeding into the river?
        17: "0.0", # Supra-litoral rock T
        18: "0.0", # Supra-litoral sediment T
        20: "0.0", # Littoral sediment T
               
        # Mountain habitat
        13: "0.014", # Montane habitats used - fair brush for now. T

        # The unclassified
        24: "0.15", # Permanent Pasture on RDPE agri-environment scheme * T
        25: "0.15", # Permanet Pasture used for dehydrated fodder* T
        26: "0.15", # All other permanent pasture (including grazing woodland)* T
        27: "0.15", # Temporary grass * T
        28: "0.15", # temporary grass used for dehydrated fodder * T
        29: "0.15", # All other temporary grass * T
        30: "0.14", # All protien crops # out in 2011 - Removed * T
        31: "0.14", # Almonds T
        32: "0.14", # Hazelnuts or filberts T
        33: "0.14", # Walnuts T
        34: "0.14", # Pistachios T
        35: "0.14", # Flax T
        36: "0.14", # Hemp T
        37: "0.14", # Hops T
        38: "0.14", # Dehydrated fodder crops T
        39: "0.0002", # Land under woodland grant scheme * T
        40: "0.0002", # Forest/Woodland * T
        41: "0.0002", # RDPE schemes woodland * T
        42: "0.0002", # Forested land that was permanet pasture in 2003 * T
        43: "0.0002", # Land managed as set aside - removed from the data * T
        44: "0.0002", # Removed from the data * T
        45: "0.0", # Agricultural land not in production * T
        46: "0.14", # Crops * T
        47: "0.14", # Crops * T
        48: "0.12", # Permanent Fruit and Vegtables * T
        49: "0.12", # Agri-environment land that does not fit any other catagory - Removed * T

        } 

def get_Cfactor(land_cover):

    def get_C(a1):
        if a1 >= 0:            
            return COMBINE_SCS[a1]
        else:
            return -9999

    V_get_C = np.vectorize(get_C, otypes=["O"])

    CUSLE = np.empty_like(land_cover, dtype=str)
    
    CUSLE = V_get_C(land_cover)
    
    # Convert str to float
    CUSLE = CUSLE.astype(np.float)
    
    # Check no data values
    CUSLE[land_cover == -9999] = -9999

    arcpy.AddMessage("Cfactor for the river catchment calculated")
    arcpy.AddMessage("-------------------------")

    return CUSLE

