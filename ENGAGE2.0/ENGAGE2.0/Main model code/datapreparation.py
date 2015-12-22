###### MODEL LOOP DESCRIPTION #####
# The purpose of this file is to carry out all the data preparation prior to the model starting to operate

##### VARIABLES - used in this file #####
# numpy_array_location - this is the location on the computer where hard copies of the numpy arrays can be stored.

### MODEL INPUTS ###

# Import statements
import arcpy
import numpy as np
import datetime
import time
from itertools import izip

# Class to handle the cases where the data is not found
class DoesNotCompute(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def output_raster_types(output_surface_runoff, output_discharge, output_water_depth, output_spatial_precipitation
                        , output_sediment_depth, output_net_sediment_transport):
    # Create an output frequency dict of the different strings and print back the selections
    output_file_dict = {"Surface_runoff": output_surface_runoff, "Discharge": output_discharge, "Water_depth": output_water_depth, 
                        "Spatial_precipitation": output_spatial_precipitation, "Sediment_depth": output_sediment_depth, "Net_sediment": output_net_sediment_transport}

    for output, output_frequency in output_file_dict.iteritems():
        arcpy.AddMessage("You have selected " + str(output_frequency) + " for " + output)

    return output_file_dict


# Function to check if the data exists in the preprocessing geodatabase
def check_preprocessing_files():
    arcpy.AddMessage("-------------------------")
    try:
        # Check for elevation data
        if arcpy.Exists("MODEL_DTM"):
            DTM = "MODEL_DTM"

            if arcpy.Exists("MODEL_DTM_Channel_Burned"):
                DTM = "MODEL_DTM_Channel_Burned"
            arcpy.AddMessage("Elevation data detected")
                        
        else:
            # Raise a custom exception
            raise DoesNotCompute("Digital terrain model (DTM)")

        # Check and confirm the land cover file / type
        if arcpy.Exists("MODEL_Landcover_LCM"):            
            land_cover = "MODEL_Landcover_LCM"
            land_cover_type = 'LCM 2007'
            arcpy.AddMessage("LCM 2007 land cover data detected")
            
            if arcpy.Exists("MODEL_Landcover_LCM_Altered"):
                land_cover = "MODEL_Landcover_LCM_Altered"
                land_cover_type = 'LCM 2007'
                arcpy.AddMessage("Altered LCM land cover detected and selected")
                
        elif arcpy.Exists("MODEL_Landcover_CORINE"):
            land_cover = "MODEL_Landcover_CORINE"
            land_cover_type = 'CORINE 2006'
            arcpy.AddMessage("CORINE 2006 land cover data detected")
            
            if arcpy.Exists("MODEL_Landcover_CORINE_Altered"):
                land_cover = "MODEL_Landcover_CORINE_Altered"
                land_cover_type = 'CORINE 2006'
                arcpy.AddMessage("Altered CORINE land cover detected and selected")
                
        elif arcpy.Exists("MODEL_COMBINE_LC"):
            land_cover = "MODEL_COMBINE_LC"
            land_cover_type = 'COMBINE'
            arcpy.AddMessage("Natural England SPS and LCM 2007 combined land cover data detected")
            
            if arcpy.Exists("MODEL_COMBINE_LC_Altered"):
                land_cover = "MODEL_COMBINE_LC_Altered"
                land_cover_type = 'COMBINE'
                arcpy.AddMessage("Altered Natural England SPS and LCM 2007 land cover detected and selected")
                
        else:
            raise DoesNotCompute("land cover data")

        # Check and confirm the host soil file / type
        if arcpy.Exists("MODEL_Soil_HOST"):
            soil = "MODEL_Soil_HOST"
            soil_type = "HOST"
            arcpy.AddMessage("HOST soil data detected")
            
        elif arcpy.Exists("MODEL_Soil_FAO"):
            soil = "MODEL_Soil_FAO"
            soil_type = "FAO"
            arcpy.AddMessage("FAO soil data detected")
            
        else:
            raise DoesNotCompute("soil data")

        # Check and confirm the grainsize proportions    
        if arcpy.Exists("MODEL_GS1"):
            GS_1_P = "MODEL_GS1"
            
        if arcpy.Exists("MODEL_GS2"):
            GS_2_P = "MODEL_GS2"

        if arcpy.Exists("MODEL_GS3"):
            GS_3_P = "MODEL_GS3"

        if arcpy.Exists("MODEL_GS4"):
            GS_4_P = "MODEL_GS4"

        if arcpy.Exists("MODEL_GS5"):
            GS_5_P = "MODEL_GS5"

        if arcpy.Exists("MODEL_GS6"):
            GS_6_P = "MODEL_GS6"

        if arcpy.Exists("MODEL_GS7"):
            GS_7_P = "MODEL_GS7"
            arcpy.AddMessage("Grain size proportions data detected")
                        
        else:
            raise DoesNotCompute("grain size proportions")  

        if arcpy.Exists("MODEL_ASD_soil_depth"):
            ASD_soil_depth = "MODEL_ASD_soil_depth"
            arcpy.AddMessage("Advanced superficial deposit soil depth data detected")  
                       
        else:
            ASD_soil_depth = '#'
            arcpy.AddMessage("Advanced superficial deposit data not detected")  

        if arcpy.Exists("MODEL_BGS_SOIL_DEPTH"):
            BGS_soil_depth = "MODEL_BGS_SOIL_DEPTH"
            arcpy.AddMessage("BGS soil depth data detected")  
                       
        else:
            BGS_soil_depth = '#'
            arcpy.AddMessage("BGS soil depth data not detected") 
            
        if arcpy.Exists("MODEL_general_soil_depth"):
            general_soil_depth = "MODEL_general_soil_depth"
            arcpy.AddMessage("Generalised soil depth data detected")  
                       
        else:
            general_soil_depth = '#'
            arcpy.AddMessage("General data not detected")    

        if arcpy.Exists("MODEL_river_catchment"):
            river_catchment = "MODEL_river_catchment"
            arcpy.AddMessage("River catchment detected")  
                      
        else:
            raise DoesNotCompute("River catchment")

        if arcpy.Exists("MODEL_orgC"):
            orgC = "MODEL_orgC"
            arcpy.AddMessage("orgC detected") 

        else:
            orgC = '#'
            calculate_sediment_erosion_hillslope = False
            arcpy.AddMessage("orgC not detected therefore hillslope erosion cannot be calculated") 

        arcpy.AddMessage("-------------------------")  
    except DoesNotCompute as error:        
        arcpy.AddError("Model data: " + str(error.value) + " from the pre-processing script could not be found at the location you specified") 
           
        
    return DTM, land_cover, land_cover_type, soil, soil_type, GS_1_P, GS_2_P, GS_3_P, GS_4_P, GS_5_P, GS_6_P, GS_7_P, ASD_soil_depth, BGS_soil_depth, general_soil_depth, river_catchment, orgC

# Function to convert the date into a day of the year
def convert_date_day_year(current_date):
    month_and_day = datetime.datetime.strptime(current_date, '%d/%m/%Y')
    day = int(month_and_day.strftime('%j'))
    return day

# Function to calculate the locations that have an active layer
def calculate_active_layer(river_soil_depth, cell_size):
    
    # Locate areas which need an active layer (everywhere else should be 0.0)
    active_layer = np.zeros_like(river_soil_depth, dtype = float)

    B = (river_soil_depth >= 0.2)
    active_layer[B] = 0.2
    
    B = ~B & (river_soil_depth > 0)
    active_layer[B] = river_soil_depth[B]
    
    # Calculate the remaining soil depth at that location
    inactive_layer = river_soil_depth - active_layer

    # Convert active layer to volume:
    active_layer = active_layer * cell_size * cell_size

    # Convert active layer to volume:
    inactive_layer = inactive_layer * cell_size * cell_size 

    # Covnert NoData to -9999
    inactive_layer[river_soil_depth == -9999] = -9999
    active_layer[river_soil_depth == -9999] = -9999

    arcpy.AddMessage("Calculated active and inactive layer volumes in the river channel") 
    arcpy.AddMessage("-------------------------") 

    return active_layer, inactive_layer

# Function to calculation the default grain size volumes in m2
def get_grain_volumes(GS_P_list, active_layer, inactive_layer):
        
    # List to store grain size volumes
    active_layer_GS_volumes =[]
    inactive_layer_GS_volumes =[]

    # Iterate through the list of grain size volumes for the active layer
    for proportion in GS_P_list:
        volume = np.zeros_like(proportion, dtype = float)
        volume = active_layer * proportion
        volume[active_layer == -9999] = -9999
        active_layer_GS_volumes.append(volume)

    # Iterate through the list of grain size volumes for the inactive layer
    for proportion in GS_P_list:
        volume = np.zeros_like(proportion, dtype = float)
        volume = inactive_layer * proportion
        volume[active_layer == -9999] = -9999
        inactive_layer_GS_volumes.append(volume)

    arcpy.AddMessage("Calculated starting volumes for each of the 7 grain sizes in the active and inactive layers") 
    arcpy.AddMessage("-------------------------") 
    return active_layer_GS_volumes, inactive_layer_GS_volumes

# Function to the average number of days rainfall per year based on the input textfile
def average_days_rainfall(model_start_date, precipitation_textfile):
    
    
    total_number_days = 0
    month_day = 0
    total_day_precip = 0
    total_day_precip_month = 0
    total_precip_month = 0.0

    # List to store the monthly precipitation values and average daily month values
    total_day_month_precip = []
    total_avg_month_precip = []

    # Open the precipitation file
    precip_read = open(precipitation_textfile)

    # Set the starting date
    current_date = datetime.datetime.strptime(model_start_date, '%d/%m/%Y')

    for precip in precip_read:
        month_day += 1
        tomorrow = current_date + datetime.timedelta(days=1)
        tomorrow_day = int(tomorrow.strftime('%d'))

        if precip == '.' or precip == '---':
            precip = 0
        
        try:
     
            if float(precip) > 0:
                total_day_precip += 1
                total_day_precip_month += 1
                total_precip_month += float(precip)

        except ValueError:
            precip = 0         
        
        if tomorrow_day == 1:
            # Used to calculate the number of days precipitation in a month
            total_day_month_precip.append(total_day_precip_month)

            # Used to calculate the average precipitation in a month
            avg_day_month_precip = total_precip_month / month_day
            total_avg_month_precip.append(avg_day_month_precip)

            total_day_precip_month = 0
            total_precip_month = 0 
            month_day = 0

        if total_number_days == 1456 or total_number_days == 2913 or total_number_days == 4370 or total_number_days == 5827:
            total_number_days += 1

        # Increment the date and day by 1
        total_number_days += 1        
        current_date = current_date + datetime.timedelta(days=1)
    
    years_of_sim = total_number_days / 364.25
    day_pcp_yr = total_day_precip / years_of_sim
              
    arcpy.AddMessage("Average number of days precipitation per year is " + str(day_pcp_yr))
    arcpy.AddMessage("-------------------------")  
    precip_read.close()

    return day_pcp_yr, years_of_sim, total_day_month_precip, total_avg_month_precip

# Function to create and store the temporary file locations on the harddrive of the computer
def temporary_file_locations(numpy_array_location, GS_P_list, active_layer_GS_volumes, inactive_layer_GS_volumes):

    # Create temporary file location for grain size proportions in the active layer
    AL_GS_1_P_temp = numpy_array_location + '\AL_GS_1_P_temp.npy'
    AL_GS_2_P_temp = numpy_array_location + '\AL_GS_2_P_temp.npy'
    AL_GS_3_P_temp = numpy_array_location + '\AL_GS_3_P_temp.npy'
    AL_GS_4_P_temp = numpy_array_location + '\AL_GS_4_P_temp.npy'
    AL_GS_5_P_temp = numpy_array_location + '\AL_GS_5_P_temp.npy'
    AL_GS_6_P_temp = numpy_array_location + '\AL_GS_6_P_temp.npy'
    AL_GS_7_P_temp = numpy_array_location + '\AL_GS_7_P_temp.npy'
    
    active_layer_GS_P_temp = [AL_GS_1_P_temp, AL_GS_2_P_temp, AL_GS_3_P_temp, AL_GS_4_P_temp, AL_GS_5_P_temp, AL_GS_6_P_temp, AL_GS_7_P_temp]

    # Create temporary file location for grain size proportions in the inactive layer
    IL_GS_1_P_temp = numpy_array_location + '\IL_GS_1_P_temp.npy'
    IL_GS_2_P_temp = numpy_array_location + '\IL_GS_2_P_temp.npy'
    IL_GS_3_P_temp = numpy_array_location + '\IL_GS_3_P_temp.npy'
    IL_GS_4_P_temp = numpy_array_location + '\IL_GS_4_P_temp.npy'
    IL_GS_5_P_temp = numpy_array_location + '\IL_GS_5_P_temp.npy'
    IL_GS_6_P_temp = numpy_array_location + '\IL_GS_6_P_temp.npy'
    IL_GS_7_P_temp = numpy_array_location + '\IL_GS_7_P_temp.npy'

    inactive_layer_GS_P_temp = [IL_GS_1_P_temp, IL_GS_2_P_temp, IL_GS_3_P_temp, IL_GS_4_P_temp, IL_GS_5_P_temp, IL_GS_6_P_temp, IL_GS_7_P_temp]

    # Create temporary file location for grain size volumes in the active layer
    AL_GS_1_V_temp = numpy_array_location + '\AL_GS_1_V_temp.npy'
    AL_GS_2_V_temp = numpy_array_location + '\AL_GS_2_V_temp.npy'
    AL_GS_3_V_temp = numpy_array_location + '\AL_GS_3_V_temp.npy'
    AL_GS_4_V_temp = numpy_array_location + '\AL_GS_4_V_temp.npy'
    AL_GS_5_V_temp = numpy_array_location + '\AL_GS_5_V_temp.npy'
    AL_GS_6_V_temp = numpy_array_location + '\AL_GS_6_V_temp.npy'
    AL_GS_7_V_temp = numpy_array_location + '\AL_GS_7_V_temp.npy'
    
    active_layer_GS_V_temp = [AL_GS_1_V_temp, AL_GS_2_V_temp, AL_GS_3_V_temp, AL_GS_4_V_temp, AL_GS_5_V_temp, AL_GS_6_V_temp, AL_GS_7_V_temp]

    # Create temporary file location for grain size volumes in the inactive layer
    IL_GS_1_V_temp = numpy_array_location + '\IL_GS_1_V_temp.npy'
    IL_GS_2_V_temp = numpy_array_location + '\IL_GS_2_V_temp.npy'
    IL_GS_3_V_temp = numpy_array_location + '\IL_GS_3_V_temp.npy'
    IL_GS_4_V_temp = numpy_array_location + '\IL_GS_4_V_temp.npy'
    IL_GS_5_V_temp = numpy_array_location + '\IL_GS_5_V_temp.npy'
    IL_GS_6_V_temp = numpy_array_location + '\IL_GS_6_V_temp.npy'
    IL_GS_7_V_temp = numpy_array_location + '\IL_GS_7_V_temp.npy'

    inactive_layer_GS_V_temp = [IL_GS_1_V_temp, IL_GS_2_V_temp, IL_GS_3_V_temp, IL_GS_4_V_temp, IL_GS_5_V_temp, IL_GS_6_V_temp, IL_GS_7_V_temp]

    # Save the proportion arrays to disk
    np.save(active_layer_GS_P_temp[0], GS_P_list[0])
    np.save(active_layer_GS_P_temp[1], GS_P_list[1])
    np.save(active_layer_GS_P_temp[2], GS_P_list[2])
    np.save(active_layer_GS_P_temp[3], GS_P_list[3])
    np.save(active_layer_GS_P_temp[4], GS_P_list[4])
    np.save(active_layer_GS_P_temp[5], GS_P_list[5])
    np.save(active_layer_GS_P_temp[6], GS_P_list[6])
    arcpy.AddMessage("Saved proportions in active layer to disk")

    # Save the remaining soil proportion arrays to disk
    np.save(inactive_layer_GS_P_temp[0], GS_P_list[0])
    np.save(inactive_layer_GS_P_temp[1], GS_P_list[1])
    np.save(inactive_layer_GS_P_temp[2], GS_P_list[2])
    np.save(inactive_layer_GS_P_temp[3], GS_P_list[3])
    np.save(inactive_layer_GS_P_temp[4], GS_P_list[4])
    np.save(inactive_layer_GS_P_temp[5], GS_P_list[5])
    np.save(inactive_layer_GS_P_temp[6], GS_P_list[6])
    arcpy.AddMessage("Saved proportions in inactive layer to disk")

    # Save the grain volumes arrays to disk
    np.save(active_layer_GS_V_temp[0], active_layer_GS_volumes[0])
    np.save(active_layer_GS_V_temp[1], active_layer_GS_volumes[1])
    np.save(active_layer_GS_V_temp[2], active_layer_GS_volumes[2])
    np.save(active_layer_GS_V_temp[3], active_layer_GS_volumes[3])
    np.save(active_layer_GS_V_temp[4], active_layer_GS_volumes[4])
    np.save(active_layer_GS_V_temp[5], active_layer_GS_volumes[5])
    np.save(active_layer_GS_V_temp[6], active_layer_GS_volumes[6])
    arcpy.AddMessage("Saved active layer volumes to disk")

    # Save the inactive grain volumes arrays to disk
    np.save(inactive_layer_GS_V_temp[0], inactive_layer_GS_volumes[0])
    np.save(inactive_layer_GS_V_temp[1], inactive_layer_GS_volumes[1])
    np.save(inactive_layer_GS_V_temp[2], inactive_layer_GS_volumes[2])
    np.save(inactive_layer_GS_V_temp[3], inactive_layer_GS_volumes[3])
    np.save(inactive_layer_GS_V_temp[4], inactive_layer_GS_volumes[4])
    np.save(inactive_layer_GS_V_temp[5], inactive_layer_GS_volumes[5])
    np.save(inactive_layer_GS_V_temp[6], inactive_layer_GS_volumes[6])
    arcpy.AddMessage("Saved inactive layer volumes to disk")
    arcpy.AddMessage("-------------------------") 

    return active_layer_GS_P_temp, active_layer_GS_V_temp, inactive_layer_GS_P_temp, inactive_layer_GS_V_temp

# Function to check whether or not baseflow has been provided and split the incoming textfile if required
def combined_precipitation(numpy_array_location, precipitation_textfile, baseflow_textfile):
    # Check if the user has provided a baseflow textfile and if so combine the data into a new file
    if baseflow_textfile and baseflow_textfile != '#':
        
        arcpy.AddMessage("Baseflow data detected")
        baseflow_read = open(baseflow_textfile)
        precipitation_read = open(precipitation_textfile)

        combined_precipitation_read = open(numpy_array_location + "\combined_precipitation.txt", 'w')

        for precipitation, baseflow in izip(precipitation_read, baseflow_read):
            precipitation = precipitation.strip()
            baseflow = baseflow.strip()
            baseflow = baseflow[9:22]
            combined_precipitation_read.write(precipitation + " " + baseflow + "\n")

        arcpy.AddMessage("Combined baseflow and precipitation")
        arcpy.AddMessage("-------------------------")    
               
        # Close the textfiles
        baseflow_read.close()
        precipitation_read.close()
        combined_precipitation_read.close()
        baseflow_provided = True
        precipitation_textfile = numpy_array_location + "\combined_precipitation.txt"

    else:
        arcpy.AddMessage("No baseflow data detected")
        baseflow_provided = False
        precipitation_textfile = precipitation_textfile

    return precipitation_textfile, baseflow_provided

# Function to check incoming string boolean created by ArcGIS
def convert_to_boolean(trueorfalse):

    if trueorfalse == 'true' or trueorfalse == 'True':
        trueorfalse = True
        arcpy.AddMessage("converted to True boolean")

    elif trueorfalse == 'false' or trueorfalse == 'False':
        trueorfalse = False
        arcpy.AddMessage("converted to False boolean")
    else:
        trueorfalse = trueorfalse
        arcpy.AddMessage("was already a boolean")

    return trueorfalse


# Function to create and store the temporary file locations on the harddrive of the computer
def temporary_average_numpys(numpy_array_location):
    # Create temporary file location for grain size proportions in the active layer
    Q_surf_temp = numpy_array_location + '\Q_surf_temp.npy'
    Discharge_temp = numpy_array_location + '\Discharge_temp.npy'
    Water_depth_temp = numpy_array_location + '\Water_depth_temp.npy'
    Spatial_precipiation_temp = numpy_array_location + '\Spatial_precipiation_temp.npy'
    Sediment_depth_temp = numpy_array_location + '\Sediment_depth_temp.npy'
    Net_sediment_temp = numpy_array_location + '\Net_sediment_temp.npy'
    
    output_averages_temp = [Q_surf_temp, Discharge_temp, Water_depth_temp, Spatial_precipiation_temp, Sediment_depth_temp, Net_sediment_temp]

    return output_averages_temp
                        