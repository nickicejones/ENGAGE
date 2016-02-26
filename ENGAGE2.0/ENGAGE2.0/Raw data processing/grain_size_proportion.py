##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
import numpy as np
import grainsize_lookup
from arcpy.sa import *
import masswasting
from itertools import izip

# Calculate the distibution of the grainsizes across the catchment
def grain_size_calculation(soil_parent_material_50, DTM_clip_np, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_polygon, catch_extent, bottom_left_corner, Q50_exceedance):
    # 9 proportions of grainsizes that are listed below - defaults are listed on the right
    g_pro_1 = float(arcpy.GetParameterAsText(14)) #0.1
    g_pro_2 = float(arcpy.GetParameterAsText(15)) #0.35
    g_pro_3 = float(arcpy.GetParameterAsText(16)) #0.15
    g_pro_4 = float(arcpy.GetParameterAsText(17)) #0.15
    g_pro_5 = float(arcpy.GetParameterAsText(18)) #0.15
    g_pro_6 = float(arcpy.GetParameterAsText(19)) #0.05
    g_pro_7 = float(arcpy.GetParameterAsText(20)) #0.05
        
    # Create a list of the proportions
    grain_proportions = [g_pro_1, g_pro_2, g_pro_3, g_pro_4, g_pro_5, g_pro_6, g_pro_7]
    
    
    # Process the soil grain size data if provided so it is ready to go into the model
    if soil_parent_material_50 and soil_parent_material_50 != "#":
        # Check the soil parent type
        desc_soil_parent_material = arcpy.Describe(soil_parent_material_50)
        soil_raster_feature = desc_soil_parent_material.datasetType
        arcpy.AddMessage("The soil parent material is a " + soil_raster_feature)

        # process the soil parent material for entry into the model.
        if soil_raster_feature == 'FeatureClass':
   
            soil_parent_clip = arcpy.Clip_analysis(soil_parent_material_50, river_catchment_polygon)

            arcpy.AddField_management(soil_parent_clip, "MIN_NO", "SHORT")
            arcpy.AddField_management(soil_parent_clip, "MAX_NO", "SHORT")
            arcpy.AddField_management(soil_parent_clip, "DOM_NO", "SHORT")

            arcpy.AddMessage("Added new fields to the table")
            
            # Create update cursor for feature class 
            rows = arcpy.UpdateCursor(soil_parent_clip) 

            for row in rows:
                if row.MIN_GRAIN == "UNKN":
                    row.MIN_NO = 5

                elif row.MIN_GRAIN == "BOULDER":
                    row.MIN_NO = 4

                elif row.MIN_GRAIN == "GRAVEL" or row.MIN_GRAIN == "COARSE":
                    row.MIN_NO = 3

                elif row.MIN_GRAIN == "SAND" or row.MIN_GRAIN == "MEDIUM":
                    row.MIN_NO = 2

                elif row.MIN_GRAIN == "MUD" or row.MIN_GRAIN == "SILT" or row.MIN_GRAIN == "CLAY" or row.MIN_GRAIN == "FINE":
                    row.MIN_NO = 1
                
                if row.MAX_GRAIN == "UNKN":
                    row.MAX_NO = 5

                elif row.MAX_GRAIN == "BOULDER":
                    row.MAX_NO = 4

                elif row.MAX_GRAIN == "GRAVEL" or row.MAX_GRAIN == "COARSE":
                    row.MAX_NO = 3

                elif row.MAX_GRAIN == "SAND" or row.MAX_GRAIN == "MEDIUM":
                    row.MAX_NO = 2

                elif row.MAX_GRAIN == "MUD" or row.MAX_GRAIN == "SILT" or row.MAX_GRAIN == "CLAY" or row.MAX_GRAIN == "FINE":
                    row.MAX_NO = 1

                if row.DOM_GRAIN == "UNKN":
                    row.DOM_NO = 5

                elif row.DOM_GRAIN == "BOULDER":
                    row.DOM_NO = 4

                elif row.DOM_GRAIN == "GRAVEL" or row.DOM_GRAIN == "COARSE":
                    row.DOM_NO = 3

                elif row.DOM_GRAIN == "SAND" or row.DOM_GRAIN == "MEDIUM":
                    row.DOM_NO = 2

                elif row.DOM_GRAIN == "MUD" or row.DOM_GRAIN == "SILT" or row.DOM_GRAIN == "CLAY" or row.DOM_GRAIN == "FINE":
                    row.DOM_NO = 1
          
                else:
                    row.MIN_NO = 5
                    row.MAX_NO = 5
                    row.DOM_NO = 5

                rows.updateRow(row) 


            # Then the Min grainsize 
            soil_parent_material_min_grain = arcpy.FeatureToRaster_conversion(soil_parent_clip, "MIN_NO", "Temp9", DTM_cell_size)
            #soil_parent_material_min_grain_clip = arcpy.Clip_management(soil_parent_material_min_grain, catch_extent, "MODEL_MIN_GRAIN", river_catchment_polygon, "#","ClippingGeometry") 
            #soil_parent_material_min_grain_clip2 = arcpy.Clip_management(soil_parent_material_min_grain_clip, catch_extent, "MODEL_MIN_GRAIN2", river_catchment_polygon, "#","ClippingGeometry")  
            soil_parent_material_min_grain_clip = arcpy.gp.ExtractByMask_sa(soil_parent_material_min_grain, river_catchment_polygon, "MODEL_MIN_GRAIN")
            arcpy.AddMessage("Soil parent material min grain field converted to raster and clipped")

            # Then the Max grainsize
            soil_parent_material_max_grain = arcpy.FeatureToRaster_conversion(soil_parent_clip, "MAX_NO", "Temp10", DTM_cell_size)
            #soil_parent_material_max_grain_clip = arcpy.Clip_management(soil_parent_material_max_grain, catch_extent, "MODEL_MAX_GRAIN", river_catchment_polygon, "#","ClippingGeometry")  
            #soil_parent_material_min_grain_clip2 = arcpy.Clip_management(soil_parent_material_max_grain_clip, catch_extent, "MODEL_MAX_GRAIN2", river_catchment_polygon, "#","ClippingGeometry")
            soil_parent_material_max_grain_clip = arcpy.gp.ExtractByMask_sa(soil_parent_material_max_grain, river_catchment_polygon, "MODEL_MAX_GRAIN")
            arcpy.AddMessage("Soil parent material max grain field converted to raster and clipped")

            # Then the DOM grainsize
            soil_parent_material_dom_grain = arcpy.FeatureToRaster_conversion(soil_parent_clip, "DOM_NO", "Temp11", DTM_cell_size)
            #soil_parent_material_dom_grain_clip = arcpy.Clip_management(soil_parent_material_dom_grain, catch_extent, "MODEL_DOM_GRAIN", river_catchment_polygon, "#","ClippingGeometry")  
            #soil_parent_material_dom_grain_clip2 = arcpy.Clip_management(soil_parent_material_dom_grain_clip, catch_extent, "MODEL_DOM_GRAIN2", river_catchment_polygon, "#","ClippingGeometry")
            soil_parent_material_dom_grain_clip = arcpy.gp.ExtractByMask_sa(soil_parent_material_dom_grain, river_catchment_polygon, "MODEL_DOM_GRAIN")
            arcpy.AddMessage("Soil parent material dom grain field converted to raster and clipped")

        else:
            Soil_clip = arcpy.Clip_management(soil_parent_material, catch_extent, "soil_parent_material_Clip", river_catchment_polygon, "#","ClippingGeometry")

        # Convert the grainsizes to numpy arrays
        min_grain_size_np = arcpy.RasterToNumPyArray("MODEL_MIN_GRAIN", '#','#','#', -9999)
        max_grain_size_np = arcpy.RasterToNumPyArray("MODEL_MAX_GRAIN", '#','#','#', -9999)
        dom_grain_size_np = arcpy.RasterToNumPyArray("MODEL_DOM_GRAIN", '#','#','#', -9999)
        
        get_grain_proportions = grainsize_lookup.soil_depth_look7()

        grain_pro_1, grain_pro_2, grain_pro_3, grain_pro_4, grain_pro_5, grain_pro_6, grain_pro_7 = get_grain_proportions.get_grain_proportions(min_grain_size_np, max_grain_size_np, dom_grain_size_np)
                                
        hundred_array = np.zeros_like(min_grain_size_np, dtype = float)
        hundred_array[:] = 100

        # Create the float arrays for the different proportions using the 
        g_pro_1_float = np.zeros_like(min_grain_size_np, dtype = float) # Create a float array
        np.divide(grain_pro_1, hundred_array, g_pro_1_float) # divide the INT array by 100
        g_pro_1_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        np.around(g_pro_1_float, decimals = 3)
        g_pro_1_float_ras = arcpy.NumPyArrayToRaster(g_pro_1_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_1_float_ras.save("MODEL_GS1") # save the raster

        g_pro_2_float = np.zeros_like(grain_pro_2, dtype = float)
        np.divide(grain_pro_2, hundred_array, g_pro_2_float)
        g_pro_2_float[min_grain_size_np == -9999] = -9999
        np.around(g_pro_2_float, decimals = 3)
        g_pro_2_float_ras = arcpy.NumPyArrayToRaster(g_pro_2_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_2_float_ras.save("MODEL_GS2")

        g_pro_3_float = np.zeros_like(grain_pro_3, dtype = float) # Create a float array
        np.divide(grain_pro_3, hundred_array, g_pro_3_float) # divide the INT array by 100
        g_pro_3_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        np.around(g_pro_3_float, decimals = 3)
        g_pro_3_float_ras = arcpy.NumPyArrayToRaster(g_pro_3_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_3_float_ras.save("MODEL_GS3") # save the raster

        g_pro_4_float = np.zeros_like(grain_pro_4, dtype = float) # Create a float array
        np.divide(grain_pro_4, hundred_array, g_pro_4_float) # divide the INT array by 400
        g_pro_4_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        np.around(g_pro_4_float, decimals = 3)
        g_pro_4_float_ras = arcpy.NumPyArrayToRaster(g_pro_4_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_4_float_ras.save("MODEL_GS4") # save the raster

        g_pro_5_float = np.zeros_like(grain_pro_5, dtype = float) # Create a float array
        np.divide(grain_pro_5, hundred_array, g_pro_5_float) # divide the INT array by 500
        g_pro_5_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        np.around(g_pro_5_float, decimals = 3)
        g_pro_5_float_ras = arcpy.NumPyArrayToRaster(g_pro_5_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_5_float_ras.save("MODEL_GS5") # save the raster

        g_pro_6_float = np.zeros_like(grain_pro_6, dtype = float) # Create a float array
        np.divide(grain_pro_6, hundred_array, g_pro_6_float) # divide the INT array by 600
        g_pro_6_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        np.around(g_pro_6_float, decimals = 3)
        g_pro_6_float_ras = arcpy.NumPyArrayToRaster(g_pro_6_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_6_float_ras.save("MODEL_GS6") # save the raster

        g_pro_7_float = np.zeros_like(grain_pro_7, dtype = float) # Create a float array
        np.divide(grain_pro_7, hundred_array, g_pro_7_float) # divide the INT array by 700
        g_pro_7_float[min_grain_size_np == -9999] = -9999
        np.around(g_pro_7_float, decimals = 3) # confirm the nodata cells
        g_pro_7_float_ras = arcpy.NumPyArrayToRaster(g_pro_7_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_7_float_ras.save("MODEL_GS7") # save the raster

        #g_pro_8_float = np.zeros_like(grain_pro_8, dtype = float) # Create a float array
        #np.divide(grain_pro_8, hundred_array, g_pro_8_float) # divide the INT array by 800
        #g_pro_8_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        #g_pro_8_float_ras = arcpy.NumPyArrayToRaster(g_pro_8_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_8_float_ras.save("MODEL_GS8") # save the raster

        #g_pro_9_float = np.zeros_like(grain_pro_9, dtype = float) # Create a float array
        #np.divide(grain_pro_9, hundred_array, g_pro_9_float) # divide the INT array by 900
        #g_pro_9_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        #g_pro_9_float_ras = arcpy.NumPyArrayToRaster(g_pro_9_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_9_float_ras.save("MODEL_GS9") # save the raster

        #g_pro_10_float = np.zeros_like(grain_pro_10, dtype = float) # Create a float array
        #np.divide(grain_pro_10, hundred_array, g_pro_10_float) # divide the INT array by 1000
        #g_pro_10_float[min_grain_size_np == -9999] = -9999 # confirm the nodata cells
        #g_pro_10_float_ras = arcpy.NumPyArrayToRaster(g_pro_10_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_10_float_ras.save("MODEL_GS10") # save the raster
        grain_pro_array_list = [g_pro_1_float, g_pro_2_float, g_pro_3_float, g_pro_4_float, g_pro_5_float, g_pro_6_float, g_pro_7_float]

    # Grain size information
    else:
    
        arcpy.AddMessage("No spatially distributed information provided. Therefore uniform distributions will be created")
        
        total_pro = 0.0

        for grain_pro in grain_proportions:
        
            total_pro += grain_pro

        arcpy.AddMessage("The total of the proportions is " + str(total_pro))

        if total_pro != 1.0:
            raise Exception("The total of the proportions does not equal 1")

        # Drainage area threshold
        drainage_threshold = 0.5 # Could potentially add on as a scalable factor at the end

        # Convert the proportions to numpy arrays of the river catchment                       
        g_pro_1_array = np.empty_like(DTM_clip_np, dtype = float)
        g_pro_1_array[:] = g_pro_1
        g_pro_1_array[DTM_clip_np == -9999] = -9999
        g_pro_1_raster = arcpy.NumPyArrayToRaster(g_pro_1_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_1_raster.save("MODEL_GS1")

        g_pro_2_array = np.empty_like(DTM_clip_np, dtype = float) 
        g_pro_2_array[:] = g_pro_2
        g_pro_2_array[DTM_clip_np == -9999] = -9999
        g_pro_2_raster = arcpy.NumPyArrayToRaster(g_pro_2_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_2_raster.save("MODEL_GS2")
    
        g_pro_3_array = np.empty_like(DTM_clip_np, dtype = float) 
        g_pro_3_array[:] = g_pro_3
        g_pro_3_array[DTM_clip_np == -9999] = -9999
        g_pro_3_raster = arcpy.NumPyArrayToRaster(g_pro_3_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_3_raster.save("MODEL_GS3")
        
        g_pro_4_array = np.empty_like(DTM_clip_np, dtype = float) 
        g_pro_4_array[:] = g_pro_4
        g_pro_4_array[DTM_clip_np == -9999] = -9999
        g_pro_4_raster = arcpy.NumPyArrayToRaster(g_pro_4_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_4_raster.save("MODEL_GS4")

        g_pro_5_array = np.empty_like(DTM_clip_np, dtype = float) 
        g_pro_5_array[:] = g_pro_5
        g_pro_5_array[DTM_clip_np == -9999] = -9999
        g_pro_5_raster = arcpy.NumPyArrayToRaster(g_pro_5_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_5_raster.save("MODEL_GS5")
  
        g_pro_6_array = np.empty_like(DTM_clip_np, dtype = float) 
        g_pro_6_array[:] = g_pro_6
        g_pro_6_array[DTM_clip_np == -9999] = -9999
        g_pro_6_raster = arcpy.NumPyArrayToRaster(g_pro_6_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_6_raster.save("MODEL_GS6")
        
        g_pro_7_array = np.empty_like(DTM_clip_np, dtype = float) 
        g_pro_7_array[:] = g_pro_7
        g_pro_7_array[DTM_clip_np == -9999] = -9999
        g_pro_7_raster = arcpy.NumPyArrayToRaster(g_pro_7_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_7_raster.save("MODEL_GS7")
        
        #g_pro_8_array = np.empty_like(DTM_clip_np, dtype = float) 
        #g_pro_8_array[:] = g_pro_8
        #g_pro_8_array[DTM_clip_np == -9999] = -9999
        #g_pro_8_raster = arcpy.NumPyArrayToRaster(g_pro_8_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_8_raster.save("MODEL_GS8")
    
        #g_pro_9_array = np.empty_like(DTM_clip_np, dtype = float) 
        #g_pro_9_array[:] = g_pro_9
        #g_pro_9_array[DTM_clip_np == -9999] = -9999
        #g_pro_9_raster = arcpy.NumPyArrayToRaster(g_pro_9_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_9_raster.save("MODEL_GS9")
        
        #g_pro_10_array = np.empty_like(DTM_clip_np, dtype = float) 
        #g_pro_10_array[:] = g_pro_10
        #g_pro_10_array[DTM_clip_np == -9999] = -9999
        #g_pro_10_raster = arcpy.NumPyArrayToRaster(g_pro_10_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_10_raster.save("MODEL_GS10")
        grain_pro_array_list = [g_pro_1_array, g_pro_2_array, g_pro_3_array, g_pro_4_array, g_pro_5_array, g_pro_6_array, g_pro_7_array] 
        arcpy.AddMessage("Converted grain proportions to arrays")  
         
    if soil_parent_material_50 and soil_parent_material_50 != "#":   
        # Part 2 - checking the river cells as the flow conditions will not allow that type of sediment to build up in those cells
        # Need to check which cells contain soil and which should be river bedrock
        arcpy.AddMessage("Checking the river grain size proportions based on critcal shear stress")

        # Convert the DTM back to a raster for this part of the script
        DTM = arcpy.NumPyArrayToRaster(DTM_clip_np, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)

        # Do the various ArcGIS processing to calculate flow accumulation values
        filled_dtm = Fill(DTM)
        arcpy.AddMessage("Filled DTM")
        flow_directions = FlowDirection(filled_dtm)
        arcpy.AddMessage("Calculated flow directions")
        flow_accumulation = FlowAccumulation(flow_directions)
        arcpy.AddMessage("Accumulated flow")

        # Calculate the cell of highest flow accumulation
        max_flow_accumulation = arcpy.GetRasterProperties_management(flow_accumulation, "MAXIMUM")
        max_flow_accumulation = float(max_flow_accumulation.getOutput(0)) 
        arcpy.AddMessage("The max flow accumulation is " + str(max_flow_accumulation))

        # Calculate the discharge in each cell based on the discharge
        Q_50_exceedence_raster = (flow_accumulation / max_flow_accumulation) * float(Q50_exceedance)
        #Q_50_exceedence_raster.save("Q50_raster")
        Q_50_exceedence_np = arcpy.RasterToNumPyArray(Q_50_exceedence_raster, '#', '#', '#', -9999)
        arcpy.AddMessage("Discharge in each cell for 50% exceedence calculated")
   
        # Need to calculate slope (used in calculating depth)
        save_date = "1"
        slope = masswasting.masswasting_sediment().calculate_slope_fraction(filled_dtm, bottom_left_corner, DTM_cell_size, save_date)  
        slope[DTM_clip_np == -9999] = -9999
        slope_raster = arcpy.NumPyArrayToRaster(slope, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        slope_raster.save("Slope")
        arcpy.AddMessage("Slope calculated")
        
        # Calculate stream power for each cell in the raster
        stream_power = 1000 * 9.81 
        stream_power *= Q_50_exceedence_np
        stream_power *= slope
        stream_power /= DTM_cell_size
        stream_power[DTM_clip_np == -9999] = -9999
        stream_power_raster = arcpy.NumPyArrayToRaster(stream_power, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        stream_power_raster.save("stream_power")
        arcpy.AddMessage("Stream power calculated")

        # Calcate the minimum grainsize
        grain_size_minimum = stream_power / 6512.22545
        grain_size_minimum = np.power(grain_size_minimum, 2)
        grain_size_minimum = np.power(grain_size_minimum, 1./3.)
        grain_size_minimum[DTM_clip_np == -9999] = -9999
        grain_size_minimum_raster = arcpy.NumPyArrayToRaster(grain_size_minimum, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        grain_size_minimum_raster.save("grain_size_minimum")
        arcpy.AddMessage("Grain Size Minimum calculated")


        '''
        # 7 Grainsizes - for input into the model
        GS_1 = 0.0000156        # Clay - Grain size 1
        GS_2 = 0.000354         # Sand - Grain size 2 
        GS_3 = 0.004            # Fine Gravel - Grain size 3
        GS_4 = 0.0113           # Medium Gravel - Grain size 4
        GS_5 = 0.032            # Coarse Gravel - Grain size 5
        GS_6 = 0.128            # Cobble - Grain size 6
        GS_7 = 0.256            # Boulder - Grain size 7
        GS_list = [GS_1, GS_2, GS_3, GS_4, GS_5, GS_6, GS_7]
    
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


        
        # Get the d84 for calculating depth
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
        
        
        d84 = V_get_grain84(grain_pro_array_list)
        d84[DTM_clip_np == -9999] = -9999
        d84_raster = arcpy.NumPyArrayToRaster(d84, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        d84_raster.save("d84")
        arcpy.AddMessage("D84 calculated")

        # Calculate the recking parameter in order to work out the depth - it requires, slope, d84 and unit width discharge. - checked 04/07/14
        def depth_recking(Q_dis, slope, d84, cell_size):
                               
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
        
            depth_recking[DTM_clip_np == -9999] = -9999
                      
            return depth_recking

        # Calculate the depth recking
        depth_recking_np = depth_recking(Q_50_exceedence_np, slope, d84, DTM_cell_size)
        depth_recking_np[DTM_clip_np == -9999] = -9999
        depth_recking_raster = arcpy.NumPyArrayToRaster(depth_recking_np, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        depth_recking_raster.save("depth_recking")
        arcpy.AddMessage("Depth calculated")

        # Calculate shear stress
        # Create a series of empty arrays
        T = np.zeros_like(slope, dtype = float) 
           
        #Shear Stress
        T = slope * depth_recking_np                                  
        T *= 1000 * 9.81         
        T[DTM_clip_np == -9999] = -9999
        T_shear_stress = arcpy.NumPyArrayToRaster(T, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        T_shear_stress.save("T_shear_stress")

        # Assumung a shields parameter of 0.06 then to get the maximum particle that can be entrained in each cell given Q50
        T /= 971.19
        T[DTM_clip_np == -9999] = -9999
        max_sediment_D = arcpy.NumPyArrayToRaster(T, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        max_sediment_D.save("max_sediment_D")
        '''

        # Get the indices for the cells that sediment transport would be calculated
        Q_dis_mask = np.zeros_like(Q_50_exceedence_np, dtype = float)
           
        # Get indices with great enough discharge to intitate sediment transport
        Q_dis_threshold = 0.01

        # Check that the depth is great enough to intitate sediment transport in selected cells - might need changing though 
        # - this only gets the cells with great enough depth for sediment transport to occur and this will need to be recalcuclate for each timestep
        np.putmask(Q_dis_mask, Q_50_exceedence_np > Q_dis_threshold, Q_50_exceedence_np)
      
        # Get the indices where the sediment transport is greater than 0 
        sort_idx = np.flatnonzero(Q_dis_mask)

        # Now return those indices as a list
        new_idx = zip(*np.unravel_index(sort_idx[::-1], Q_50_exceedence_np.shape))

        for i, j in new_idx:
            for grain_proportion, grain_proportion_array in izip(grain_proportions, grain_pro_array_list):
                grain_proportion_array[i, j] = grain_proportion
   
        # Create the float arrays for the different proportions using the   
        g_pro_1_float_ras = arcpy.NumPyArrayToRaster(g_pro_1_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_1_float_ras.save("MODEL_GS1") # save the raster
   
        g_pro_2_float_ras = arcpy.NumPyArrayToRaster(g_pro_2_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_2_float_ras.save("MODEL_GS2")
    
        g_pro_3_float_ras = arcpy.NumPyArrayToRaster(g_pro_3_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_3_float_ras.save("MODEL_GS3") # save the raster
   
        g_pro_4_float_ras = arcpy.NumPyArrayToRaster(g_pro_4_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_4_float_ras.save("MODEL_GS4") # save the raster
 
        g_pro_5_float_ras = arcpy.NumPyArrayToRaster(g_pro_5_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_5_float_ras.save("MODEL_GS5") # save the raster
   
        g_pro_6_float_ras = arcpy.NumPyArrayToRaster(g_pro_6_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_6_float_ras.save("MODEL_GS6") # save the raster
   
        g_pro_7_float_ras = arcpy.NumPyArrayToRaster(g_pro_7_float, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_7_float_ras.save("MODEL_GS7") # save the 

        '''
        # Get the d84 for calculating depth
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
        
        
        d84 = V_get_grain84(grain_pro_array_list)
        d84[DTM_clip_np == -9999] = -9999
        d84_raster = arcpy.NumPyArrayToRaster(d84, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        d84_raster.save("d84")
        arcpy.AddMessage("D84 calculated")

        # Calculate the depth recking
        depth_recking_np = depth_recking(Q_50_exceedence_np, slope, d84, DTM_cell_size)
        depth_recking_np[DTM_clip_np == -9999] = -9999
        depth_recking_raster = arcpy.NumPyArrayToRaster(depth_recking_np, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        depth_recking_raster.save("depth_recking_2")
        arcpy.AddMessage("Depth calculated")

        # Calculate shear stress
        # Create a series of empty arrays
        T = np.zeros_like(slope, dtype = float) 
           
        #Shear Stress
        T = slope * depth_recking_np                                  
        T *= 1000 * 9.81         
        T[DTM_clip_np == -9999] = -9999
        T_shear_stress = arcpy.NumPyArrayToRaster(T, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        T_shear_stress.save("T_shear_stress_2")

        # Assumung a shields parameter of 0.06 then to get the maximum particle that can be entrained in each cell given Q50
        T /= 971.19
        T[DTM_clip_np == -9999] = -9999
        max_sediment_D = arcpy.NumPyArrayToRaster(T, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        max_sediment_D.save("max_sediment_D_2")
        '''

    arcpy.AddMessage("Grainsizes calculated")
    arcpy.AddMessage("-------------------------")