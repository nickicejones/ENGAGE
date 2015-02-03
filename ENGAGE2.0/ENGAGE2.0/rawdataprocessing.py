# Import Required Modules
import arcpy
import numpy as np
import grainsize_lookup
from arcpy.sa import *

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Check out extensions
arcpy.CheckOutExtension("Spatial")

# Get input parameters
# set environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Users will have to provide a rivere catchment boundry 
river_catchment = arcpy.GetParameterAsText(1)

# Digital Terrain Model
DTM = arcpy.GetParameterAsText(2)

# Land Cover Data
Land_cover_type = arcpy.GetParameterAsText(3)
land_cover = arcpy.GetParameterAsText(4)
natural_england_SPS = arcpy.GetParameterAsText(5) # optional
roads = arcpy.GetParameterAsText(6) # optional

# Soil Data
Soil_type = arcpy.GetParameterAsText(7)
soil = arcpy.GetParameterAsText(8)

# Soil grain size Data
soil_parent_material_50 = arcpy.GetParameterAsText(9) # shapefile of UK coverage

# Soil depth Data
# Uk soil parent material 
advanced_superficial_deposit = arcpy.GetParameterAsText(10) # raster of superficial deposit depth
soil_parent_material_1 = arcpy.GetParameterAsText(11) 

# Calculate some stats for the DTM
# Fill the raster
DTM_fill = Fill(DTM)
arcpy.AddMessage("Filled digital terrain model")
arcpy.AddMessage("-----------------------")
arcpy.SetProgressorPosition(5)

# Calculate the flow direction of the DTM
DTM_flow_direction = FlowDirection(DTM_fill)
arcpy.AddMessage("Calculated flow direction")
arcpy.AddMessage("-----------------------")

def catchment_correction(river_catchment, cell_size):
 
    river_catchment_raster = arcpy.FeatureToRaster_conversion(river_catchment, "OBJECTID", "MODEL_river_catchment_ras", cell_size)
    river_catchment_polygon = arcpy.RasterToPolygon_conversion(river_catchment_raster, "MODEL_river_catchment_poly", "NO_SIMPLIFY", "#")

    lst = arcpy.ListFields(river_catchment_polygon)

    SBS_exists = 'false'
    GRID_exists = 'false'

    for f in lst:        
        if f.name == "SBS_CODE":
            SBS_exists = 'true'
            arcpy.AddMessage("SBS_CODE exists")
        elif f.name == "grid_code":
            GRID_exists = 'true'
            arcpy.AddMessage("grid_code exists")

    if SBS_exists == 'false':
        arcpy.AddField_management(river_catchment_polygon, "SBS_CODE", "SHORT")
        arcpy.AddMessage("added SBS_CODE")
    if GRID_exists == 'false':    
        arcpy.AddField_management(river_catchment_polygon, "grid_code", "SHORT")
        arcpy.AddMessage("added grid_code")

            
    # Create update cursor for feature class 
    rows = arcpy.UpdateCursor(river_catchment_polygon) 

    for row in rows:
        row.SBS_CODE = 0
        row.grid_code = 0

        rows.updateRow(row)
        
    # Delete cursor and row objects to remove locks on the data 
    del row 
    del rows 
    arcpy.AddMessage("-------------------------")
    return river_catchment_polygon

# Check if the pour point needs snapping and calculate the river catchment.
river_catchment_polygon = catchment_correction(river_catchment, cell_size)

# Check if user is using FAO or Corine
if Soil_type == 'FAO':
    BNG = 'true'
if Land_cover_type == 'CORINE 2006':
    BNG = 'true'
else:
    BNG = 'false'

