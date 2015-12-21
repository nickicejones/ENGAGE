# Required modules
import arcpy
import os
import subprocess  

#Input discharge guage file at the bottom of the catchment
input_gauge_record = arcpy.GetParameterAsText(0)

# The baseflow index to compare with
baseflow_index = float(arcpy.GetParameterAsText(1)) # set the default as 0 if the user does not input a value pass one is used in the model

out_gauge_record = "gauge.prn"

# Open the dsicharge guage file and the output file
discharge_read = open(input_gauge_record, 'r')
output_read = open(out_gauge_record, 'w')

# Iterate through the discharge file and convert the data into the required format
for line in discharge_read:
    split = line.split()
    date = str(split[0])
    discharge = str(split[1])
    date_split = date.split("/")
    day = str(date_split[0])
    month = str(date_split[1])
    year = str(date_split[2])
    output_read.write(year + month + day + " ")
    output_read.write(discharge)
    output_read.write('\n')

arcpy.AddMessage("Corrected date for use in baseflow calculation")

# Close opened files
discharge_read.close()
output_read.close()

# Run the calculations of the baseflow calculations
args = "bflow.exe"
subprocess.call(args, stdin=None, stdout=None, stderr=None, shell=False)

# Open the baseflow data
baseflow_stats = "baseflow.DAT"

baseflow_stats_read = open(baseflow_stats)

bfi_dict = {}

for line in baseflow_stats_read.readlines()[3:]:
    split_stats = line.split()
    pass_1_bfi = float(split_stats[1])
    arcpy.AddMessage("Pass 1 bfi is " + str(pass_1_bfi))
    pass_2_bfi = float(split_stats[2])
    arcpy.AddMessage( "Pass 2 bfi is " + str(pass_2_bfi))
    pass_3_bfi = float(split_stats[3])
    arcpy.AddMessage( "Pass 3 bfi is " + str(pass_3_bfi))
    bfi_dict = {pass_1_bfi: "pass_1_bfi", pass_2_bfi: "pass_2_bfi", pass_3_bfi: "pass_3_bfi"}

if baseflow_index > 0:
    closest_pass = min(bfi_dict, key=lambda x:abs(x-baseflow_index))
    arcpy.AddMessage( "The closest pass is " + str(closest_pass))

    for pass_value, pass_str in bfi_dict.iteritems():
        if pass_value == closest_pass:
            use_pass = pass_str
            arcpy.AddMessage(str(use_pass) + " selected")

else:
    use_pass = "pass_1_bfi"
    arcpy.AddMessage(str(use_pass) + " selected")

# Open the baseflow file
baseflow = "baseflow.out"
baseflow_read = open(baseflow, 'r')
first_loop = 'true'

# Create a textfile to store the output baseflow values
output_baseflow = open("baseflow_output.txt", 'w')

# A dict that multiples the values in the baseflow output based on the E values
dict_of_multiplication = {"E-07": 0.00000001, "E-06": 0.0000001, "E-05": 0.000001, "E-04": 0.00001, "E-03": 0.0001, "E-02": 0.001, "E-01": 0.1, "E+00": 1, "E+01": 10, "E+02": 100, "E+03": 1000, "E+04": 10000, "E+05": 100000, "E+06": 1000000, "E+07": 10000000}

for baseflow in baseflow_read.readlines()[1:]:
    
    if first_loop == 'true':
        date = baseflow[:9]
        baseflow = "0.0"
        output_baseflow.write(date)
        output_baseflow.write(baseflow)
        output_baseflow.write('\n')

        arcpy.AddMessage("First loop is true")

    else: 
        #Slice the lines in the file to get the different values for the algorithm to sort out       
        date = baseflow[:9]

        record_flow = baseflow[9:22]
        
        pass_1_full = baseflow[22:34]        
        pass_2_full = baseflow[35:47]
        pass_3_full = baseflow[48:60]
        pass_1_first = float(pass_1_full[0:-4])
        pass_2_first = float(pass_2_full[0:-4])
        pass_3_first = float(pass_3_full[0:-4])
        pass_1_last = pass_1_full[-4:]
        pass_2_last = pass_2_full[-4:]
        pass_3_last = pass_3_full[-4:]

        output_baseflow.write(date)
        if use_pass == 'pass_1_bfi':           
            corrected_discharge = str(pass_1_first * dict_of_multiplication[pass_1_last])
            output_baseflow.write(corrected_discharge)
            output_baseflow.write('\n')

        if use_pass == 'pass_2_bfi':            
            corrected_discharge = str(pass_2_first * dict_of_multiplication[pass_2_last])
            output_baseflow.write(corrected_discharge)
            output_baseflow.write('\n')

        if use_pass == 'pass_3_bfi':
            corrected_discharge = str(pass_3_first * dict_of_multiplication[pass_3_last])
            output_baseflow.write(corrected_discharge)
            output_baseflow.write('\n')

    first_loop = 'false'

# Close the files as they are no longer needed
baseflow_read.close()
output_baseflow.close()