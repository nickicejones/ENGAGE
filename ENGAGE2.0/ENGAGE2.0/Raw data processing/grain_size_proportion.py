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

# Calculate the distibution of the grainsizes across the catchment
def grain_size_calculation(soil_parent_material_50, DTM_clip_np, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_polygon, catch_extent, bottom_left_corner):
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

    # Grain size information
    else:
    
        arcpy.AddMessage("No spatially distributed information provided. Therefore uniform distributions will be created")
        # 9 proportions of grainsizes that are listed below - defaults are listed on the right
        g_pro_1 = float(arcpy.GetParameterAsText(13)) #0.1
        g_pro_2 = float(arcpy.GetParameterAsText(14)) #0.35
        g_pro_3 = float(arcpy.GetParameterAsText(15)) #0.15
        g_pro_4 = float(arcpy.GetParameterAsText(16)) #0.15
        g_pro_5 = float(arcpy.GetParameterAsText(17)) #0.15
        g_pro_6 = float(arcpy.GetParameterAsText(18)) #0.05
        g_pro_7 = float(arcpy.GetParameterAsText(19)) #0.05
        
        # Create a list of the proportions
        grain_proportions = [g_pro_1, g_pro_2, g_pro_3, g_pro_4, g_pro_5, g_pro_6, g_pro_7]
        total_pro = 0.0

        for grain_pro in grain_proportions:
        
            total_pro += grain_pro

        arcpy.AddMessage("The total of the proportions is " + str(total_pro))

        if total_pro != 1.0:
            raise Exception("The total of the proportions does not equal 1")

        # Drainage area threshold
        drainage_threshold = 0.5 # Could potentially add on as a scalable factor at the end

        # Convert the proportions to numpy arrays of the river catchment

        grain_pro_array_list = [] 
        
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

        arcpy.AddMessage("Converted grain proportions to arrays")      

    arcpy.AddMessage("Grainsizes calculated")
    arcpy.AddMessage("-------------------------")