#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import numpy as np
import time
import arcpy
from itertools import izip
import gc



# User created scripts
import rasterstonumpys
import elevation_adjustment
import active_inactive_layer_check
import masswasting

class sedimenttransport(object):
    """description of class"""

    # Combined function to calculate the d50, d84, Fs of the input grainsizes - checked 11/06/15
    def d50_d84_Fs_grain(self, GS_list, active_layer_GS_P_temp):

        start = time.time()

        GS_1_P = np.load(active_layer_GS_P_temp[0])
        GS_2_P = np.load(active_layer_GS_P_temp[1])
        GS_3_P = np.load(active_layer_GS_P_temp[2])
        GS_4_P = np.load(active_layer_GS_P_temp[3])
        GS_5_P = np.load(active_layer_GS_P_temp[4])      
        GS_6_P = np.load(active_layer_GS_P_temp[5])
        GS_7_P = np.load(active_layer_GS_P_temp[6])

        # load grain size proportions
        GS_P_list = [GS_1_P, GS_2_P, GS_3_P, GS_4_P, GS_5_P, GS_6_P, GS_7_P]

        
        # Add the no data value to the grain size list
        no_data = -9999
        if no_data not in GS_list:  
            arcpy.AddMessage("-------------------------")  
            arcpy.AddMessage("No data not found in list")  
            arcpy.AddMessage("Added no data (-9999) to list")  
            arcpy.AddMessage("-------------------------")         
            GS_list.append(-9999)
        else:
            arcpy.AddMessage("-------------------------") 
            arcpy.AddMessage("No data value found in list")
            arcpy.AddMessage("-------------------------") 

        graintable = np.array(GS_list)

        def V_get_grain50(GS_P_list):
            
            # create the cumulative sum buffer (empty at this point)
            csum = np.zeros_like(GS_P_list[0], dtype = float)
            # create the counter for number of samples needed to reach .5
            cnt = np.zeros(GS_P_list[0].shape, dtype='uint8')

            # iterate through the images:
            for grain_proportion in GS_P_list:
                # add the image into the cumulative sum buffer                
                csum += grain_proportion
                # add 1 to the counter if the sum of a pixel is < .5
                cnt += csum < .5

            # now cnt has a number for each pixel:
            # 0: the first image >= .5
            # ...
            # 9: all images together < .5

            return graintable[cnt]
        
        
        d50 = V_get_grain50(GS_P_list)

        d50[GS_P_list[0] == -9999] = -9999              
        
        def V_get_grain84(GS_P_list):
            
            # create the cumulative sum buffer (empty at this point)
            csum = np.zeros_like(GS_P_list[0], dtype = float)
            # create the counter for number of samples needed to reach .84
            cnt = np.zeros(GS_P_list[0].shape, dtype='uint8')

            # iterate through the images:
            for grain_proportion in GS_P_list:
                # add the image into the cumulative sum buffer
                csum += grain_proportion
                # add 1 to the counter if the sum of a pixel is < .5
                cnt += csum < .84

            # now cnt has a number for each pixel:
            # 0: the first image >= .5
            # ...
            # 9: all images together < .5

            return graintable[cnt]
                
        d84 = V_get_grain84(GS_P_list)
        d84[GS_P_list[0] == -9999] = -9999
        
        Fs = np.zeros_like(GS_P_list[0])

        for grain_proportion, grain_size in izip(GS_P_list, GS_list):  
            if grain_size > 0.0000625 and grain_size <= 0.002:
                
                Fs = Fs + grain_proportion

        Fs[GS_P_list[0] == -9999] = -9999
        
        arcpy.AddMessage("Calculating d50 (Medium grain size), d84 (84% grain size), Fs (sand fraction (%)) took " + str(round(time.time() - start,2)) + "s.") 
        arcpy.AddMessage(" ") 

        return d50, d84, Fs, GS_P_list

    # Calculate the recking parameter in order to work out the depth - it requires, slope, d84 and unit width discharge. - checked 04/07/14
    def depth_recking(self, Q_dis, slope, d84, cell_size):
        
        start = time.time()
                       
        q_dis = Q_dis / cell_size
                                      
        pre_slope = 9.81 * slope

        sqrt = np.sqrt(pre_slope)

        recking_parameter = np.zeros_like(slope, dtype= float)
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
        arcpy.AddMessage("Calculating depth took " + str(round(time.time() - start,2)) + "s.") 
        arcpy.AddMessage(" ") 
                      
        return depth_recking

    # Calculate the sediment entrainment for the grainsizes and then use that to calculate the sediment timestep - checked 04/07/14
    def SedimentEntrainmentQmax(self, slope, depth_recking, Fs, d50, cell_size, GS_list, GS_P_list):
        
        start = time.time()
        
        def sediment_entrainment_calculation(slope, depth_recking, Fs, d50, grain_size, grain_proportion, cell_size):

            # Create a series of empty arrays
            sediment_entrainment = np.zeros_like(slope, dtype = float)     
            T = np.zeros_like(slope, dtype = float) 
            Trs50 = np.zeros_like(slope, dtype = float) 
            Tri = np.zeros_like(slope, dtype = float) 
            shear_vel = np.zeros_like(slope, dtype = float) 
            ToverTri = np.zeros_like(slope, dtype = float) 
            Wi = np.zeros_like(slope, dtype = float) 
                        
            B = (depth_recking > 0.01)

            T[B] = slope[B] * depth_recking[B]
                                    
            T[B] *= 1000 * 9.81         
            
            Trs50[B] = 1.65 * 1000 * 9.81 * d50[B]
            
            Trs50[B] *= 0.021 + (0.015 * np.exp(-20 * Fs[B]))

            Tri[B] =  grain_size / d50[B]
            
            Tri[B] **= 0.67 / (1 + np.exp(1.5 - (grain_size / d50[B])))
                        
            Tri[B] *= Trs50[B]
            
            shear_vel[B] = (T[B] / 1000)**0.5   
            
            ToverTri[B] = T[B] / Tri[B]
            
            C = np.logical_and(ToverTri > 0.01, ToverTri < 1.35)
            
            Wi[C] = (ToverTri[C]**7.5)*0.002
            
            C = np.logical_and(ToverTri > 0.01, ToverTri > 1.35)
            
            Wi[C] = 14 * np.power(1 - (0.894 / np.power(ToverTri[C], 0.5)), 4.5)
            
            sediment_entrainment[B] = (Wi[B] * grain_proportion[B] * np.power(shear_vel[B], 3)) / ((2.65 - 1) * 9.81)

            # Convert sediment to width of channel by multiplying by the cell size
            sediment_entrainment[B] = sediment_entrainment[B] * cell_size

            sediment_entrainment[slope== -9999] = -9999 # Ensure no data cells remain no data
            
            return sediment_entrainment
                 
      
        # Grain size counter
        counter = 1
        Q_max_accumulation = 0.0


        # Temporary active layer height
        layer_height = 0.2
              
        # Iterate through the grain sizes and proportions calculating the transport
        for grain_size, grain_proportion in izip(GS_list, GS_P_list):                                 
            # Calculate sediment transport for that grainsize
            sediment_entrainment = sediment_entrainment_calculation(slope, depth_recking, Fs, d50, grain_size, grain_proportion, cell_size)
            
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


                                                     
    def sediment_loop(self, sediment_time_step_seconds, GS_list, Q_dis, slope, 
                                                           cell_size, flow_direction_np, bottom_left_corner, daily_save_date, 
                                                           active_layer_GS_P_temp, active_layer_V_temp, 
                                                           inactive_layer_GS_P_temp, inactive_layer_V_temp, inactive_layer,
                                                           DTM, DTM_MINUS_AL_IAL):
                
        def sediment_entrainment_calculation(slope, depth_recking, Fs, d50, GS, GS_P, GS_V, cell_size, sediment_time_step_seconds):

            # Create a series of empty arrays
            sediment_entrainment = np.zeros_like(slope, dtype = float)     
            T = np.zeros_like(slope, dtype = float) 
            Trs50 = np.zeros_like(slope, dtype = float) 
            Tri = np.zeros_like(slope, dtype = float) 
            shear_vel = np.zeros_like(slope, dtype = float) 
            ToverTri = np.zeros_like(slope, dtype = float) 
            Wi = np.zeros_like(slope, dtype = float) 
                        
            B = (depth_recking > 0.01)
             
            T[B] = slope[B] * depth_recking[B]
                                   
            T[B] *= 1000 * 9.81         
            
            Trs50[B] = 1.65 * 1000 * 9.81 * d50[B]
            
            Trs50[B] *= 0.021 + (0.015 * np.exp(-20 * Fs[B]))

            Tri[B] =  GS / d50[B]
            
            Tri[B] **= 0.67 / (1 + np.exp(1.5 - (GS / d50[B])))
                        
            Tri[B] *= Trs50[B]
            
            shear_vel[B] = (T[B] / 1000)**0.5   
            
            ToverTri[B] = T[B] / Tri[B]
            
            C = np.logical_and(ToverTri > 0.01, ToverTri < 1.35)
            
            Wi[C] = (ToverTri[C]**7.5)*0.002
            
            C = np.logical_and(ToverTri > 0.01, ToverTri > 1.35)
            
            Wi[C] = 14 * np.power(1 - (0.894 / np.power(ToverTri[C], 0.5)), 4.5)
            
            sediment_entrainment[B] = (Wi[B] * GS_P[B] * np.power(shear_vel[B], 3)) / ((2.65 - 1) * 9.81)

            # Convert sediment to width of channel by multiplying by the cell size
            sediment_entrainment[B] = sediment_entrainment[B] * cell_size
            
            sediment_entrainment[B] *= sediment_time_step_seconds

            # Find out if any of the cells are greater than the availiable amount in the cell
            C = (sediment_entrainment > GS_V)

            # If true only transport the maximum amount in the cell
            sediment_entrainment[C] = GS_V[C]
            
            sediment_entrainment[slope == -9999] = -9999 # Ensure no data cells remain no data
            
            return sediment_entrainment

        def move_sediment(depth_recking, sediment_entrainment_out, slope, flow_direction_np):
                        
            depth_mask = np.zeros_like(depth_recking, dtype = float)
            depth_threshold = 0.01

            # Get indices with great enough depth to intitate sediment transport
            # Check that the depth is great enough to intitate sediment transport in selected cells - might need changing though 
            # - this only gets the cells with great enough depth for sediment transport to occur and this will need to be recalcuclate for each timestep
            np.putmask(depth_mask, depth_recking >= depth_threshold, depth_recking)
      
            # Get the indices where the sediment transport is greater than 0 
            sort_idx = np.flatnonzero(depth_mask)

            # Now return those indices as a list
            new_idx = zip(*np.unravel_index(sort_idx[::-1], depth_recking.shape))

            # Get the rows and columns of the slope file
            nrows, ncols = slope.shape

            # Pads the array with zeros to prevent negative indexing
            tmp = np.zeros((nrows+2, ncols+2), dtype = float) 
            tmp[1:-1, 1:-1] = sediment_entrainment_out
            sediment_entrainment_out = tmp
            
            # Create empty array for the moved sediment
            sediment_entrainment_in = np.zeros_like(sediment_entrainment_out, dtype = float)
                       
            lookup = {32: (-1, -1), 
                      16: (0, -1), 
                      8:(1, -1), 
                      4:(1,  0),             
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
                sediment_entrainment_in[r + dr, c + dc] += sediment_entrainment_out[r, c] # move the sediment in the downstream direction by one timestep.
                           

            sediment_entrainment_in_fin = np.zeros_like(slope, dtype=float)
            sediment_entrainment_in_fin = sediment_entrainment_in[1:-1, 1:-1] 
            sediment_entrainment_in_fin[slope == -9999] = -9999
            
            return sediment_entrainment_in_fin
                        
        total_change = np.zeros_like(slope, dtype = float)

        counter_transport = 1
        total_time = 0.0
        layer_height = 0.2 # metres - need to convert to volume at some point
        
        #Add the first time_step onto the loop
        if sediment_time_step_seconds < 86400:
            total_time += sediment_time_step_seconds
        
        while total_time < 86400:
            arcpy.AddMessage("Time of day = " + str(total_time) + "s.")
           
            total_volume = np.zeros_like(slope, dtype = float)

            # Calculate the d50, d84, Fs for this timestep
            d50, d84, Fs, active_layer_GS_P = self.d50_d84_Fs_grain(GS_list, active_layer_GS_P_temp)

            # Calcualte the depth recking and index of active cells in this timestep
            depth_recking = self.depth_recking(Q_dis, slope, d84, cell_size)
            

            # Iterate through the grain sizes and proportions calculating the transport
            for GS, GS_P, GS_V_temp in izip(GS_list, active_layer_GS_P, active_layer_V_temp):
                                
                GS_V = np.load(GS_V_temp)
                arcpy.AddMessage("Loaded grain volume")                
                                               
                # Calculate sediment transport out for that grainsize              
                sediment_entrainment_out = sediment_entrainment_calculation(slope, depth_recking, Fs, d50, GS, GS_P, GS_V, cell_size, sediment_time_step_seconds)
                arcpy.AddMessage("Calculated sediment transport for " + "_" + str(GS))
                
           
                # Calculate sediment transport in for that grainsize
                sediment_entrainment_in = move_sediment(depth_recking, sediment_entrainment_out, slope, flow_direction_np)
                arcpy.AddMessage("Transported sediment for grain size " + "_" + str(GS))
                
                # Calculate the change in sediment volume
                new_grain_volume = GS_V - sediment_entrainment_out + sediment_entrainment_in               
                np.save(GS_V_temp, new_grain_volume)
                arcpy.AddMessage("Calculated sediment transport for grain size " + str(counter_transport))
                               
                # Update the total volume
                total_volume += new_grain_volume

                # Increase the grain counter by 1 until it reaches 7
                counter_transport +=1
                if counter_transport == 8:
                    counter_transport = 1

            # Collect garbage
            del d50, d84, Fs, depth_recking, sediment_entrainment_out, sediment_entrainment_in, new_grain_volume
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 

            # grain size volumes counter
            counter_proportion = 1

            for GS_P_temp, GS_V_temp in izip(active_layer_GS_P_temp, active_layer_V_temp):
                GS_V = np.load(GS_V_temp)                               
                GS_P = GS_V / total_volume
                
                

                arcpy.AddMessage("Calculated new proportion for grainsize " + str(counter_proportion)) 
                
                # Check for nodata and nan values.
                GS_P[total_volume == 0] = 0
                GS_P[slope == -9999] = -9999 
                np.save(GS_P_temp, GS_P) 
                                
                del GS_V, GS_P

                counter_proportion += 1
                if counter_proportion == 8:
                    counter_proportion = 1
                              
            # Collect garbage
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected))      
                
            total_volume[slope == -9999] = -9999   
             
              
                        
            active_layer, inactive_layer = active_inactive_layer_check.active_layer_depth(total_volume, inactive_layer, active_layer_GS_P_temp, active_layer_V_temp, 
                                                           inactive_layer_GS_P_temp, inactive_layer_V_temp, cell_size)
            

            # Increment the timestep ready for the next loop
            total_time += sediment_time_step_seconds

            ### Check if elevations need to be recalculated ###
            DTM, DTM_MINUS_AL_IAL, recalculate_slope_flow = elevation_adjustment.update_DTM_elevations(DTM, DTM_MINUS_AL_IAL, active_layer, inactive_layer, cell_size)
            
            inactive_layer *= (cell_size*cell_size)
            active_layer *= (cell_size*cell_size)

            
            # Collect garbage
            collected = gc.collect()
            arcpy.AddMessage("Garbage collector: collected %d objects." % (collected)) 

        ### SECTION TO CHECK IF MASS WASTING NEEDS TO TAKE PLACE ###
        
        DTM, DTM_MINUS_AL_IAL, recalculate_slope_flow, active_layer, inactive_layer = masswasting.masswasting_sediment().masswasting_loop(DTM, DTM_MINUS_AL_IAL, 
                                                                                                                                          active_layer, inactive_layer,
                                                                                                                                          bottom_left_corner, cell_size,
                                                                                                                                          flow_direction_np,
                                                                                                                                          active_layer_GS_P_temp,
                                                                                                                                          active_layer_V_temp,
                                                                                                                                          inactive_layer_GS_P_temp, 
                                                                                                                                          inactive_layer_V_temp)
        return inactive_layer, DTM, DTM_MINUS_AL_IAL, recalculate_slope_flow
                     
            ### Section to save rasters while testing model ###
            #rasterstonumpys.convert_numpy_to_raster_single(active_layer, "active_layer", bottom_left_corner, cell_size, "0")
            #rasterstonumpys.convert_numpy_to_raster_single(inactive_layer, "inactive_layer", bottom_left_corner, cell_size, "0")
        