#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import arcpy
import csv
import datetime
import numpy as np
from itertools import izip

# Simple function to convert rasters to numpys
def convert_raster_to_numpy(list_of_rasters):   
    list_of_numpy_arrays = []
    for raster in list_of_rasters:
        if raster and raster != '#':
            arcpy.AddMessage("Converting " + str(raster) + " raster to numpy array")
            numpy_raster = arcpy.RasterToNumPyArray(raster, '#', '#', '#', -9999)   
            list_of_numpy_arrays.append(numpy_raster)
        else:
            list_of_numpy_arrays.append(raster)

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

        
# Function to check which outputs are required from the model
def raster_outputs(week_day, month_day, year_day, current_date, first_loop, output_file_dict, output_format, output_averages_temp,
                   bottom_left_corner, cell_size, Q_surf_np, Q_dis, depth_recking, precipitation, sediment_depth, net_sediment):

    # Create a format which says what todays date is
    daily_save_date = str(current_date.strftime('%d_%m_%Y'))
    monthly_save_date = str(current_date.strftime('%m_%Y'))  
    year_save_date = str(current_date.strftime('%Y')) 
    tomorrow = current_date + datetime.timedelta(days=1)
    tomorrow_day = int(tomorrow.strftime('%d'))
    tomorrow_month = int(tomorrow.strftime('%m'))

    # Check if empty arrays need to be created to store averages or totals this is only carried out on the first loop
    if first_loop == True:
        arcpy.AddMessage("First day of operation checking average output rasters")
        for output_type, output_frequency in output_file_dict.iteritems():
            
            if str(output_frequency) != 'No output' and str(output_frequency) != 'Daily':                       
                if output_type == "Surface_runoff": 
                    Q_surf_avg = np.zeros_like(Q_surf_np)
                    np.save(output_averages_temp[0], Q_surf_avg)
                    arcpy.AddMessage(output_type + " raster created")
                if output_type == "Discharge": 
                    Q_dis_avg = np.zeros_like(Q_surf_np)
                    np.save(output_averages_temp[1], Q_dis_avg)
                    arcpy.AddMessage(output_type + " raster created")
                if output_type == "Water_depth": 
                    depth_avg = np.zeros_like(Q_surf_np)
                    np.save(output_averages_temp[2], depth_avg)
                    arcpy.AddMessage(output_type + " raster created")
                if output_type == "Spatial_precipitation": 
                    precipitation_avg = np.zeros_like(Q_surf_np)
                    np.save(output_averages_temp[3], precipitation_avg)
                    arcpy.AddMessage(output_type + " raster created")
                if output_type == "Sediment_depth": 
                    sed_depth_avg = np.zeros_like(Q_surf_np)
                    np.save(output_averages_temp[4], sed_depth_avg)
                    arcpy.AddMessage(output_type + " raster created")
                if output_type ==  "Net_sediment": 
                    sed_erosion_deposition_avg = np.zeros_like(Q_surf_np)
                    np.save(output_averages_temp[5], sed_erosion_deposition_avg)
                    arcpy.AddMessage(output_type + " raster created")

    # Load the average arrays if required.                    
    if first_loop == False:
        for output_type, output_frequency in output_file_dict.iteritems():
            if str(output_frequency) != 'No output' and str(output_frequency) != 'Daily':
                if output_type == "Surface_runoff":  
                    Q_surf_avg = np.load(output_averages_temp[0])
                if output_type == "Discharge": 
                    Q_dis_avg = np.load(output_averages_temp[1])
                if output_type == "Water_depth": 
                    depth_avg = np.load(output_averages_temp[2])
                if output_type == "Spatial_precipitation": 
                    precipitation_avg = np.load(output_averages_temp[3])
                if output_type == "Sediment_depth":                   
                    sed_depth_avg = np.load(output_averages_temp[4])
                if output_type ==  "Net_sediment": 
                    sed_erosion_deposition_avg = np.load(output_averages_temp[5])


    # Add one onto the weekly/monthly/yearly day counter
    week_day = week_day + 1
    month_day = month_day + 1
    year_day = year_day + 1
        
    for output_type, output_frequency in output_file_dict.iteritems(): 
        
        ### What to do if the output is daily ###          
        if output_frequency == 'Daily':
            if output_type == "Surface_runoff": 
                convert_numpy_to_raster_single(Q_surf_np, output_type, bottom_left_corner, cell_size, daily_save_date)
            if output_type == "Discharge": 
                convert_numpy_to_raster_single(Q_dis, output_type, bottom_left_corner, cell_size, daily_save_date)
            if output_type == "Water_depth": 
                convert_numpy_to_raster_single(depth_recking, output_type, bottom_left_corner, cell_size, daily_save_date)
            if output_type == "Spatial_precipitation": 
                convert_numpy_to_raster_single(precipitation, output_type, bottom_left_corner, cell_size, daily_save_date)
            if output_type == "Sediment_depth": 
                convert_numpy_to_raster_single(Q_surf, output_type, bottom_left_corner, cell_size, daily_save_date) # Need to change output
            if output_type ==  "Net_sediment": 
                convert_numpy_to_raster_single(Q_surf, output_type, bottom_left_corner, cell_size, daily_save_date) # Need to change output

        ### What happens if the output is weekly ###
        if output_frequency == 'Weekly':                   
            if output_type == "Surface_runoff":                
                arcpy.AddMessage("Surface_runoff added to weekly average")
                Q_surf_avg = Q_surf_avg + Q_surf_np
                

            if output_type == "Discharge":
                arcpy.AddMessage("Discharge added to weekly average")
                Q_dis_avg = Q_dis_avg + Q_dis

            if output_type == "Water_depth":
                arcpy.AddMessage("Water depth added to weekly average")
                depth_avg = depth_avg + depth_recking

            if output_type == "Spatial_precipitation":
                arcpy.AddMessage("Spatial precipitation added to weekly average")
                precipitation_avg = precipitation_avg + precipitation

            if output_type == "Sediment_depth":
                arcpy.AddMessage("Sediment depth added to weekly average")
                sed_depth_avg = sed_depth_avg + Q_surf # need to change Q_surf

            if output_type == "Net_sediment":
                arcpy.AddMessage("Net sediment added to weekly average")
                sed_erosion_deposition_avg = sed_erosion_deposition_avg + Q_surf # need to change Q_surf

            if week_day == 7:
                if output_format == 'Daily average':
                    arcpy.AddMessage("Weekly average selected")
                    if output_type == "Surface_runoff": 
                        arcpy.AddMessage("Saving weekly runoff average")
                        Q_surf_avg = Q_surf_avg / 7
                        Q_surf_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        Q_surf_avg = np.zeros_like(Q_surf_avg)

                    if output_type == "Discharge": 
                        arcpy.AddMessage("Saving weekly discharge average")
                        Q_dis_avg = Q_dis_avg / 7
                        Q_dis_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                    if output_type == "Water_depth": 
                        arcpy.AddMessage("Saving weekly depth average")
                        depth_avg = depth_avg / 7
                        depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        depth_avg = np.zeros_like(depth_avg)

                    if output_type == "Spatial_precipitation": 
                        arcpy.AddMessage("Saving weekly spatial precipitation average")
                        precipitation_avg = precipitation_avg / 7
                        precipitation_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        precipitation_avg = np.zeros_like(precipitation_avg)

                    if output_type == "Sediment_depth": 
                        arcpy.AddMessage("Saving weekly sediment depth average")
                        sed_depth_avg = sed_depth_avg / 7
                        sed_depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        sed_depth_avg = np.zeros_like(sed_depth_avg)

                    if output_type ==  "Net_sediment": 
                        arcpy.AddMessage("Saving weekly sediment eroision/deposition average")
                        sed_erosion_deposition_avg = sed_erosion_deposition_avg / 7
                        sed_erosion_deposition_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)

                elif output_format == 'Total':
                    arcpy.AddMessage("Weekly total selected")
                    if output_type == "Surface_runoff": 
                        arcpy.AddMessage("Saving weekly Surface_runoff total")
                        Q_surf_avg = Q_surf_avg
                        Q_surf_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        Q_surf_avg = np.zeros_like(Q_surf_avg)

                    if output_type == "Discharge": 
                        arcpy.AddMessage("Saving weekly discharge total")
                        Q_dis_avg = Q_dis_avg
                        Q_dis_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                    if output_type == "Water_depth": 
                        arcpy.AddMessage("Saving weekly depth total")
                        depth_avg = depth_avg
                        depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        depth_avg = np.zeros_like(depth_avg)

                    if output_type == "Spatial_precipitation": 
                        arcpy.AddMessage("Saving weekly spatial precipitation total")
                        precipitation_avg = precipitation_avg
                        precipitation_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        precipitation_avg = np.zeros_like(precipitation_avg)

                    if output_type == "Sediment_depth": 
                        arcpy.AddMessage("Saving weekly sediment depth total")
                        sed_depth_avg = sed_depth_avg
                        sed_depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        sed_depth_avg = np.zeros_like(sed_depth_avg)

                    if output_type ==  "Net_sediment": 
                        arcpy.AddMessage("Saving weekly sediment eroision/deposition total")
                        sed_erosion_deposition_avg = sed_erosion_deposition_avg
                        sed_erosion_deposition_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, daily_save_date)
                        sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)


        # What happens if the output is monthly
        if output_frequency == 'Monthly':
            arcpy.AddMessage("Tomorrow will be day " + str(tomorrow_day))                   
            if output_type == "Surface_runoff":
                arcpy.AddMessage("Surface_runoff added to monthly average")
                Q_surf_avg = Q_surf_avg + Q_surf_np

            if output_type == "Discharge":
                arcpy.AddMessage("Discharge added to monthly average")
                Q_dis_avg = Q_dis_avg + Q_dis

            if output_type == "Water_depth":
                arcpy.AddMessage("Water depth added to monthly average")
                depth_avg = depth_avg + depth_recking

            if output_type == "Spatial_precipitation":
                arcpy.AddMessage("Spatial precipitation added to monthly average")
                precipitation_avg = precipitation_avg + precipitation

            if output_type == "Sediment_depth":
                arcpy.AddMessage("Sediment depth added to monthly average")
                sed_depth_avg = sed_depth_avg + Q_surf # need to change Q_surf

            if output_type == "Net_sediment":
                arcpy.AddMessage("Net sediment added to monthly average")
                sed_erosion_deposition_avg = sed_erosion_deposition_avg + Q_surf # need to change Q_surf
                    
            if tomorrow_day == 1:
                if output_format == 'Daily average':
                    arcpy.AddMessage("Monthly average selected")
                    if output_type == "Surface_runoff": 
                        arcpy.AddMessage("Saving monthly Surface_runoff average")
                        Q_surf_avg = Q_surf_avg / month_day
                        Q_surf_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        Q_surf_avg = np.zeros_like(Q_surf_avg)

                    if output_type == "Discharge": 
                        arcpy.AddMessage("Saving monthly discharge average")
                        Q_dis_avg = Q_dis_avg / month_day
                        Q_dis_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                    if output_type == "Water_depth": 
                        arcpy.AddMessage("Saving monthly depth average")
                        depth_avg = depth_avg / month_day
                        depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        depth_avg = np.zeros_like(depth_avg)

                    if output_type == "Spatial_precipitation": 
                        arcpy.AddMessage("Saving spatial precipitation average")
                        precipitation_avg = precipitation_avg / month_day
                        precipitation_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        precipitation_avg = np.zeros_like(precipitation_avg)

                    if output_type == "Sediment_depth": 
                        arcpy.AddMessage("Saving monthly sediment depth average")
                        sed_depth_avg = sed_depth_avg / month_day
                        sed_depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        sed_depth_avg = np.zeros_like(sed_depth_avg)

                    if output_type ==  "Net_sediment": 
                        arcpy.AddMessage("Saving monthly sediment eroision/deposition average")
                        sed_erosion_deposition_avg = sed_erosion_deposition_avg / month_day
                        sed_erosion_deposition_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)
                        
                elif output_format == 'Total':
                    arcpy.AddMessage("Monthly total selected")
                    if output_type == "Surface_runoff": 
                        arcpy.AddMessage("Saving monthly Surface_runoff total")
                        Q_surf_avg = Q_surf_avg 
                        Q_surf_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        Q_surf_avg = np.zeros_like(Q_surf_avg)

                    if output_type == "Discharge": 
                        arcpy.AddMessage("Saving monthly discharge total")
                        Q_dis_avg = Q_dis_avg 
                        Q_dis_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                    if output_type == "Water_depth": 
                        arcpy.AddMessage("Saving monthly depth total")
                        depth_avg = depth_avg 
                        depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        depth_avg = np.zeros_like(depth_avg)

                    if output_type == "Spatial_precipitation": 
                        arcpy.AddMessage("Saving spatial precipitation total")
                        precipitation_avg = precipitation_avg 
                        precipitation_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        precipitation_avg = np.zeros_like(precipitation_avg)

                    if output_type == "Sediment_depth": 
                        arcpy.AddMessage("Saving monthly sediment depth total")
                        sed_depth_avg = sed_depth_avg 
                        sed_depth_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        sed_depth_avg = np.zeros_like(sed_depth_avg)

                    if output_type ==  "Net_sediment": 
                        arcpy.AddMessage("Saving monthly sediment eroision/deposition total")
                        sed_erosion_deposition_avg = sed_erosion_deposition_avg 
                        sed_erosion_deposition_avg[Q_surf_np == -9999] = -9999
                        convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, monthly_save_date)
                        sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)


            # What happens if the output is yearly
            if output_frequency == 'Yearly':
                arcpy.AddMessage("Tomorrow will be day " + str(tomorrow_day) + "and month will be " + str(tomorrow_month))                   
                    
                if output_type == "Surface_runoff":
                    arcpy.AddMessage("Surface_runoff added to yearly average")
                    Q_surf_avg = Q_surf_avg + Q_surf_np

                if output_type == "Discharge":
                    arcpy.AddMessage("Discharge added to yearly average")
                    Q_dis_avg = Q_dis_avg + Q_dis

                if output_type == "Water_depth":
                    arcpy.AddMessage("Water depth added to yearly average")
                    depth_avg = depth_avg + depth_recking

                if output_type == "Spatial_precipitation":
                    arcpy.AddMessage("Spatial precipitation added to yearly average")
                    precipitation_avg = precipitation_avg + precipitation

                if output_type == "Sediment_depth":
                    arcpy.AddMessage("Sediment depth added to yearly average")
                    sed_depth_avg = sed_depth_avg + Q_surf # need to change Q_surf

                if output_type == "Net_sediment":
                    arcpy.AddMessage("Net sediment added to yearly average")
                    sed_erosion_deposition_avg = sed_erosion_deposition_avg + Q_surf # need to change Q_surf
                    
                if tomorrow_day == 1 and tomorrow_month == 1:
                    if output_format == 'Daily average':
                        arcpy.AddMessage("Yearly average selected")
                        if output_type == "Surface_runoff": 
                            arcpy.AddMessage("Saving Yearly Surface_runoff average")
                            Q_surf_avg = Q_surf_avg / year_day
                            Q_surf_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            Q_surf_avg = np.zeros_like(Q_surf_avg)

                        if output_type == "Discharge": 
                            arcpy.AddMessage("Saving Yearly discharge average")
                            Q_dis_avg = Q_dis_avg / year_day
                            Q_dis_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                        if output_type == "Water_depth": 
                            arcpy.AddMessage("Saving Yearly depth average")
                            depth_avg = depth_avg / year_day
                            depth_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            depth_avg = np.zeros_like(depth_avg)

                        if output_type == "Spatial_precipitation": 
                            arcpy.AddMessage("Saving spatial precipitation Yearly average")
                            precipitation_avg = precipitation_avg / year_day
                            precipitation_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            precipitation_avg = np.zeros_like(precipitation_avg)

                        if output_type == "Sediment_depth": 
                            arcpy.AddMessage("Saving Yearly sediment depth average")
                            sed_depth_avg = sed_depth_avg / year_day
                            sed_depth_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            sed_depth_avg = np.zeros_like(sed_depth_avg)

                        if output_type ==  "Net_sediment": 
                            arcpy.AddMessage("Saving yearly net sediment average")
                            sed_erosion_deposition_avg = sed_erosion_deposition_avg / year_day
                            sed_erosion_deposition_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)

                    elif output_format == 'Total':
                        arcpy.AddMessage("Yearly total selected")
                        if output_type == "Surface_runoff": 
                            arcpy.AddMessage("Saving yearly Surface_runoff total")
                            Q_surf_avg = Q_surf_avg 
                            Q_surf_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(Q_surf_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            Q_surf_avg = np.zeros_like(Q_surf_avg)

                        if output_type == "Discharge": 
                            arcpy.AddMessage("Saving yearly discharge total")
                            Q_dis_avg = Q_dis_avg 
                            Q_dis_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(Q_dis_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            Q_dis_avg = np.zeros_like(Q_dis_avg)
                            
                        if output_type == "Water_depth": 
                            arcpy.AddMessage("Saving yearly depth total")
                            depth_avg = depth_avg 
                            depth_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            depth_avg = np.zeros_like(depth_avg)

                        if output_type == "Spatial_precipitation": 
                            arcpy.AddMessage("Saving yearly precipitation total")
                            precipitation_avg = precipitation_avg 
                            precipitation_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(precipitation_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            precipitation_avg = np.zeros_like(precipitation_avg)

                        if output_type == "Sediment_depth": 
                            arcpy.AddMessage("Saving yearly sediment depth total")
                            sed_depth_avg = sed_depth_avg 
                            sed_depth_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(sed_depth_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            sed_depth_avg = np.zeros_like(sed_depth_avg)

                        if output_type ==  "Net_sediment": 
                            arcpy.AddMessage("Saving yearly sediment eroision/deposition total")
                            sed_erosion_deposition_avg = sed_erosion_deposition_avg 
                            sed_erosion_deposition_avg[Q_surf_np == -9999] = -9999
                            convert_numpy_to_raster_single(sed_erosion_deposition_avg, output_type, bottom_left_corner, cell_size, year_save_date)
                            sed_erosion_deposition_avg = np.zeros_like(sed_erosion_deposition_avg)

    # Counter resets
    if week_day == 7:
        week_day = 0
        arcpy.AddMessage("Week complete resetting output counter")

    if tomorrow_day == 1:
        month_day = 0
        arcpy.AddMessage("Month complete resetting output counter")
            
    if tomorrow_day == 1 and tomorrow_month == 1:
        year_day = 0
        arcpy.AddMessage("Year complete resetting output counter")

    # Save the average arrays to disk if required
    for output_type, output_frequency in output_file_dict.iteritems():
        if str(output_frequency) != 'No output' and str(output_frequency) != 'Daily': 
            # Save the average arrays to disk.
            if output_type == "Surface_runoff":  
                np.save(output_averages_temp[0], Q_surf_avg)
                del Q_surf_avg
               
            if output_type == "Discharge": 
                np.save(output_averages_temp[1], Q_dis_avg)
                del Q_dis_avg

            if output_type == "Water_depth": 
                np.save(output_averages_temp[2], depth_avg)
                del depth_avg

            if output_type == "Spatial_precipitation": 
                np.save(output_averages_temp[3], precipitation_avg)
                del precipitation_avg

            if output_type == "Sediment_depth": 
                np.save(output_averages_temp[4], sed_depth_avg)
                del sed_depth_avg

            if output_type ==  "Net_sediment": 
                np.save(output_averages_temp[5], sed_erosion_deposition_avg)
                del sed_erosion_deposition_avg

    return week_day, month_day, year_day

def numpystocsv(list_of_numpys, list_of_numpy_names):
    
    for numpy_array, numpy_name in izip(list_of_numpys, list_of_numpy_names):
        numpy_array_type = type(numpy_array).__module__
        numpy_array_bool = type(numpy_array).__module__ == np.__name__

        if numpy_array_bool == True:   
            np.savetxt(r"D:/EngageTesting/CSV_outputs/" + numpy_name + ".csv", numpy_array, delimiter=",")
            print numpy_name + " is a numpy array." 
        else:
            print numpy_name + " is not a numpy array. It is " + str(numpy_array_type)

    