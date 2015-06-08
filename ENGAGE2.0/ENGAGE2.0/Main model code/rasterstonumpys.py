# Import statments
import arcpy
import csv
import numpy as np

# Simple function to convert rasters to numpys
def convert_raster_to_numpy(list_of_rasters):   
    list_of_numpy_arrays = []
    for raster in list_of_rasters:
        arcpy.AddMessage("Converting " + str(raster) + " raster to numpy array")
        numpy_raster = arcpy.RasterToNumPyArray(raster, '#', '#', '#', -9999)   
        list_of_numpy_arrays.append(numpy_raster)

    arcpy.AddMessage("-------------------------")          
    arcpy.AddMessage("Successfully converted rasters to numpy arrays")
    arcpy.AddMessage("-------------------------")

    return list_of_numpy_arrays

def convert_numpy_to_raster_dict(list_of_numpys, bottom_left_corner, cell_size, save_date):
    
    for name, numpy in list_of_numpys.iteritems():
        arcpy.AddMessage("Converting " + str(name) + " numpy array to raster")
        raster = arcpy.NumPyArrayToRaster(numpy, bottom_left_corner, cell_size, cell_size, -9999)
        raster.save(name + "_" + str(save_date))        
        del name, numpy, raster
        
    arcpy.AddMessage("-------------------------")
    arcpy.AddMessage("Successfully converted numpy arrays to rasters")
    arcpy.AddMessage("-------------------------")

def convert_numpy_to_raster_list(list_of_numpys, bottom_left_corner, cell_size, save_date):
    
    number = 1
    for name in list_of_numpys:

        arcpy.AddMessage("Converting numpy array to raster")
        raster = arcpy.NumPyArrayToRaster(name, bottom_left_corner, cell_size, cell_size, -9999)
        raster.save("testing" + str(number) + "_" + str(save_date))        
        del name, raster
        number += 1    
    arcpy.AddMessage("-------------------------")
    arcpy.AddMessage("Successfully converted numpy arrays to rasters")
    arcpy.AddMessage("-------------------------")

def convert_numpy_to_raster_single(numpy, output_type, bottom_left_corner, cell_size, save_date):
    arcpy.AddMessage("Converting " + str(output_type) + " numpy array to raster")
    raster = arcpy.NumPyArrayToRaster(numpy, bottom_left_corner, cell_size, cell_size, -9999)
    raster.save(output_type + "_" + str(save_date))        
    del raster
        
    arcpy.AddMessage("-------------------------")
    arcpy.AddMessage("Successfully converted numpy arrays to rasters")
    arcpy.AddMessage("-------------------------")

def save_discharge_or_sediment_csv(output_excel_discharge, output_excel_sediment):
    # Set up the discharge location which outputs the value at the bottom of the catchment every day.
    if output_excel_discharge and output_excel_discharge != "#":
        output_excel_discharge = output_excel_discharge + "/discharge.csv"
        daily_discharge =  open(output_excel_discharge, 'wb')
        discharge_spamwriter = csv.writer(daily_discharge, delimiter=',')
    else:
        discharge_spamwriter = "#"

    # Set up the save location for sediment leaving the bottom of the system
    if output_excel_sediment and output_excel_sediment != "#":
        output_excel_sediment = output_excel_sediment + "/discharge.csv"
        daily_sediment =  open(output_excel_sediment, 'wb')
        sediment_spamwriter = csv.writer(daily_sediment, delimiter=',')

    else:
        sediment_spamwriter = "#"

    return discharge_spamwriter, sediment_spamwriter

def output_discharge_csv(current_date, discharge_spamwriter, Q_max):
    if discharge_spamwriter and discharge_spamwriter != "#":
        discharge_spamwriter.writerow([current_date, Q_max])
        arcpy.AddMessage("Daily Discharge Written to CSV")

def output_sediment_csv(current_date, sediment_spamwriter, Sed_max):
    if sediment_spamwriter and sediment_spamwriter != "#":
        sediment_spamwriter.writerow([current_date, Sed_max])
        arcpy.AddMessage("Daily Discharge Written to CSV")