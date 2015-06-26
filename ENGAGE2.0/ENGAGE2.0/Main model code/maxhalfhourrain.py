###### MODEL LOOP DESCRIPTION #####
# The purpose of this file is to calculate monthly maximum half-hour rainfall events

##### VARIABLES - used in this file #####

### MODEL INPUTS ###
# precipitation_textfile - textfile containing hourly precipitation

# Import statements
import datetime

# Function to convert string to float
def num(s):
    try:
        return float(s)
    except ValueError:
        s = 0.0
        return s

def max_30min_rainfall(precipitation_hour_textfile, model_start_date):

   

    # Starting variables
    hour_counter = 0
    max_rainfall = 0.0
    max_30min_rainfall_list = []
    
    # Set the starting date
    current_date = datetime.datetime.strptime(model_start_date, '%d/%m/%Y')

    # Open the precipitation file
    precip_read = open(precipitation_hour_textfile)

    for precip in precip_read:
        hour_counter += 1
        tomorrow = current_date + datetime.timedelta(days=1)
        tomorrow_day = int(tomorrow.strftime('%d'))
        # As the value is hourly divide the value by 2 to get the 30 minute value
        
        precip = num(precip)
        
        # Convert to hour if there has been some rainfall
        if precip > 0:
            precip /= 2

        # If the value is greater than the previous value then it replaces the value
        if precip > max_rainfall and precip < 80.0:
            max_rainfall = precip

        # If it is the end of the month add the maximum value to the array!
        if tomorrow_day == 1 and hour_counter == 24:
            max_30min_rainfall_list.append(max_rainfall)
            max_rainfall = 0

        if hour_counter == 24:
            current_date = current_date + datetime.timedelta(days=1)
            hour_counter = 0
               
    precip_read.close()

    return max_30min_rainfall_list






