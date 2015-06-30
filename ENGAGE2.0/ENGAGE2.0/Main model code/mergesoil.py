##### Description of this python file #####
# This is a module to check the soil depths are correct based on the land use (this prevents soil erosion taking place where no soil erosion should be taking place!


##### VARIABLES - Used in this file#####
# 


#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import arcpy
import numpy as np

Corine = {

        1: 0, #CONTINIOUS URBAN FABRIC
        2: 0,	#DISCONTINUOUS URBAN FABRIC
        3: 0,	#INDUSTRIAL OR COMMERCIAL UNTS
        4: 0,	#ROAD AND RAIL NETWORKS AND ASSOCIATED L
        5: 0,	#PORT AREAS
        6: 0,	#AIRPORTS
        30: 0,	#BEACHES, DUNES, AND SAND PLAINS
        31: 0,	#BARE ROCK
        34: 0,	#GLACIERS AND PERPETUAL SNOW
        35: 0,	#INLAND MARSHES
        36: 0,	#PEATBOGS
        37: 0,	#SALT-MARSHES
        38: 0,	#SALINES
        40: 0, #WATER COURSES
        41: 0, #WATER BODIES
        42: 0, #COASTAL LAGOONS
        43: 0, #ESTUARIES
        44: 0, #SEA AND OCEAN

        #URBAN CODES
        65: 0, # Commercial and buisness T
        66: 0, # Industrial T
            
        #IMPERVIOUS AREAS
        61: 0, # Paved parking lots, roofs, driveways (Excl right of way) T
        62: 0, # Paved streets and roads: open ditches (incl right of way) T
        63: 0, # Gravel streets and roads (including right of way) T
        64: 0, # Dirt streets and roads (including right of way) T

        #RESIDENTIAL
        67: 0, # 1/8 acre or less (town houses) T
        68: 0, # 1/4 acre T
        69: 0, # 1/3 acre T
        70: 0, # 1/2 acre T
        71: 0, # 1 acre T
        72: 0, # 2 acres T

        }

# Values which should not have any soil for Combined land cover
COMBINE_SCS = {             
        12: 0, # Bog (using bespoke value) T
        14: 0, # Inland rock (considered to be an impervious value) T
        15: 0, # Saltwater T
        16: 0, # Freshwater T


        #URBAN CODES
        23: 0, # Suburban T
        22: 0, # Urban T
        65: 0, # Commercial and buisness T
        66: 0, # Industrial T
            
        #IMPERVIOUS AREAS
        61: 0, # Paved parking lots, roofs, driveways (Excl right of way) T
        62: 0, # Paved streets and roads: open ditches (incl right of way) T
        63: 0, # Gravel streets and roads (including right of way) T
        64: 0, # Dirt streets and roads (including right of way) T

        #RESIDENTIAL
        67: 0, # 1/8 acre or less (town houses) T
        68: 0, # 1/4 acre T
        69: 0, # 1/3 acre T
        70: 0, # 1/2 acre T
        71: 0, # 1 acre T
        72: 0, # 2 acres T
            
                                      
        # Values not covered in Halcrow report:
        # Would this be the same as bog?
        9: 0, # Fen, Marsh Swamp - same as bog? T
               
        # The following are coastal features which are not usually
        # incoporated into SCS curves, the following values are derived
        # from the SCS table
        21: 0, # Saltmarsh - same as bog? T
        19: 0, # Littoral rock *This was included in the Halcrow report T
               
        # Are these important - as far as I am concerned sand dunes arent
        # going to be feeding into the river?
        17: 0, # Supra-litoral rock T
        18: 0, # Supra-litoral sediment T
        20: 0, # Littoral sediment T

        } 


# Function to check what the soil depth should be based on land cover and merging the existing soil depths
def calculate_soil_depth(land_cover, land_cover_type, ASD_soil_depth, BGS_soil_depth, general_soil_depth):

    # Create an empty numpy array to store the new soil depths
    final_soil_depth = np.zeros_like(land_cover, dtype = float)
    
    # Bit of the script to sort out the various input features into the script
    if ASD_soil_depth and ASD_soil_depth != '#':
    # Check to see which cells have sediment and not equal to the default value
        B = [ASD_soil_depth > 0]
        final_soil_depth[B] = river_soil_depth[B]

        # If BGS soil depth data has been provided then use that ## Note to self this may result in the filling in of cells that should be bedrock - consider removing or allocating based on flow accumulation. - Check with Chris.
        if BGS_soil_depth and BGS_soil_depth != '#':
            # Swap B round to be true for the other cells
            B = ~B
            final_soil_depth[B] = BGS_soil_depth[B]

    elif BGS_soil_depth and BGS_soil_depth != '#':
        final_soil_depth = BGS_soil_depth

    else:
        final_soil_depth = general_soil_depth

    if land_cover_type == "LCM 2007":
        def get_soil_depths(a1):
            if a1 > 0:
                return COMBINE_SCS[a1]  
            else:
                return -9999

        V_get_soil_depths = np.vectorize(get_soil_depths)
        
        land_cover_soil_depths = np.zeros_like(land_cover, dtype = np.int8)

        land_cover_soil_depths = V_get_soil_depths(land_cover)

        arcpy.AddMessage("Soil depths based LCM 2007 land cover data calculated")
        arcpy.AddMessage("-------------------------")

    # Method for calculating the CN2 number from CORINE data
    elif land_cover_type == "CORINE 2006":
        def get_soil_depths(a1):
            if a1 > 0:
                return Corine[a1]  
            else:
                return -9999

        V_get_soil_depths = np.vectorize(get_soil_depths)
        
        land_cover_soil_depths = np.zeros_like(land_cover, dtype = np.int8)

        land_cover_soil_depths = V_get_soil_depths(land_cover)

        arcpy.AddMessage("Soil depths based CORINE land cover data calculated")
        arcpy.AddMessage("-------------------------")
        
    # This checks to see which parts should have no soil depth and converts the final soil depth based on that.
    B = (land_cover_soil_depths == 0)
    final_soil_depth[B] = land_cover_soil_depths[B]

    return final_soil_depth