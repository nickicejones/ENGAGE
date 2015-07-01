###### MODEL LOOP DESCRIPTION #####
# The purpose of this file is to convert an hourly discharge file into a daily preciptation file.
##### VARIABLES - used in this file #####

#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import numpy as np
import arcpy

# Check if the value in the precipiation file can be converted into a value for use in the model or wether there is an error
def num(s):
    try:
        return float(s)
    except ValueError:
        s = 0.0
        return s


# Function to convert hourly to daily precipitation 
def convert_precipitation(precipitation_hour_textfile):
    
    # Name of the daily textfile
    precipitation_textfile = "daily_precipitation.txt"

    # Open the files ready for writing 
    precipitation_hourly_read = open(precipitation_hour_textfile)
    precipitation_daily_read = open(precipitation_textfile, 'w')

    hour_counter = 0
    day_precipitation_total = 0.0

    for precipitation in precipitation_hourly_read:
        precipitation = num(precipitation)
        day_precipitation_total += precipitation

        hour_counter += 1

        if hour_counter == 24: 
            day_precipitation_total = str(day_precipitation_total)           
            precipitation_daily_read.write(day_precipitation_total)
            precipitation_daily_read.write('\n')
            hour_counter = 0
            day_precipitation_total = 0.0

    # Close the opened files
    precipitation_daily_read.close()
    precipitation_hourly_read.close()

    return precipitation_textfile