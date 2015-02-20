# Calculate the lower and upper limits for the volume of the active layer
al_upper_volume_limit = float(0.3 * cell_size * cell_size)
arcpy.AddMessage("Upper active layer limit set at " + str(al_upper_volume_limit))
al_lower_volume_limit = float(0.05 * cell_size * cell_size) 
arcpy.AddMessage("Lower active layer limit set at " + str(al_lower_volume_limit))
                                             
for active_layer_proportion_temp, active_layer_volume_temp, inactive_layer_proproportion_temp, inactive_layer_volume_temp in izip(active_layer_pro_temp_list, active_layer_vol_temp_list, inactive_layer_pro_temp_list):
    # Locad the arrays from the disk
    active_layer_proportion = np.load(active_layer_proportion_temp)
    active_layer_volume = np.load(active_layer_volume_temp)
    inactive_layer_proproportion = np.load(inactive_layer_proproportion_temp)
    
                                
    # Count the grainsizes as the model works through them
    grain_size_counter = 1
    total_inactive_layer_volume = 0.0
    total_active_layer_soil_volume = 0.0

    # Check the depth of the active layer is not to large or too small
    for i, j in new_idx: # Iterate through the cells transporting sediment
                    
        if float(active_layer[i, j]) >= al_upper_volume_limit: # check to see if the volume in that cell is greater than 30m3
            arcpy.AddMessage("The cell " + str(i) + " " + str(j) + " depth is " + str(active_layer[i, j]) + "m3 which is over " + str(al_upper_volume_limit) + " recalculating active layer depth....") 
            arcpy.AddMessage(" ") 
            inactive_layer_volume_list = []    
                        
            # Calculate the volume of grainsize in the remaining soil
            inactive_layer_volume = inactive_layer[i, j] * inactive_layer_proproportion[i, j]
            arcpy.AddMessage("The previous volume of grain size " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume))
                        
            # Calculate the amount that needs to be added to the remaining soil volume that from the active layer
            new_inactive_layer_grainsize_volume = (20 * active_layer_proportion[i, j]) + inactive_layer_volume # add 20cm proportion of that grainsize to the active layer
            arcpy.AddMessage("The new volume of grain size " + str(grain_size_counter) + " in the inactive layer is " + str(new_inactive_layer_grainsize_volume))
            arcpy.AddMessage(" ") 

            # Add the new volume to a list
            inactive_layer_volume_list.append(new_inactive_layer_grainsize_volume)
                        
            # Keep a total of the total volume of the remaining soil volume
            total_inactive_layer_volume = total_inactive_layer_volume + new_inactive_layer_grainsize_volume                         
            arcpy.AddMessage("Total soil volume in the inactive layer is " + str(total_inactive_layer_volume))
            arcpy.AddMessage(" ") 

            # Take 20cm3 off the total active layer volume and then work out the new volumes in the active layer
            active_layer_volume[i, j] = (active_layer[i, j] - 20) * active_layer_proportion[i, j] 
                        
            arcpy.AddMessage("New grainsize volume " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))  
            arcpy.AddMessage(" ")                                               
            np.save(active_layer_volume_temp, active_layer_volume)
            grain_size_counter += 1

            # Now the code jumps down to after else statement
                  
        elif active_layer[i, j] < lower_volume_limit and inactive_layer[i, j] > 0: # check to see if the volume in that cell is greater than 5m3
                                            
            arcpy.AddMessage("The cell " + str(i) + " " + str(j) + " depth is " + str(active_layer[i, j]) + "m3 which is under " + str(lower_volume_limit) + " recalculating active layer depth....") 
            arcpy.AddMessage(" ") 
            total_soil_removed_from_remaining = 0.0
            total_active_soil_volume = 0.0   
            total_inactive_layer_volume = inactive_layer_volume[i, j]          
            inactive_layer_volumes_list = []
                    
            # The volume of the grainsize left in the active layer is
            arcpy.AddMessage("Current active layer volume of grain size " + str(grain_size_counter) + " is " + str(grain_volume[i, j]))
                        
            if inactive_layer_volume[i, j] >= 20:
                # Calculate the volume that needs to be added to this grainsize 
                active_layer_volume_added = 20 * inactive_layer_pro[i, j]
                grain_volume[i, j] = active_layer_volume_added + grain_volume[i, j]                      
                arcpy.AddMessage("New active layer soil " + str(grain_volume[i, j]))
                np.save(grain_volume_temp, grain_volume)

                # take 20cm3 off the total remaining volume and then work out the new proportions in the remaining soil volume
                new_inactive_layer_volume = (20 * inactive_layer_pro[i, j]) 
                total_soil_removed_from_remaining = total_soil_removed_from_remaining + new_inactive_layer_volume
                arcpy.AddMessage("Soil volume of grain size being removed from below the active layer " + str(grain_size_counter) + " is " + str(new_inactive_layer_volume))

            elif inactive_layer_volume[i, j] < 20:
                # Calculate the volume that needs to be added to this grainsize 
                active_layer_volume_added = inactive_layer_volume[i, j] * inactive_layer_pro[i, j]
                grain_volume[i, j] = active_layer_volume_added + grain_volume[i, j]                      
                arcpy.AddMessage("New active layer soil " + str(grain_volume[i, j]))
                np.save(grain_volume_temp, grain_volume)

                # take off the total remaining volume and then work out the new proportions in the remaining soil volume
                new_inactive_layer_volume = (inactive_layer_volume[i, j] * inactive_layer_pro[i, j]) 
                total_soil_removed_from_remaining = total_soil_removed_from_remaining + new_inactive_layer_volume
                arcpy.AddMessage("Soil volume of grain size being removed from below the active layer" + str(grain_size_counter) + " is " + str(new_inactive_layer_volume))

            else:
                arcpy.AddMessage("No soil in this cell to top up active layer")


            # There is a need to calculate the total active layer volume for that cell                                                         
            total_active_layer_soil_volume = total_active_layer_soil_volume + active_layer_volume[i, j]                                             
            arcpy.AddMessage("Total soil volume in the active layer is " + str(total_active_soil_volume))                        
                        
                                                                                        
            # Increment the counter by one
            grain_size_counter += 1

        for active_layer_proportion_temp, grain_volume_temp in izip(active_layer_pro_temp_list, active_layer_vol_temp_list):
            grain_proportion = np.load(grain_proportion_temp)
            grain_volume = np.load(grain_volume_temp)

            grain_proportion[i, j] = total_active_soil_volume / grain_volume[i, j]
            np.save(grain_proportion_temp, grain_proportion)      
                        
        # Take amount off the total in the remaining soil
        inactive_layer_volume[i, j] = inactive_layer_volume[i, j] - total_soil_removed_from_remaining
        arcpy.AddMessage("Total soil volume not in the active layer is " + str(inactive_layer_volume[i, j]))
        arcpy.AddMessage(" ")

        # Add 20cm3 to the remaining soil volume
        inactive_layer_volume[i, j] = total_inactive_layer_volume
        total_volume_active_layer[i, j] = total_volume_active_layer[i, j] - 20

        for inactive_layer_pro_temp, inactive_layer_vol in izip (inactive_layer_pro_temp_list, inactive_layer_grainsize_volumes_list):
            inactive_layer_pro = np.load(inactive_layer_pro_temp)
            inactive_layer_pro[i, j] = inactive_layer_vol / total_inactive_layer_volume
            np.save(inactive_layer_pro_temp, inactive_layer_pro)

# grain size volumes counter
counter_proportion = 1

for grain_proportion_temp in inactive_layer_pro_temp_list:
    grain_proportion = np.load(grain_proportion_temp)                               
                
                
    arcpy.AddMessage("Saved proportions in remaining soil to disk " + str(counter_proportion)) 
                
    grain_proportion[slope == -9999] = -9999 
           
    counter_proportion += 1
    if counter_proportion == 8:
        counter_proportion = 1