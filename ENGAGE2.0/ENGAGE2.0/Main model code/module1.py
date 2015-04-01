import numpy as np

# Create sample data
cell_size = 10
grain_proportion = np.array([[0.5, 0.5],
                          [0.1, 0.1],
                          [0, 0]])
grain_size = 0.02
slope = np.array([[0.5, 0.5],
                          [0.1, 0.1],
                          [0, 0]])
depth_recking = np.array([[0.5, 0.5],
                          [0.1, 0.1],
                          [0, 0]])
Fs = np.array([[0.5, 0.5],
                          [0.1, 0.1],
                          [0, 0]])
d50 = np.array([[0.5, 0.5],
                          [0.1, 0.1],
                          [0, 0]])   
 
   
def sediment_entrainment_calculation(slope, depth_recking, Fs, d50, grain_size, grain_proportion, cell_size):

    # Create a series of empty arrays
    sediment_entrainment = np.zeros_like(slope, dtype = float)     
    T = np.zeros_like(slope, dtype = float) 
    Trs50 = np.zeros_like(slope, dtype = float) 
    Tri = np.zeros_like(slope, dtype = float) 
    shear_vel = np.zeros_like(slope, dtype = float) 
    ToverTri = np.zeros_like(slope, dtype = float) 
    Wi = np.zeros_like(slope, dtype = float) 


    B = (depth_recking > 0)
    print B

    T[B] = 1000 * 9.81 * slope[B] * depth_recking[B]
    print T

    Trs50[B] = 1.65 * 1000 * 9.81 * d50[B]
    print Trs50

    Trs50[B] *= 0.021 + (0.015 * np.exp(-20 * Fs[B]))
    print Trs50

    Tri[B] =  grain_size / d50[B]
    print Tri

    Tri[B] **= 0.67 / (1 + np.exp(1.5 - (grain_size / d50[B])))
    print Tri

    Tri[B] *= Trs50[B]
    print Tri  

    shear_vel[B] = (T[B] / 1000)**0.5   
    print Tri         
    ToverTri[B] = T[B] / Tri[B]
    print ToverTri 
           
    C = B & (ToverTri < 1.35)
    print C
            
    Wi[C] = (ToverTri[C]**7.5)*0.002

    C = ~C & B

    Wi[C] = 14 * np.power(1 - (0.894 / np.power(ToverTri[C], 0.5)), 4.5)

    sediment_entrainment[B] = (Wi[B] * grain_proportion[B] * np.power(shear_vel[B], 3)) / ((2.65 - 1) * 9.81)

    # Convert sediment to width of channel by multiplying by the cell size
    sediment_entrainment[B] = sediment_entrainment[B] * cell_size

    sediment_entrainment[slope== -9999] = -9999  
    return sediment_entrainment 
   
   
sediment_entrainment = sediment_entrainment_calculation(slope, depth_recking, Fs, d50, grain_size, grain_proportion, cell_size)   
   
   
   
   
   
   
   
   
''' # I have 26 arrays

active_layer # An array

active_layer_volumes = [] # List of 7 arrays
active_layer_proportions = [] # List of 7 arrays
 
inactive_layer # Array

inactive_layer_volumes = [] # List of 7 arrays
inactive_layer_proportions = [] # List of 7 arrays

# Calculate the lower and upper limits for the volume of the active layer
al_upper_volume_limit = 5
al_lower_volume_limit = 1

# Count the grainsizes as the model works through them
grain_size_counter = 1    
         
# Set up some empty arrays to hold the new values 
new_active_layer_total = np.zeros_like(active_layer)
new_inactive_layer_total = np.zeros_like(inactive_layer)

for active_layer_proportion, active_layer_volume, inactive_layer_proportion, inactive_layer_volume in izip(active_layer_volumes, active_layer_proportions,inactive_layer_volumes, inactive_layer_proportions):
         
    for i, j in new_idx: # Iterate through the cells 
                                 
        if active_layer[i, j] >= al_upper_volume_limit: # check to see if the volume in that cell is greater than 5m3
            inactive_layer_volume[i, j] = (20 * active_layer_proportion[i, j]) + inactive_layer_volume[i, j] # add 20cm proportion of that grainsize to the active layer
            active_layer_volume[i, j] = (active_layer[i, j] - 20) * active_layer_proportion[i, j] 
        elif active_layer[i, j] < al_lower_volume_limit and inactive_layer[i, j] > 0: # check to see if the volume in that cell is greater than 5m3        
            active_layer_volume[i, j] = (20 * inactive_layer_proportion[i, j]) + active_layer_volume[i, j]                      
            inactive_layer_volume[i, j] = inactive_layer_volume[i, j] - (20 * inactive_layer_proportion[i, j])  
                              
    # Add the new calculated volumes to a running total array
    new_active_layer_total += active_layer_volume
    new_inactive_layer_total += inactive_layer_volume
                                      
    new_active_layer_total[active_layer == -9999] = -9999
    new_inactive_layer_total[inactive_layer == -9999] = -9999

for i, j in new_idx: # Iterate through the cells transporting sediment
                                 
            if active_layer[i, j] >= al_upper_volume_limit: # check to see if the volume in that cell is greater than 30m3
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

            elif active_layer[i, j] < al_lower_volume_limit and inactive_layer[i, j] > 0: # check to see if the volume in that cell is greater than 5m3
                arcpy.AddMessage(" ") 
                arcpy.AddMessage("The cell " + str(i) + " " + str(j) + " depth is " + str(active_layer[i, j]) + "m3 which is under " + str(al_lower_volume_limit) + " recalculating active layer depth....") 
                if inactive_layer_volume[i, j] >= 20:
                    # The volume of the grainsize left in the active layer is
                    arcpy.AddMessage("The previous volume of grain size " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))                 
                    active_layer_volume[i, j] = (20 * inactive_layer_proportion[i, j]) + active_layer_volume[i, j]                      
                    arcpy.AddMessage("The new volume of grain size " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))
                        
                    # take 20cm3 off the inactive volume and then work out the new proportions in the remaining soil volume
                    arcpy.AddMessage("Previous grainsize volume " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume[i, j])) 
                    inactive_layer_volume[i, j] = inactive_layer_volume[i, j] - (20 * inactive_layer_proportion[i, j]) 
                    arcpy.AddMessage("New grainsize volume " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume[i, j])) 
                        
                elif inactive_layer_volume[i, j] < 20:
                    # The volume of the grainsize left in the active layer is
                    arcpy.AddMessage("The previous volume of grain size " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))                 
                    active_layer_volume[i, j] = inactive_layer_volume[i, j] + active_layer_volume[i, j]                      
                    arcpy.AddMessage("The new volume of grain size " + str(grain_size_counter) + " in the active layer is " + str(active_layer_volume[i, j]))
                        
                    # reset the inactive volume and then work out the new proportions in the remaining soil volume
                    arcpy.AddMessage("Previous grainsize volume " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume[i, j])) 
                    inactive_layer_volume[i, j] = 0.0
                    arcpy.AddMessage("New grainsize volume " + str(grain_size_counter) + " in the inactive layer is " + str(inactive_layer_volume[i, j])) 
                                                  
                np.save(inactive_layer_volume_temp, inactive_layer_volume)
                np.save(active_layer_volume_temp, active_layer_volume)
                arcpy.AddMessage("Change to volume saved to disk")


                ### GET THE INDICES OF CELLS WITH CELLS GREATER THAN THE DEPTH THRESHOLD ###
    # Calculate the depth threshold
    depth_threshold = cell_size / 1000
    #depth_threshold = 0.0

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
    arcpy.AddMessage(" ") '''