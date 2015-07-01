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
    1:	0, #CONTINIOUS URBAN FABRIC
    2: 0,	#DISCONTINUOUS URBAN FABRIC
    3: 0,	#INDUSTRIAL OR COMMERCIAL UNTS
    4: 0,	#ROAD AND RAIL NETWORKS AND ASSOCIATED L
    5: 0,	#PORT AREAS
    6: 0,	#AIRPORTS
    7: 1,	#MINERAL EXTRACTION SITES
    8: 1,	#DUMP SITES
    9: 1,	#CONSTRUCTION SITES
    10: 1,	#GREEN URBAN AREAS
    11: 1,	#SPORT AND LEISURE FACILITIES
    12: 1,	#NON-IRRIGATED ARABLE LAND
    13: 1,	#PERMANENTLY IRRIGATED LAND
    14: 1,	#RICE FIELDS
    15: 1,	#VINEYARDS
    16: 1,	#FRUIT TREES AND BERRY PLANTATIONS
    17: 1,	#OLIVE GROWES
    18: 1,	#PASTURES
    19: 1,	#ANNUAL CROPS ASSOCIATED WITH PERMANENT
    20: 1,	#COMPLEX CULTIVATION PATTERNS
    21: 1,	#AGRICULTURE, WITH SIGNIFICANT AREAS OF
    22: 1,	#AGRO-FORESTRY AREAS
    23: 1,	#BROAD-LEAVED FOREST
    24: 1,	#CONIFEROUS FOREST
    25: 1,	#MIXED FOREST
    26: 1,	#NATURAL GRASSLAND
    27: 1,	#MOORS AND HEATHLAND
    28: 1,	#SCLEROPHYLLOUS VEGETATION
    29: 1,	#TRANSITIONAZL WOODLAND-SHRUB
    30: 1,	#BEACHES, DUNES, AND SAND PLAINS
    31: 0,	#BARE ROCK
    32: 1,	#SPARSELY VEGETATED AREAS
    33: 1,	#BURNT AREAS
    34: 0,	#GLACIERS AND PERPETUAL SNOW
    35: 0,	#INLAND MARSHES
    36: 0,	#PEATBOGS
    37: 0,	#SALT-MARSHES
    38: 0,	#SALINES
    39: 0,	#INTERTIDAL FLATS
    40: 0, #WATER COURSES
    41: 0, #WATER BODIES
    42: 0, #COASTAL LAGOONS
    43: 0, #ESTUARIES
    44: 0, #SEA AND OCEAN

    #WOODLAND CODES
    50: 1, # Broad leaf woodland - Poor condition
    45: 1, # Broad leaf woodland - Fair condition
    51: 1, # Broad leaf woodland - Good condition
           
    52: 1, # Coniferous woodland - Poor condition
    46: 1, # Coniferous woodland - Fair condition
    53: 1, # Coniferous woodland - Good condition

    73: 1, # Woods?grass combination (orchard or tree farm).- Poor condition
    74: 1, # Woods?grass combination (orchard or tree farm).  - Fair condition
    75: 1, # Woods?grass combination (orchard or tree farm).  - Good condition

    #ARABLE CODES
    47: 1, # Arable and horticulture - Good condition
    54: 1, # Arable and horticulture - Poor condition
    76: 1, # Fallow - Bare soil

    #Grassland CODES
    48: 1, # Improved grassland - Poor condition
    55: 1, # Improved grassland - Fair condition
    56: 1, # Improved grassland - Good condition

        #URBAN CODES
    57: 0, # Farmsteds - buildings, lanes, driveways and surrounding lots
    65: 0, # Commercial and buisness
    66: 0, # Industrial

    #OPEN PARKS / SPACES
    58: 1, # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Poor
    59: 1, # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Fair
    60: 1, # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Good
            
    #IMPERVIOUS AREAS
    61: 0, # Paved parking lots, roofs, driveways (Excl right of way)
    62: 0, # Paved streets and roads: open ditches (incl right of way)
    63: 0, # Gravel streets and roads (including right of way)
    64: 1, # Dirt streets and roads (including right of way)

    #RESIDENTIAL
    67: 0, # 1/8 acre or less (town houses) T
    68: 0, # 1/4 acre T
    69: 0, # 1/3 acre T
    70: 0, # 1/2 acre T
    71: 0, # 1 acre T
    72: 0, # 2 acres 

    }

