# Import statements
import numpy as np
import time
import arcpy
from itertools import izip
import gc

# User created scripts
import rasterstonumpys


class sedimenttransport(object):
    """description of class"""

    # Combined function to calculate the d50, d84, Fs of the input grainsizes
    def d50_d84_Fs_grain(self, grain_size_list, active_layer_pro_temp_list):

        start = time.time()

        grain_size_1_proportion = np.load(active_layer_pro_temp_list[0])
        grain_size_2_proportion = np.load(active_layer_pro_temp_list[1])
        grain_size_3_proportion = np.load(active_layer_pro_temp_list[2])
        grain_size_4_proportion = np.load(active_layer_pro_temp_list[3])
        grain_size_5_proportion = np.load(active_layer_pro_temp_list[4])      
        grain_size_6_proportion = np.load(active_layer_pro_temp_list[5])
        grain_size_7_proportion = np.load(active_layer_pro_temp_list[6])

        # load grain size proportions
        grain_size_proportions = [grain_size_1_proportion, grain_size_2_proportion, grain_size_3_proportion, grain_size_4_proportion, grain_size_5_proportion, grain_size_6_proportion, grain_size_7_proportion]

        # Add the no data value to the grain size list
        grain_size_list.append(-9999)

        graintable = np.array(grain_size_list)

        def V_get_grain50(grain_size_proportions):
            
            # create the cumulative sum buffer (empty at this point)
            csum = np.zeros_like(grain_size_proportions[0], dtype = float)
            # create the counter for number of samples needed to reach .5
            cnt = np.zeros(grain_size_proportions[0].shape, dtype='uint8')

            # iterate through the images:
            for grain_proportion in grain_size_proportions:
                # add the image into the cumulative sum buffer
                csum += grain_proportion
                # add 1 to the counter if the sum of a pixel is < .5
                cnt += csum < .5

            # now cnt has a number for each pixel:
            # 0: the first image >= .5
            # ...
            # 9: all images together < .5

            return graintable[cnt]
        
        d50 = V_get_grain50(grain_size_proportions)

        d50[grain_size_proportions[0] == -9999] = -9999              
        
        def V_get_grain84(grain_size_proportions):
            
            # create the cumulative sum buffer (empty at this point)
            csum = np.zeros_like(grain_size_proportions[0], dtype = float)
            # create the counter for number of samples needed to reach .84
            cnt = np.zeros(grain_size_proportions[0].shape, dtype='uint8')

            # iterate through the images:
            for grain_proportion in grain_size_proportions:
                # add the image into the cumulative sum buffer
                csum += grain_proportion
                # add 1 to the counter if the sum of a pixel is < .5
                cnt += csum < .84

            # now cnt has a number for each pixel:
            # 0: the first image >= .5
            # ...
            # 9: all images together < .5

            return graintable[cnt]

        d84 = V_get_grain84(grain_size_proportions)
        d84[grain_size_proportions[0] == -9999] = -9999
        
        Fs = np.zeros_like(grain_size_proportions[0])

        for grain_proportion, grain_size in izip(grain_size_proportions, grain_size_list):  
            if grain_size > 0.0000625 and grain_size <= 0.002:
                
                Fs = Fs + grain_proportion

        Fs[grain_size_proportions[0] == -9999] = -9999

        arcpy.AddMessage("Calculating d50 (Medium grain size), d84 (84% grain size), Fs (sand fraction (%)) took " + str(round(time.time() - start,2)) + "s.") 
        arcpy.AddMessage(" ") 

        return d50, d84, Fs

    # Calculate the recking parameter in order to work out the depth - it requires, slope, d84 and unit width discharge. - checked 04/07/14
    def depth_recking(self, Q_dis, slope, d84, cell_size):
        
        start = time.time()
        
        # convert discharge into unit width 
        q_dis = Q_dis / cell_size

        pre_slope = 9.81 * slope

        recking_parameter = np.zeros_like(slope, dtype = float)
        recking_parameter = q_dis / (np.sqrt(pre_slope * d84**3))
        recking_parameter[slope == -9999] = -9999

        depth_100 = d84**0.1
        depth_100 *= q_dis**0.6
        depth_100 /= pre_slope**0.3
        depth_100 *= 1/3.2 

        
        q_dis **=0.46
        pre_slope **= 0.23

        depth_1 = d84**0.31
        depth_1 *= q_dis
        depth_1 /= pre_slope
        depth_1 *= 1/1.6
                     
        depth_recking = np.zeros_like(slope, dtype = float)

        np.putmask(depth_recking, recking_parameter >= 100, depth_100)
        np.putmask(depth_recking, recking_parameter < 100, depth_1)

        depth_recking[slope == -9999] = -9999

        

        ### GET THE INDICES OF CELLS WITH CELLS GREATER THAN THE DEPTH THRESHOLD ###
        # Calculate the depth threshold
        #depth_threshold = cell_size / 1000
        depth_threshold = 0.0

        # Create the empty arrays for putting the masked data into
        depth_mask = np.zeros_like(depth_recking, dtype = float)

        # Check that the depth is great enough to intitate sediment transport in selected cells - might need changing though 
        # - this only gets the cells with great enough depth for sediment transport to occur and this will need to be recalcuclate for each timestep
        np.putmask(depth_mask, depth_recking >= depth_threshold, depth_recking)
        
        # Get the indices where the sediment transport is greater than 0 
        sort_idx = np.flatnonzero(depth_mask)

        # Now return those indices as a list
        new_idx = zip(*np.unravel_index(sort_idx[::-1], depth_recking.shape))

        arcpy.AddMessage("Calculating depth using the recking parameter took " + str(round(time.time() - start,2)) + "s.") 
        arcpy.AddMessage(" ") 

        return depth_recking, new_idx

    # Calculate the sediment entrainment for the grainsizes and then use that to calculate the sediment timestep - checked 04/07/14
    def SedimentEntrainmentQmax(self, new_idx, slope, depth_recking, Fs, d50, cell_size, grain_size_list, active_layer_pro_temp_list):
        
        start = time.time()

        grain_size_1_proportion = np.load(active_layer_pro_temp_list[0])
        grain_size_2_proportion = np.load(active_layer_pro_temp_list[1])
        grain_size_3_proportion = np.load(active_layer_pro_temp_list[2])
        grain_size_4_proportion = np.load(active_layer_pro_temp_list[3])
        grain_size_5_proportion = np.load(active_layer_pro_temp_list[4])      
        grain_size_6_proportion = np.load(active_layer_pro_temp_list[5])
        grain_size_7_proportion = np.load(active_layer_pro_temp_list[6])

        # load grain size proportions
        grain_size_proportions = [grain_size_1_proportion, grain_size_2_proportion, grain_size_3_proportion, grain_size_4_proportion, grain_size_5_proportion, grain_size_6_proportion, grain_size_7_proportion]
        
        def sediment_entrainment_calculation(new_idx, slope, depth_recking, Fs, d50, grain_size, grain_proportion, layer_height, cell_size):

            sediment_entrainment = np.zeros_like(slope, dtype = float)     

            for i, j in new_idx:

                T = 1000 * 9.81 * slope[i, j] * depth_recking[i, j]

                Trs50= 1.65 * 1000 * 9.81 * d50[i, j]

                Trs50 *= 0.021 + (0.015 * np.exp(-20 * Fs[i, j]))

                Tri =  grain_size / d50[i, j]

                Tri **= 0.67 / (1 + np.exp(1.5 - (grain_size / d50[i, j])))

                Tri *= Trs50
        
                shear_vel = (T / 1000)**0.5   
            
                ToverTri = T / Tri
                
                Wi = 0

                if ToverTri < 1.35:
                    Wi = (ToverTri**7.5)*0.002
                else:
                    Wi = 14 * np.power(1 - (0.894 / np.power(ToverTri, 0.5)), 4.5)

                sediment_entrainment[i, j] = (Wi * grain_proportion[i, j] * np.power(shear_vel, 3)) / ((2.65 - 1) * 9.81)

                # Convert sediment to width of channel by multiplying by the cell size
                sediment_entrainment[i, j] = sediment_entrainment[i, j] * cell_size

            sediment_entrainment[slope== -9999] = -9999 # Ensure no data cells remain no data

            return sediment_entrainment
                 
      
        # Grain size counter
        counter = 1
        Q_max_accumulation = 0.0


        # Temporary active layer height
        layer_height = 0.2
              
        # Iterate through the grain sizes and proportions calculating the transport
        for grain_size, grain_proportion in izip(grain_size_list, grain_size_proportions):                                 
            # Calculate sediment transport for that grainsize
            sediment_entrainment = sediment_entrainment_calculation(new_idx, slope, depth_recking, Fs, d50, grain_size, grain_proportion, layer_height, cell_size)

            arcpy.AddMessage("Calculated sediment transport for " + "_" + str(grain_size))
                            
            Q_max = np.amax(sediment_entrainment)

            Q_max_accumulation += Q_max 
                        
            arcpy.AddMessage("Q_max for " + str(grain_size) + " is " + str(Q_max))
            arcpy.AddMessage("Accumulated Q_max is " + str(Q_max_accumulation))
            arcpy.AddMessage(" ")

            # Increase the grain size counter by 1
            counter +=1
                            
        sediment_time_step_seconds = ((0.1 * layer_height) * (cell_size * cell_size)) / Q_max_accumulation
        if sediment_time_step_seconds < 10:
            sediment_time_step_seconds = 10
                
        arcpy.AddMessage("The timestep based on these caluclations should be " + str(sediment_time_step_seconds) + " seconds")  
        
        arcpy.AddMessage("Calculating maximum entrainment and sediment timestep " + str(round(time.time() - start,2)) + "s.") 
        arcpy.AddMessage(" ")
                          
        return sediment_time_step_seconds

    def active_layer_depth(self, active_layer, inactive_layer, new_idx, active_layer_pro_temp_list, active_layer_vol_temp_list, inactive_layer_pro_temp_list, inactive_layer_vol_temp_list, cell_size, iteration_counter):
            
        # Calculate the lower and upper limits for the volume of the active layer
        al_upper_volume_limit = float(0.3 * cell_size * cell_size)
        arcpy.AddMessage("Upper active layer limit set at " + str(al_upper_volume_limit))
        al_lower_volume_limit = float(0.05 * cell_size * cell_size) 
        arcpy.AddMessage("Lower active layer limit set at " + str(al_lower_volume_limit))
         
        # Count the grainsizes as the model works through them
        grain_size_counter = 1    
         
        # Set up some empty arrays to hold the new values 
        new_active_layer_total = np.zeros_like(active_layer)
        new_inactive_layer_total = np.zeros_like(inactive_layer)
                                       
        for active_layer_proportion_temp, active_layer_volume_temp, inactive_layer_proproportion_temp, inactive_layer_volume_temp in izip(active_layer_pro_temp_list, active_layer_vol_temp_list, inactive_layer_pro_temp_list, inactive_layer_vol_temp_list):
            # Locad the arrays from the disk
            active_layer_proportion = np.load(active_layer_proportion_temp)
            active_layer_volume = np.load(active_layer_volume_temp)
            inactive_layer_proproportion = np.load(inactive_layer_proproportion_temp)
            inactive_layer_volume = np.load(inactive_layer_volume_temp)
                                
            
            # Check the depth of the active layer is not to large or too small
            for i, j in new_idx: # Iterate through the cells transporting sediment
                    
                if float(active_layer[i, j]) >= al_upper_volume_limit: # check to see if the volume in that cell is greater than 30m3
                    arcpy.AddMessage(" ") 
                    arcpy.AddMessage("The cell " + str(i) + " " + str(j) + " depth is " + str(active_layer[i, j]) + "m3 which is over " + str(al_upper_volume_limit) + " recalculating active layer depth....") 
                                          
                    # Calculate the amount that needs to be added to the remaining soil volume that from the active layer
                    arcpy.AddMessage("The previous volume of grain size " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume[i, j]))
                    inactive_layer_volume[i, j] = (20 * active_layer_proportion[i, j]) + inactive_layer_volume[i, j] # add 20cm proportion of that grainsize to the active layer
                    arcpy.AddMessage("The new volume of grain size " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume[i, j]))
                    
                    # Take 20cm3 off the total active layer volume and then work out the new volumes in the active layer
                    arcpy.AddMessage("Previous grainsize volume " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))  
                    active_layer_volume[i, j] = (active_layer[i, j] - 20) * active_layer_proportion[i, j]                         
                    arcpy.AddMessage("New grainsize volume " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))  
                                                                                    
                    np.save(inactive_layer_volume_temp, inactive_layer_volume)
                    np.save(active_layer_volume_temp, active_layer_volume)
                    arcpy.AddMessage("Change to volume saved to disk")
            
            # Add the new calculated volumes to a running total array
            new_active_layer_total += active_layer_volume
            new_inactive_layer_total += inactive_layer_volume

            # Increment the grainsize by 1 for the next round of calculations
            grain_size_counter = grain_size_counter + 1
            
        new_active_layer_total[active_layer == -9999] = -9999
        new_inactive_layer_total[inactive_layer == -9999] = -9999

        return new_active_layer_total, new_inactive_layer_total
                                                     
    def sediment_loop(self, sediment_time_step_seconds, grain_size_list, Q_dis, slope, cell_size, flow_direction_np, bottom_left_corner, save_date, active_layer_pro_temp_list, active_layer_vol_temp_list, inactive_layer, inactive_layer_pro_temp_list, inactive_layer_vol_temp_list):
                
        def sediment_entrainment_calculation(new_idx, slope, depth_recking, Fs, d50, grain_size, grain_proportion, grain_volume, cell_size):

            sediment_entrainment = np.zeros_like(slope, dtype =  float)     

            for i, j in new_idx:

                T = 1000 * 9.81 * slope[i, j] * depth_recking[i, j]

                Trs50= 1.65 * 1000 * 9.81 * d50[i, j]

                Trs50 *= 0.021 + (0.015 * np.exp(-20 * Fs[i, j]))

                Tri =  grain_size / d50[i, j]

                Tri **= 0.67 / (1 + np.exp(1.5 - (grain_size / d50[i, j])))

                Tri *= Trs50
        
                shear_vel = (T / 1000)**0.5   
            
                ToverTri = T / Tri
                
                if ToverTri < 1.35:
                    Wi = (ToverTri**7.5) * 0.002
                else:
                    Wi = 14 * np.power(1 - (0.894 / np.power(ToverTri, 0.5)), 4.5)

                sediment_entrainment[i, j] = (Wi * grain_proportion[i, j] * np.power(shear_vel, 3)) / ((2.65 - 1) * 9.81)

                # Convert from unit width to width by multiplying by the width of the cell

                sediment_entrainment[i, j] = sediment_entrainment[i, j] * cell_size
                                                
                # Ensures that the transport rates does not exceed the amount left in the active layer
                if sediment_entrainment[i, j] >= grain_volume[i, j]:
                    sediment_entrainment[i, j] = grain_volume[i, j]

            sediment_entrainment[slope == -9999] = -9999 # Ensure no data cells remain no data

            return sediment_entrainment

        def move_sediment(new_idx, sediment_entrainment_out, slope, flow_direction_np):
             
            # Create empty array for the moved sediment
            sediment_entrainment_in = np.zeros_like(slope, dtype = float)
        
            # Get the rows and columns of the slope file
            nrows, ncols = slope.shape

            # Pads the array with zeros to prevent negative indexing
            tmp = np.zeros((nrows+2, ncols+2), dtype = float) 
            tmp[1:-1, 1:-1] = sediment_entrainment_out
            sediment_entrainment_out = tmp

            # Pads the grain size active layer to prevent negative indexing
            #tmp2 = np.zeros((nrows+2, ncols+2), dtype = float) 
            #tmp2[1:-1, 1:-1] = grain_size_active_layer_mask
            #grain_size_active_layer_mask = tmp2
        
            lookup = {32: (-1, -1),
              16:  (0, -1), 
              8:   (1, -1),
              4:   (1,  0),
              64: (-1,  0),
              128:(-1,  1),
              1:   (0,  1),
              2:   (1,  1)}

            for i, j in new_idx:
            # Need to take into account the offset in the "padded_transport"
                r, c = i + 1, j + 1
                # This also allows for flow_direction values not listed above...
                dr, dc = lookup.get(flow_direction_np[i, j], (0,0)) # Gets the flow direction for that cell
                #if grain_transport_mask[r, c] <= grain_size_active_layer_mask[r, c]: # this adds in a check to make sure that there is sufficient sediment in the active layer to transport it. 
                sediment_entrainment_in[i + dr, j + dc] += sediment_entrainment_out[r, c] # move the sediment in the downstream direction by one timestep.

            sediment_entrainment_in[slope == -9999] = -9999

            return sediment_entrainment_in
                        
        total_change = np.zeros_like(slope, dtype = float)

        counter_transport = 1
        total_time = 0.0
        iteration_counter = 1
        layer_height = 0.2 # metres - need to convert to volume at some point
        
        #Add the first time_step onto the loop
        if sediment_time_step_seconds < 86400:
            total_time += sediment_time_step_seconds
        
        while total_time < 86400:
            arcpy.AddMessage("Time of day = " + str(total_time) + "s.")
           
            total_volume = np.zeros_like(slope, dtype = float)

            # Calculate the d50, d84, Fs for this timestep
            d50, d84, Fs = self.d50_d84_Fs_grain(grain_size_list, active_layer_pro_temp_list)

            # Calcualte the depth recking and index of active cells in this timestep
            depth_recking, new_idx = self.depth_recking(Q_dis, slope, d84, cell_size)
            
            # Iterate through the grain sizes and proportions calculating the transport
            for grain_size, grain_proportion_temp, grain_volume_temp in izip(grain_size_list, active_layer_pro_temp_list, active_layer_vol_temp_list):
                
                grain_proportion = np.load(grain_proportion_temp)
                grain_volume = np.load(grain_volume_temp)
                arcpy.AddMessage("Loaded grain proportion and volume")                
                                               
                # Calculate sediment transport out for that grainsize
                sediment_entrainment_out = sediment_entrainment_calculation(new_idx, slope, depth_recking, Fs, d50, grain_size, grain_proportion, grain_volume, cell_size)
                sediment_entrainment_out = sediment_entrainment_out * sediment_time_step_seconds # convert to the total amount by times by the total
                arcpy.AddMessage("Calculated sediment transport for " + "_" + str(grain_size))
           
                # Calculate sediment transport in for that grainsize
                sediment_entrainment_in = move_sediment(new_idx, sediment_entrainment_out, slope, flow_direction_np)
                arcpy.AddMessage("Transported sediment for grain size " + "_" + str(grain_size))

                # Calculate the change in sediment volume
                new_grain_volume = grain_volume - sediment_entrainment_out + sediment_entrainment_in

                # Calculate the total leaving the cells
                total_change = total_change - sediment_entrainment_out 
                total_change = total_change + sediment_entrainment_in
                
                # Calcuate the change per grainsize
                sediment_change = np.zeros_like(slope, dtype = float)
                
                # Update the total volume
                total_volume += new_grain_volume

                # Calculate the total leaving the cells
                sediment_change = sediment_change - sediment_entrainment_out 
                sediment_change = sediment_change + sediment_entrainment_in
                np.save(grain_volume_temp, new_grain_volume)

                arcpy.AddMessage("Calculated sediment transport for grain size " + str(counter_transport))

                # Increase the grain counter by 1 until it reaches 7
                counter_transport +=1
                if counter_transport == 8:
                    counter_transport = 1

            # Collect garbage
            del d50, d84, Fs, depth_recking, sediment_change, sediment_entrainment_out, sediment_entrainment_in
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 

            # grain size volumes counter
            counter_proportion = 1

            for grain_proportion_temp, grain_volume_temp in izip(active_layer_pro_temp_list, active_layer_vol_temp_list):
                grain_volume = np.load(grain_volume_temp)                               
                grain_proportion = grain_volume / total_volume
                
                arcpy.AddMessage("Calculated new proportion for grainsize " + str(counter_proportion)) 
                
                grain_proportion[slope == -9999] = -9999 
                np.save(grain_proportion_temp, grain_proportion) 
                
                del grain_volume, grain_proportion

                counter_proportion += 1
                if counter_proportion == 8:
                    counter_proportion = 1
                              
            # Collect garbage
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected))      
                                   
            active_layer, inactive_layer = self.active_layer_depth(total_volume, inactive_layer, new_idx, active_layer_pro_temp_list, active_layer_vol_temp_list,  inactive_layer_pro_temp_list, inactive_layer_vol_temp_list, cell_size, iteration_counter)

            # Increment the timestep ready for the next loop
            total_time += sediment_time_step_seconds
            total_change[slope == -9999] = -9999
            total_volume[slope == -9999] = -9999

            iteration_counter += 1



            ### Section to save rasters while testing model ###
            rasterstonumpys.convert_numpy_to_raster_single(active_layer, "active_layer", bottom_left_corner, cell_size, "0")
            rasterstonumpys.convert_numpy_to_raster_single(inactive_layer, "inactive_layer", bottom_left_corner, cell_size, "0")
        