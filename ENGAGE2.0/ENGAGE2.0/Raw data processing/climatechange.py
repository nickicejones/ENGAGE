# Required modules
import arcpy

precipitation_textfile = arcpy.GetParameterAsText(0)

scaling_percent = float(arcpy.GetParameterAsText(1)) # This should be a percentage  

scale_direction = arcpy.GetParameterAsText(2) # increase or decrease precipitation

output_precipitation = arcpy.GetParameterAsText(3) 

# Calculate whether or not the file needs to be scaled up or down
scale_factor = scaling_percent / 100

arcpy.AddMessage("Precipitation will be " + str(scale_direction) + "d by " + str(scaling_percent ) + "%")

# Open the precipitation file
precipitation_read = open(precipitation_textfile, 'r')

# Open the output file ready to write the file 
output_precipitation_read = open(output_precipitation, 'w')

# Iterate through the precipitation file and create a changed value based on user input.
for precipitation in precipitation_read:
    precipitation = float(precipitation)
    if scale_direction == 'increase':
        new_precipitation = precipitation + (precipitation * scale_factor)       
        output_precipitation_read.write(str(new_precipitation))
        output_precipitation_read.write('\n')
      
    elif scale_direction == 'decrease':
        new_precipitation = precipitation - (precipitation * scale_factor)        
        output_precipitation_read.write(str(new_precipitation))
        output_precipitation_read.write('\n')

arcpy.AddMessage("Precipitation succesfully altered")
      
precipitation_read.close()
output_precipitation_read.close()