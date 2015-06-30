##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
import numpy as np
from arcpy.sa import *

# Clip the land cover to the river catchment 
def land_cover_clip_analysis(land_cover, Land_cover_type, DTM_clip_np, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, natural_england_SPS, roads):

    # Check land cover type
    desc_land = arcpy.Describe(land_cover)
    land_raster_feature = desc_land.datasetType
    arcpy.AddMessage("The land cover is a " + land_raster_feature)

    # Check land cover cell size
    land_cell_size = desc_land.meanCellHeight
    arcpy.AddMessage("The land cover cell size is " + str(land_cell_size))

    if land_raster_feature == 'FeatureClass':
        land_cover_clip = arcpy.Clip_analysis(land_cover, buffer_catchment)
        arcpy.AddMessage("Land cover is a feature class")        
        land_cover_clip_raster = arcpy.FeatureToRaster_conversion(Land_cover_clip, "MODEL_Landcover_LCM", "Landcover", DTM_cell_size)
        arcpy.AddMessage("Land cover converted to raster")
        land_cover_clip_final = arcpy.Clip_management(land_cover, catch_extent, "MODEL_Landcover", river_catchment_BNG, "#","ClippingGeometry")

                
    else:
        # Carry clip the data using the correct type
        if land_cell_size != DTM_cell_size:
            arcpy.AddMessage("The cell size of the land cover you have provided is different to the DTM")

            land_cover_intial_clip = arcpy.Clip_management(land_cover, buffer_extent, "LCMSTAGE2", buffer_catchment, "#", "ClippingGeometry")
            land_cover_poly = arcpy.RasterToPolygon_conversion(land_cover_intial_clip, "LCMSTAGE1", "NO_SIMPLIFY", "VALUE")
            arcpy.AddMessage("Land cover converted to polygon")

            land_cover_clip = arcpy.Clip_analysis(land_cover_poly, river_catchment_BNG)
            arcpy.AddMessage("Land cover clipped to enlarged catchment")
            
            if Land_cover_type == "LCM 2007":
                land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover_clip, "grid_code", "LCMSTAGE3", DTM_cell_size)
                arcpy.AddMessage("Cell size of land cover converted to same as DTM")
                #land_cover_clip = arcpy.gp.ExtractByMask_sa(land_cover_raster, river_catchment_BNG, "MODEL_Landcover_LCM2") 
                land_cover_clip = arcpy.Clip_management(land_cover_raster, catch_extent, "MODEL_Landcover_LCM", river_catchment_BNG, "#", "ClippingGeometry")

                land_cover_shapefile = arcpy.RasterToPolygon_conversion(land_cover_clip, "MODEL_LCM_shapefile", "NO_SIMPLIFY")
                arcpy.AddMessage("Land cover converted to shapefile for editing")
                             
            elif Land_cover_type == "CORINE 2006": 
                land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover_clip, "grid_code", "LCMSTAGE3", DTM_cell_size)
                arcpy.AddMessage("Cell size of land cover converted to same as DTM")
                                      
                land_cover_clip = arcpy.gp.ExtractByMask_sa(land_cover_raster, river_catchment_BNG, "MODEL_Landcover_CORINE")

                land_cover_shapefile = arcpy.RasterToPolygon_conversion(land_cover_clip, "MODEL_CORINE_shapefile", "NO_SIMPLIFY")
                arcpy.AddMessage("Land cover converted to shapefile for editing")                        
        else:
            if Land_cover_type == "LCM 2007":

                land_cover_clip = arcpy.Clip_management(land_cover, catch_extent, "MODEL_Landcover_LCM", river_catchment_BNG, "#","ClippingGeometry")
                arcpy.AddMessage("Land cover clipped")

            elif Land_cover_type == "CORINE 2006":
                land_cover_clip = arcpy.Clip_management(land_cover, catch_extent, "MODEL_Landcover_CORINE", river_catchment_BNG, "#","ClippingGeometry")
                arcpy.AddMessage("Land cover clipped")
        
            
        if natural_england_SPS and natural_england_SPS != '#':

            # Check land cover type
            desc_land_SPS = arcpy.Describe(natural_england_SPS)
            land_SBS_raster_feature = desc_land_SPS.datasetType
            arcpy.AddMessage("The natural england land cover is a " + land_SBS_raster_feature)
            if land_SBS_raster_feature == 'FeatureClass':

                land_SBS_clip = arcpy.Clip_analysis(natural_england_SPS, buffer_catchment)
                       
                arcpy.AddField_management(land_SBS_clip, "SBS_CODE", "SHORT")
                arcpy.AddMessage("Added new fields to the table")
            
                # Create update cursor for feature class 
                rows = arcpy.UpdateCursor(land_SBS_clip) 

                for row in rows:
                    if row.USE_CD_YR == "PP4":
                        row.SBS_CODE = 24

                    elif row.USE_CD_YR == "PP3":
                        row.SBS_CODE = 25

                    elif row.USE_CD_YR == "PP1":
                        row.SBS_CODE = 26

                    elif row.USE_CD_YR == "TG3":
                        row.SBS_CODE = 27

                    elif row.USE_CD_YR == "TG2":
                        row.SBS_CODE = 28
                 
                    elif row.USE_CD_YR == "TG1":
                        row.SBS_CODE = 29
                        
                    elif row.USE_CD_YR == "PRO":
                        row.SBS_CODE = 0 # would be 30 phased out in 2011

                    elif row.USE_CD_YR == "NT7":
                        row.SBS_CODE = 31

                    elif row.USE_CD_YR == "NT5":
                        row.SBS_CODE = 32

                    elif row.USE_CD_YR == "NT6":
                        row.SBS_CODE = 33
                    
                    elif row.USE_CD_YR == "NT8":
                        row.SBS_CODE = 34

                    elif row.USE_CD_YR == "FL1":
                        row.SBS_CODE = 35

                    elif row.USE_CD_YR == "HM1":
                        row.SBS_CODE = 36

                    elif row.USE_CD_YR == "HO1":
                        row.SBS_CODE = 37

                    elif row.USE_CD_YR == "DF1":
                        row.SBS_CODE = 38
                      
                    elif row.USE_CD_YR == "SA2":
                        row.SBS_CODE = 39

                    elif row.USE_CD_YR == "FR1":
                        row.SBS_CODE = 40

                    elif row.USE_CD_YR == "FR3":
                        row.SBS_CODE = 41

                    elif row.USE_CD_YR == "FR4":
                        row.SBS_CODE = 42
                    
                    elif row.USE_CD_YR == "SA3":
                        row.SBS_CODE = 0 # would be 43

                    elif row.USE_CD_YR == "NA1":
                        row.SBS_CODE = 0 # would be 44

                    elif row.USE_CD_YR == "OT2":
                        row.SBS_CODE = 45

                    elif row.USE_CD_YR == "OT1":
                        row.SBS_CODE = 46

                    elif row.USE_CD_YR == "NE1":
                        row.SBS_CODE = 47

                    elif row.USE_CD_YR == "PC2":
                        row.SBS_CODE = 48
                    
                    elif row.USE_CD_YR == "AE1":
                        row.SBS_CODE = 0 # would be 49

                    else:
                        row.SBS_CODE = 0

                    rows.updateRow(row) 

                # Delete cursor and row objects to remove locks on the data 
                del row 
                del rows

                land_SBS_merge = arcpy.Merge_management([land_SBS_clip, river_catchment_BNG], "Temp1") 

                land_SBS_clip2 = arcpy.Clip_analysis(land_SBS_merge, river_catchment_BNG, "Clipped_SBS")

                land_SBS_raster = arcpy.FeatureToRaster_conversion(land_SBS_clip2, "SBS_CODE", "Temp2", DTM_cell_size)

                #land_SBS_raster_clip = arcpy.gp.ExtractByMask_sa(land_SBS_raster, river_catchment_BNG, "Model_NE_SBS1")
                land_SBS_raster_clip2 = arcpy.Clip_management(land_SBS_raster, catch_extent, "Model_NE_SBS", river_catchment_BNG, "#", "ClippingGeometry")

                #land_SBS_poly = arcpy.RasterToPolygon_conversion(land_SBS_raster, "LSBSSTAGE1", "NO_SIMPLIFY", "VALUE")
                #land_SBS_raster = arcpy.FeatureToRaster_conversion(land_SBS_poly, "gridcode", "Temp17", DTM_cell_size)
                #land_SBS_raster_clip3 = arcpy.gp.ExtractByMask_sa(land_SBS_raster, river_catchment_BNG, "Model_NE_SBS3")
                #land_SBS_raster_clip4 = arcpy.Clip_management(land_SBS_raster, catch_extent, "Model_NE_SBS4", river_catchment_BNG, "#", "ClippingGeometry")

                arcpy.AddMessage("Land cover converted to polygon")

            if roads and roads != '#':
                # Check land cover type
                desc_roads = arcpy.Describe(roads)
                roads_raster_feature = desc_roads.datasetType
                arcpy.AddMessage("The roads layer is a " + roads_raster_feature)
                if roads_raster_feature == 'FeatureClass':
                    roads_clip = arcpy.Clip_analysis(roads, buffer_catchment)
                        
                    arcpy.AddField_management(roads_clip, "ROAD_CODE", "SHORT")
                    arcpy.AddMessage("Added new fields to the table")
            
                    # Create update cursor for feature class 
                    rows = arcpy.UpdateCursor(roads_clip) 

                    for row in rows:
                        row.ROAD_CODE = 23

                        rows.updateRow(row) 

                    # Delete cursor and row objects to remove locks on the data 
                    del row 
                    del rows

                    roads_raster = arcpy.FeatureToRaster_conversion(roads_clip, "ROAD_CODE", "Temp3", 10)

                    roads_polygon = arcpy.RasterToPolygon_conversion(roads_raster, "MODEL_roads_polygon", "NO_SIMPLIFY", "#")

                    roads_merge = arcpy.Merge_management([roads_polygon, river_catchment_BNG], "Temp4") 

                    roads_clip2 = arcpy.Clip_analysis(roads_merge, river_catchment_BNG)

                    roads_raster = arcpy.FeatureToRaster_conversion(roads_clip2, "grid_code", "Temp5", DTM_cell_size)
                    
                    # Determine cell size of roads
                    desc_roads_raster_cell_size = arcpy.Describe(roads_raster)
                    roads_raster_cell_size = desc_roads_raster_cell_size.meanCellHeight

                    if roads_raster_cell_size != DTM_cell_size:
                        roads_raster = arcpy.Resample_management(roads_raster, "Temp6", DTM_cell_size,"NEAREST")
                    
                    # With road data
                    #roads_raster_clip = arcpy.gp.ExtractByMask_sa(roads_raster, river_catchment_BNG, "Model_ROADS1")
                    roads_raster_clip = arcpy.Clip_management(roads_raster, catch_extent, "Model_ROADS", river_catchment_BNG, "#", "ClippingGeometry")
                    natural_england_SPS_np = arcpy.RasterToNumPyArray("Model_NE_SBS", '#','#','#', -9999)
                    roads_np = arcpy.RasterToNumPyArray("Model_ROADS", '#','#','#', -9999)
                    LCM_np = arcpy.RasterToNumPyArray("MODEL_Landcover_LCM", '#','#','#', -9999)
             
                    roads_zero_np = np.zeros_like(DTM_clip_np, dtype = int) 
                    np.putmask(roads_zero_np, roads_np > 0, roads_np)

                    natural_england_zero_np = np.zeros_like(DTM_clip_np, dtype = int)
                    np.putmask(natural_england_zero_np, natural_england_SPS_np  > 0, natural_england_SPS_np)
                    natural_england_zero_np[DTM_clip_np == -9999] = -9999 
                     
                    combined_land_cover = np.zeros_like(roads_np, dtype = int) 
                    combined_land_cover[DTM_clip_np == -9999] = -9999
            
                    np.putmask(combined_land_cover, combined_land_cover >= 0, natural_england_zero_np) 
                    np.putmask(combined_land_cover, roads_zero_np > 0, roads_zero_np)
                    np.putmask(combined_land_cover, combined_land_cover == 0, LCM_np)

                    combined_land_cover_ras = arcpy.NumPyArrayToRaster(combined_land_cover, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
                    combined_land_cover_ras.save("MODEL_COMBINE_LC")

                    # Delete the LCM data as no longer needed
                    #if arcpy.Exists("MODEL_Landcover_LCM"):
                        #arcpy.Delete_management("MODEL_Landcover_LCM")
                    

            else:
                # No Road Data
                natural_england_SPS_np = arcpy.RasterToNumPyArray("Model_NE_SBS", '#','#','#', -9999)
                LCM_np = arcpy.RasterToNumPyArray("MODEL_Landcover_LCM", '#','#','#', -9999)

                natural_england_zero_np = np.zeros_like(DTM_clip_np, dtype = int)
                np.putmask(natural_england_zero_np, natural_england_SPS_np  > 0, natural_england_SPS_np)
                natural_england_zero_np[DTM_clip_np == -9999] = -9999 
                     
                combined_land_cover = np.zeros_like(DTM_clip_np, dtype = int) 
                combined_land_cover[DTM_clip_np == -9999] = -9999
            
                np.putmask(combined_land_cover, combined_land_cover >= 0, natural_england_zero_np) 
                np.putmask(combined_land_cover, combined_land_cover == 0, LCM_np)

                combined_land_cover_ras = arcpy.NumPyArrayToRaster(combined_land_cover, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
                combined_land_cover_ras.save("MODEL_COMBINE_LC")

                # Delete the LCM data as no longer needed
                if arcpy.Exists("MODEL_Landcover_LCM"):
                   arcpy.Delete_management("MODEL_Landcover_LCM")
            
    arcpy.AddMessage("Land cover clipped to catchment")
    arcpy.AddMessage("-------------------------")