# Values which should not have any soil for Combined land cover
COMBINE_SCS = {             
        
    #WOODLAND CODES
    50: 1, # Broad leaf woodland - Poor condition T
    1 : 1, # Broad leaf woodland - Fair condition T
    51: 1, # Broad leaf woodland - Good condition T
            
    52: 1, # Coniferous woodland - Poor condition T
    2: 1, # Coniferous woodland - Fair condition T
    53: 1, # Coniferous woodland - Good condition T

    73: 1, # Woods?grass combination (orchard or tree farm).- Poor condition T
    74: 1, # Woods?grass combination (orchard or tree farm).  - Fair condition T
    75: 1, # Woods?grass combination (orchard or tree farm).  - Good condition T

    #ARABLE CODES
    3: 1, # Arable and horticulture - Good condition T
    54: 1, # Arable and horticulture - Poor condition T
    76: 1, # Fallow - Bare soil T

    #Grassland CODES
    4: 1, # Improved grassland - Poor condition T
    55: 1, # Improved grassland - Fair condition T
    56: 1, # Improved grassland - Good condition T
    5: 1, # Rough grassland T
    6: 1, # Neutral grassland T
    7: 1, # Calcareous grassland T
    8: 1, # Acid grassland (and bracken) T

    #MIS CODES
    10: 1, # Heather T
    11: 1, # Heather grassland T
    12: 0, # Bog (using bespoke value) T
    14: 0, # Inland rock (considered to be an impervious value) T
    15: 0, # Saltwater T
    16: 0, # Freshwater T


    #URBAN CODES
    57: 0, # Farmsteds - buildings, lanes, driveways and surrounding lots  T
    23: 0, # Suburban T
    22: 0, # Urban T
    65: 0, # Commercial and buisness T
    66: 0, # Industrial T

    #OPEN PARKS / SPACES
    58: 1, # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Poor T
    59: 1, # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Fair T
    60: 1, # Open spaces (lawns, parks, golfcourses, cemeteries etc) - Good T
            
    #IMPERVIOUS AREAS
    61: 0, # Paved parking lots, roofs, driveways (Excl right of way) T
    62: 0, # Paved streets and roads: open ditches (incl right of way) T
    63: 0, # Gravel streets and roads (including right of way) T
    64: 1, # Dirt streets and roads (including right of way) T

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
               
    # Mountain habitat
    13: 1, # Montane habitats used - fair brush for now. T

    # The unclassified
    24: 1, # Permanent Pasture on RDPE agri-environment scheme * T
    25: 1, # Permanet Pasture used for dehydrated fodder* T
    26: 1, # All other permanent pasture (including grazing woodland)* T
    27: 1, # Temporary grass * T
    28: 1, # temporary grass used for dehydrated fodder * T
    29: 1, # All other temporary grass * T
    30: 1, # All protien crops # out in 2011 - Removed * T
    31: 1, # Almonds T
    32: 1, # Hazelnuts or filberts T
    33: 1, # Walnuts T
    34: 1, # Pistachios T
    35: 1, # Flax T
    36: 1, # Hemp T
    37: 1, # Hops T
    38: 1, # Dehydrated fodder crops T
    39: 1, # Land under woodland grant scheme * T
    40: 1, # Forest/Woodland * T
    41: 1, # RDPE schemes woodland * T
    42: 1, # Forested land that was permanet pasture in 2003 * T
    43: 1, # Land managed as set aside - removed from the data * T
    44: 1, # Removed from the data * T
    45: 1, # Agricultural land not in production * T
    46: 1, # Crops * T
    47: 1, # Crops * T
    48: 1, # Permanent Fruit and Vegtables * T
    49: 1, # Agri-environment land that does not fit any other catagory - Removed * T

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