# Check if the user is working in British National Grid
def convert_BNG(BNG, DTM_fill, soil, land_cover, river_catchment_polygon):

    if BNG == 'true':
        # Define the projection of the shapefiles
        
        # Check the soil type
        desc_soil = arcpy.Describe(soil)
        soil_type = desc_soil.datasetType

        # Check the land cover type
        desc_land = arcpy.Describe(land_cover)
        land_type = desc_land.datasetType

         # River Catchemnt Projection    
        river_catchment_BNG = arcpy.Project_management(river_catchment_polygon, "catchment_BNG", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
        arcpy.AddMessage("River catchment" + " is now in British National Grid projection")
        DTM_BNG = arcpy.ProjectRaster_management(DTM_fill, "DTM_BNG","PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]","NEAREST", '#',"#","#","PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
        arcpy.AddMessage("DTM" + " is now in British National Grid projection")

        if soil_type == 'FeatureClass':
            soil_BNG = arcpy.Project_management(soil, "soil_BNG", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
            arcpy.AddMessage("Soil" + " is now in British National Grid projection")

        else: 
            soil_BNG = arcpy.ProjectRaster_management(soil, "soil_BNG","PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]","NEAREST", '#',"#","#","PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
            arcpy.AddMessage("Soil" + " is now in British National Grid projection")

        if land_type =='FeatureClass':
            land_cover_BNG = arcpy.Project_management(land_cover, "land_BNG", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
            arcpy.AddMessage("Land cover" + " is now in British National Grid projection")

        else:
            land_cover_BNG = arcpy.ProjectRaster_management(land_cover, "land_BNG","PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]","NEAREST", '#',"#","#","PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
            arcpy.AddMessage("Land cover" + " is now in British National Grid projection")
            
    else:
        DTM_BNG = DTM_fill
        soil_BNG = soil
        land_cover_BNG = land_cover
        river_catchment_BNG = river_catchment_polygon
             
    return DTM_BNG, soil_BNG, land_cover_BNG, river_catchment_BNG
DTM_BNG, soil_BNG, land_cover_BNG, river_catchment_BNG = convert_BNG(BNG, DTM_fill, soil, land_cover, river_catchment_polygon)
arcpy.AddMessage("Projection set for all files")
arcpy.AddMessage("-------------------------")

def extents(fc):
    extent = arcpy.Describe(fc).extent
    west = round(extent.XMin) 
    south = round(extent.YMin) 
    east = round(extent.XMax)
    north = round(extent.YMax) 
    return west, south, east, north

# Obtain extents of two shapes
XMin, YMin, XMax, YMax = extents(river_catchment_BNG)

# Set the extent environment
arcpy.AddMessage("The catchment extent is " + "%s %s %s %s" % (XMin, YMin, XMax, YMax))

catch_extent = "%s %s %s %s" % (XMin, YMin, XMax, YMax)

# Clip the DTM
DTM_Clip = arcpy.Clip_management(DTM_BNG, catch_extent, "MODEL_DTM", river_catchment_BNG, "#", "ClippingGeometry")
#DTM_Clip1 = arcpy.gp.ExtractByMask_sa(DTM_Clip, river_catchment_BNG, "MODEL_DTM1")
arcpy.AddMessage("Digital Terrain Model (DTM) clipped to catchment")
arcpy.AddMessage("-------------------------")

# Convert DTM to np array
DTM_Clip_np = arcpy.RasterToNumPyArray("MODEL_DTM", '#','#','#', -9999)

# Find the characteristics of the DTM
# Determine cell size
desc_DTM = arcpy.Describe(DTM_Clip)
DTM_cell_size = desc_DTM.meanCellHeight
arcpy.AddMessage("The model is working on a cell size of " + str(DTM_cell_size) + " metres.")
DTM_extent = desc_DTM.Extent

# Turns the corner into a point
bottom_left_corner = arcpy.Point(DTM_extent.XMin, DTM_extent.YMin)

# Buffer the catchment
buffer_catchment = arcpy.Buffer_analysis(river_catchment_BNG, "river_buffer", "2500")
# Describe to find characteristics of buffer clip area

# Obtain extents of two shapes
XMin, YMin, XMax, YMax = extents(buffer_catchment)

# Set the extent environment
arcpy.AddMessage("The catchment buffer extent is " + "%s %s %s %s" % (XMin, YMin, XMax, YMax))

buffer_extent = "%s %s %s %s" % (XMin, YMin, XMax, YMax)

# Clip the land cover to the river catchment 
def land_cover_clip_analysis(land_cover, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_polygon, catch_extent, natural_england_SPS, roads):

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
        land_cover_clip_final = arcpy.Clip_management(land_cover, catch_extent, "MODEL_Landcover", river_catchment_polygon, "#","ClippingGeometry")
                
    else:
        # Carry clip the data using the correct type
        if land_cell_size != DTM_cell_size:
            arcpy.AddMessage("The cell size of the land cover you have provided is different to the DTM")

            land_cover_intial_clip = arcpy.Clip_management(land_cover, buffer_extent, "LCMSTAGE2", buffer_catchment, "#", "ClippingGeometry")
            land_cover_poly = arcpy.RasterToPolygon_conversion(land_cover_intial_clip, "LCMSTAGE1", "NO_SIMPLIFY", "VALUE")
            arcpy.AddMessage("Land cover converted to polygon")

            land_cover_clip = arcpy.Clip_analysis(land_cover_poly, river_catchment_polygon)
            arcpy.AddMessage("Land cover clipped to enlarged catchment")
            
            if Land_cover_type == "LCM 2007":
                land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover_clip, "grid_code", "LCMSTAGE3", DTM_cell_size)
                arcpy.AddMessage("Cell size of land cover converted to same as DTM")
                #land_cover_clip = arcpy.gp.ExtractByMask_sa(land_cover_raster, river_catchment_polygon, "MODEL_Landcover_LCM2") 
                land_cover_clip = arcpy.Clip_management(land_cover_raster, catch_extent, "MODEL_Landcover_LCM", river_catchment_polygon, "#", "ClippingGeometry")
                              

            elif Land_cover_type == "CORINE 2006": 
                land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover_clip, "grid_code", "LCMSTAGE3", DTM_cell_size)
                arcpy.AddMessage("Cell size of land cover converted to same as DTM")
                                      
                land_cover_clip = arcpy.gp.ExtractByMask_sa(land_cover_raster, river_catchment_polygon, "MODEL_Landcover_CORINE")
                         
        else:
            land_cover_clip = arcpy.Clip_management(land_cover, catch_extent, "MODEL_Landcover", river_catchment_polygon, "#","ClippingGeometry")
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

                land_SBS_merge = arcpy.Merge_management([land_SBS_clip, river_catchment_polygon], "Temp1") 

                land_SBS_clip2 = arcpy.Clip_analysis(land_SBS_merge, river_catchment_polygon, "Clipped_SBS")

                land_SBS_raster = arcpy.FeatureToRaster_conversion(land_SBS_clip2, "SBS_CODE", "Temp2", DTM_cell_size)

                #land_SBS_raster_clip = arcpy.gp.ExtractByMask_sa(land_SBS_raster, river_catchment_polygon, "Model_NE_SBS1")
                land_SBS_raster_clip2 = arcpy.Clip_management(land_SBS_raster, catch_extent, "Model_NE_SBS", river_catchment_polygon, "#", "ClippingGeometry")

                #land_SBS_poly = arcpy.RasterToPolygon_conversion(land_SBS_raster, "LSBSSTAGE1", "NO_SIMPLIFY", "VALUE")
                #land_SBS_raster = arcpy.FeatureToRaster_conversion(land_SBS_poly, "gridcode", "Temp17", DTM_cell_size)
                #land_SBS_raster_clip3 = arcpy.gp.ExtractByMask_sa(land_SBS_raster, river_catchment_polygon, "Model_NE_SBS3")
                #land_SBS_raster_clip4 = arcpy.Clip_management(land_SBS_raster, catch_extent, "Model_NE_SBS4", river_catchment_polygon, "#", "ClippingGeometry")

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

                    roads_merge = arcpy.Merge_management([roads_polygon, river_catchment_polygon], "Temp4") 

                    roads_clip2 = arcpy.Clip_analysis(roads_merge, river_catchment_polygon)

                    roads_raster = arcpy.FeatureToRaster_conversion(roads_clip2, "grid_code", "Temp5", DTM_cell_size)
                    
                    # Determine cell size of roads
                    desc_roads_raster_cell_size = arcpy.Describe(roads_raster)
                    roads_raster_cell_size = desc_roads_raster_cell_size.meanCellHeight

                    if roads_raster_cell_size != DTM_cell_size:
                        roads_raster = arcpy.Resample_management(roads_raster, "Temp6", DTM_cell_size,"NEAREST")
                    
                    # With road data
                    #roads_raster_clip = arcpy.gp.ExtractByMask_sa(roads_raster, river_catchment_polygon, "Model_ROADS1")
                    roads_raster_clip = arcpy.Clip_management(roads_raster, catch_extent, "Model_ROADS", river_catchment_polygon, "#", "ClippingGeometry")
                    natural_england_SPS_np = arcpy.RasterToNumPyArray("Model_NE_SBS", '#','#','#', -9999)
                    roads_np = arcpy.RasterToNumPyArray("Model_ROADS", '#','#','#', -9999)
                    LCM_np = arcpy.RasterToNumPyArray("MODEL_Landcover_LCM", '#','#','#', -9999)
             
                    roads_zero_np = np.zeros_like(DTM_Clip_np, dtype = float) 
                    np.putmask(roads_zero_np, roads_np > 0, roads_np)

                    natural_england_zero_np = np.zeros_like(DTM_Clip_np, dtype = float)
                    np.putmask(natural_england_zero_np, natural_england_SPS_np  > 0, natural_england_SPS_np)
                    natural_england_zero_np[DTM_Clip_np == -9999] = -9999 
                     
                    combined_land_cover = np.zeros_like(roads_np, dtype = float) 
                    combined_land_cover[DTM_Clip_np == -9999] = -9999
            
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

                natural_england_zero_np = np.zeros_like(DTM_Clip_np)
                np.putmask(natural_england_zero_np, natural_england_SPS_np  > 0, natural_england_SPS_np)
                natural_england_zero_np[DTM_Clip_np == -9999] = -9999 
                     
                combined_land_cover = np.zeros_like(DTM_Clip_np) 
                combined_land_cover[DTM_Clip_np == -9999] = -9999
            
                np.putmask(combined_land_cover, combined_land_cover >= 0, natural_england_zero_np) 
                np.putmask(combined_land_cover, combined_land_cover == 0, LCM_np)

                combined_land_cover_ras = arcpy.NumPyArrayToRaster(combined_land_cover, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
                combined_land_cover_ras.save("MODEL_COMBINE_LC")

                # Delete the LCM data as no longer needed
                if arcpy.Exists("MODEL_Landcover_LCM"):
                   arcpy.Delete_management("MODEL_Landcover_LCM")
        
                                
land_cover_clipped = land_cover_clip_analysis(land_cover_BNG, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent, natural_england_SPS, roads)
arcpy.AddMessage("Land cover clipped to catchment")
arcpy.AddMessage("-------------------------")
arcpy.SetProgressorPosition(50)


# Clip the soil hydrology to the river catchment
def soil_clip_analysis(soil, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent):
    # Check the soil type
    desc_soil = arcpy.Describe(soil)
    soil_raster_feature = desc_soil.datasetType
    arcpy.AddMessage("The soil is a " + soil_raster_feature)

    if soil_raster_feature == 'FeatureClass':

        soil_clip = arcpy.Clip_analysis(soil, river_catchment_BNG)
   
        if Soil_type == 'UK HOST':
            arcpy.AddMessage("UK HOST soil data selected")
            soil_clipped = arcpy.FeatureToRaster_conversion(soil_clip, "HOST", "Temp7", DTM_cell_size)          
            soil_clip_raster = arcpy.Clip_management(soil_clipped, catch_extent, "MODEL_Soil_HOST", river_catchment_BNG, "#", "ClippingGeometry")
            #soil_clip_raster = arcpy.gp.ExtractByMask_sa(soil_clipped, river_catchment_BNG, "MODEL_Soil_HOST")

        elif Soil_type == 'FAO':
            arcpy.AddMessage("FAO soil data selected")

            soil_BNG = arcpy.Project_management(soil_clip, "soil_BNG", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
            arcpy.AddMessage("Soil" + " is now in British National Grid projection")

            soil_clipped = arcpy.FeatureToRaster_conversion(soil_BNG, "SNUM", "Temp8", DTM_cell_size)
            soil_clip_raster = arcpy.gp.ExtractByMask_sa(soil_clipped, river_catchment_polygon, "MODEL_Soil_FAO")
            #soil_clip_raster = arcpy.Clip_management(Soil_clip, extent, "MODEL_Soil_FAO", River_catchment_poly, "#", "ClippingGeometry")
            
    else:
        Soil_clip = arcpy.Clip_management(soil, catch_extent, "MODEL_Soil", river_catchment_polygon, "#","ClippingGeometry")
        arcpy.AddMessage("-------------------------")          
soil_clipped = soil_clip_analysis(soil_BNG, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent)
arcpy.AddMessage("Soil clipped to catchment")
arcpy.AddMessage("-------------------------")


# Calculate the distibution of the grainsizes across the catchment
def grain_size_calculation(soil_parent_material_50, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_polygon, catch_extent):
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
            '''
'''
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
        # 9 proportions of grainsizes that are listed below
        g_pro_1 = float(arcpy.GetParameterAsText(12)) #0.1
        g_pro_2 = float(arcpy.GetParameterAsText(13)) #0.35
        g_pro_3 = float(arcpy.GetParameterAsText(14)) #0.15
        g_pro_4 = float(arcpy.GetParameterAsText(15)) #0.15
        g_pro_5 = float(arcpy.GetParameterAsText(16)) #0.15
        g_pro_6 = float(arcpy.GetParameterAsText(17)) #0.05
        g_pro_7 = float(arcpy.GetParameterAsText(18)) #0.05
        
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
        
        g_pro_1_array = np.empty_like(DTM_Clip_np, dtype = float)
        g_pro_1_array[:] = g_pro_1
        g_pro_1_array[DTM_Clip_np == -9999] = -9999
        g_pro_1_raster = arcpy.NumPyArrayToRaster(g_pro_1_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_1_raster.save("MODEL_GS1")

        g_pro_2_array = np.empty_like(DTM_Clip_np, dtype = float) 
        g_pro_2_array[:] = g_pro_2
        g_pro_2_array[DTM_Clip_np == -9999] = -9999
        g_pro_2_raster = arcpy.NumPyArrayToRaster(g_pro_2_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_2_raster.save("MODEL_GS2")
    
        g_pro_3_array = np.empty_like(DTM_Clip_np, dtype = float) 
        g_pro_3_array[:] = g_pro_3
        g_pro_3_array[DTM_Clip_np == -9999] = -9999
        g_pro_3_raster = arcpy.NumPyArrayToRaster(g_pro_3_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_3_raster.save("MODEL_GS3")
        
        g_pro_4_array = np.empty_like(DTM_Clip_np, dtype = float) 
        g_pro_4_array[:] = g_pro_4
        g_pro_4_array[DTM_Clip_np == -9999] = -9999
        g_pro_4_raster = arcpy.NumPyArrayToRaster(g_pro_4_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_4_raster.save("MODEL_GS4")

        g_pro_5_array = np.empty_like(DTM_Clip_np, dtype = float) 
        g_pro_5_array[:] = g_pro_5
        g_pro_5_array[DTM_Clip_np == -9999] = -9999
        g_pro_5_raster = arcpy.NumPyArrayToRaster(g_pro_5_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_5_raster.save("MODEL_GS5")
  
        g_pro_6_array = np.empty_like(DTM_Clip_np, dtype = float) 
        g_pro_6_array[:] = g_pro_6
        g_pro_6_array[DTM_Clip_np == -9999] = -9999
        g_pro_6_raster = arcpy.NumPyArrayToRaster(g_pro_6_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_6_raster.save("MODEL_GS6")
        
        g_pro_7_array = np.empty_like(DTM_Clip_np, dtype = float) 
        g_pro_7_array[:] = g_pro_7
        g_pro_7_array[DTM_Clip_np == -9999] = -9999
        g_pro_7_raster = arcpy.NumPyArrayToRaster(g_pro_7_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        g_pro_7_raster.save("MODEL_GS7")
        
        #g_pro_8_array = np.empty_like(DTM_Clip_np, dtype = float) 
        #g_pro_8_array[:] = g_pro_8
        #g_pro_8_array[DTM_Clip_np == -9999] = -9999
        #g_pro_8_raster = arcpy.NumPyArrayToRaster(g_pro_8_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_8_raster.save("MODEL_GS8")
    
        #g_pro_9_array = np.empty_like(DTM_Clip_np, dtype = float) 
        #g_pro_9_array[:] = g_pro_9
        #g_pro_9_array[DTM_Clip_np == -9999] = -9999
        #g_pro_9_raster = arcpy.NumPyArrayToRaster(g_pro_9_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_9_raster.save("MODEL_GS9")
        
        #g_pro_10_array = np.empty_like(DTM_Clip_np, dtype = float) 
        #g_pro_10_array[:] = g_pro_10
        #g_pro_10_array[DTM_Clip_np == -9999] = -9999
        #g_pro_10_raster = arcpy.NumPyArrayToRaster(g_pro_10_array, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        #g_pro_10_raster.save("MODEL_GS10")

        arcpy.AddMessage("Converted grain proportions to arrays")      
soil_grain_calculation = grain_size_calculation(soil_parent_material_50, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent)
arcpy.AddMessage("Grainsizes calculated")
arcpy.AddMessage("-------------------------")
arcpy.SetProgressorPosition(80)

# Calculate the depth of soil in the river and on the hillslopes
def soil_depth_calc(soil_parent_material_1, advanced_superficial_deposit, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent):

    if soil_parent_material_1 and soil_parent_material_1 != '#':
        # Check the soil parent type
        desc_soil_depth = arcpy.Describe(soil_parent_material_1)
        soil_depth_raster_feature = desc_soil_depth.datasetType
        arcpy.AddMessage("The soil depth dataset is a " + soil_depth_raster_feature)

        # process the soil parent material for entry into the model.

        if soil_depth_raster_feature == 'FeatureClass':
            
            soil_parent_material_1_clip = arcpy.Clip_analysis(soil_parent_material_1, river_catchment_polygon)
                        
            arcpy.AddField_management(soil_parent_material_1_clip, "R_DEPTH", "FLOAT")

            arcpy.AddMessage("Added new fields to the table")
            
            # Create update cursor for feature class 
            rows = arcpy.UpdateCursor(soil_parent_material_1_clip) 

            for row in rows:
                if row.SOIL_DEPTH == "DEEP":
                    row.R_DEPTH = 2.0

                elif row.SOIL_DEPTH == "DEEP-INTERMEDIATE":
                    row.R_DEPTH = 1.5

                elif row.SOIL_DEPTH == "INTERMEDIATE":
                    row.R_DEPTH = 1.0

                elif row.SOIL_DEPTH == "INTERMEDIATE-SHALLOW":
                    row.R_DEPTH = 0.5

                elif row.SOIL_DEPTH == "SHALLOW":
                    row.R_DEPTH = 0.25

                elif row.SOIL_DEPTH == "NA":
                    row.R_DEPTH = 0.0

                else:
                    row.R_DEPTH = 0.0

                rows.updateRow(row) 

            # Delete cursor and row objects to remove locks on the data 
            del row 
            del rows

            soil_depth_raster = arcpy.FeatureToRaster_conversion(soil_parent_material_1_clip, "R_DEPTH", '#', DTM_cell_size)
                  
            soil_depth_raster_clip = arcpy.Clip_management(soil_depth_raster, catch_extent, "MODEL_BGS_SOIL_DEPTH", river_catchment_polygon, "#","ClippingGeometry")  
            arcpy.AddMessage("Soil depth field converted to raster and clipped")

        else:
            Soil_clip = arcpy.Clip_management(soil_depth, catch_extent, "MODEL_BGS_SOIL_DEPTH", river_catchment_polygon, "#","ClippingGeometry")

        # Process and clip the advanced superficial deposit data ready to go into the model.
    if advanced_superficial_deposit and advanced_superficial_deposit  != '#':
        # Check superficial type
        desc_advanced_superficial_deposit = arcpy.Describe(advanced_superficial_deposit)
        advanced_superficial_deposit_raster_feature = desc_advanced_superficial_deposit.datasetType
        arcpy.AddMessage("The advanced superficial deposit is a " + advanced_superficial_deposit_raster_feature)

        # Check land cover cell size
        advanced_superficial_deposit_cell_size = desc_advanced_superficial_deposit.meanCellHeight
        arcpy.AddMessage("The advanced superficial deposit cell size is " + str(advanced_superficial_deposit_cell_size))

        if advanced_superficial_deposit_cell_size != DTM_cell_size:
 
            arcpy.AddMessage("The cell size of the advanced superficial deposit you have provided is different to the DTM")
            advanced_superficial_deposit_clip = arcpy.Clip_management(advanced_superficial_deposit, buffer_extent, "Temp11", buffer_catchment, "#","ClippingGeometry")
            arcpy.AddMessage("Advanced superficial deposit clipped to enlarged catchment")
            advanced_superficial_deposit_correct_cell = arcpy.Resample_management(advanced_superficial_deposit_clip, "Temp12", DTM_cell_size, "NEAREST")
            arcpy.AddMessage("Cell size of advanced superficial deposit converted to same as DTM")
            #advanced_superficial_deposit_final_clip = arcpy.Clip_management(advanced_superficial_deposit_correct_cell, catch_extent, "MODEL_SUP_DEPTH", river_catchment_polygon, "#", "ClippingGeometry")
            advanced_superficial_deposit_final_clip = arcpy.gp.ExtractByMask_sa(advanced_superficial_deposit_correct_cell, river_catchment_polygon, "MODEL_SUP_DEPTH")
            arcpy.AddMessage("Advanced superficial deposit correct cell clipped to catchment")

        neighborhood = NbrRectangle(100, 100, "Map")

        # Execute FocalStatistics
        focal_advanced_superficial_deposit = FocalStatistics(advanced_superficial_deposit_final_clip, neighborhood, "MEAN", "")
        #focal_advanced_superficial_deposit_final_clip = arcpy.Clip_management(focal_advanced_superficial_deposit, catch_extent, "MODEL_FOCAL_SUP_DEPTH", river_catchment_polygon, "#", "ClippingGeometry")
        focal_advanced_superficial_deposit_final_clip = arcpy.gp.ExtractByMask_sa(focal_advanced_superficial_deposit, river_catchment_polygon, "MODEL_FOCAL_SUP_DEPTH")
        arcpy.AddMessage("Focal statistics calculated")

        # Convert the soil depth rasters to numpys
        advanced_superficial_deposit_np = arcpy.RasterToNumPyArray("MODEL_SUP_DEPTH", '#','#','#', 0)        
        focal_advanced_superficial_deposit_np = arcpy.RasterToNumPyArray("MODEL_FOCAL_SUP_DEPTH", '#','#','#', 0)        
        final_depth = np.zeros_like(DTM_Clip_np, dtype = float)
              
        np.putmask(final_depth, np.logical_and(focal_advanced_superficial_deposit_np > 0, final_depth >= 0), focal_advanced_superficial_deposit_np)
        np.putmask(final_depth, np.logical_and(advanced_superficial_deposit_np > 0, advanced_superficial_deposit_np > final_depth), advanced_superficial_deposit_np)
      
        final_depth[DTM_Clip_np == -9999] = -9999

        soil_depth_raster = arcpy.NumPyArrayToRaster(final_depth, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        soil_depth_raster.save("MODEL_river_soil_depth")
                
                
    # Soil depth data
    else:
        arcpy.AddMessage("No soil depth data has been provided therefore a default depth of 1m will be used")
        soil_depth = np.empty_like(DTM_Clip_np, dtype = float)
        soil_depth[:] = 1.0
        soil_depth[DTM_Clip_np == -9999] = -9999
        soil_depth_raster = arcpy.NumPyArrayToRaster(soil_depth, bottom_left_corner, DTM_cell_size, DTM_cell_size, -9999)
        soil_depth_raster.save("MODEL_river_soil_depth")

soil_depth_calculation = soil_depth_calc(soil_parent_material_1, advanced_superficial_deposit, DTM_cell_size, buffer_catchment, buffer_extent, river_catchment_BNG, catch_extent)
arcpy.AddMessage("Soil depth calculated")
arcpy.AddMessage("-------------------------")

# Small part of code to delete the unused/not needed parts
def delete_temp_files(delete_list):
    for item in delete_list:
        if arcpy.Exists(item):
            arcpy.Delete_management(item)
delete_list = ["Temp1", "Temp2", "Temp3", "Temp4", "Temp5", "Temp6", "Temp7", "Temp8", "Temp9", "Temp10", "Temp11", "Temp12", "Temp13", "Temp14", "Model_ROADS", "Model_NE_SBS",  "land_BNG", "soil_BNG", "catchment_BNG", "river_buffer", "LCMSTAGE1", "LCMSTAGE2", "LCMSTAGE3", "LCMSTAGE4",  "MODEL_SUP_DEPTH", "MODEL_FOCAL_SUP_DEPTH", "river_raster", "MODEL_river_catchment_poly", "MODEL_river_catchment_ras", "MODEL_roads_polygon", "Clipped_SBS"]
delete_temp_files(delete_list)
arcpy.SetProgressorPosition(100)
arcpy.AddMessage("Deleted temporary files")
arcpy.AddMessage("-----------------------")
arcpy.AddMessage("Preprocessing complete")