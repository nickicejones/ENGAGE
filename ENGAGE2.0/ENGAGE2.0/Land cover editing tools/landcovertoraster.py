# Import the required modules
import arcpy

# Set the environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Bit of code to get the DTM cell size
DTM = "MODEL_DTM"

# Get the cell size 
#Get the geoprocessing result object
DTM_cell_size = arcpy.GetRasterProperties_management(DTM, "CELLSIZEX")
#Get the elevation standard deviation value from geoprocessing result object
cell_size = DTM_cell_size.getOutput(0) 

if arcpy.Exists("MODEL_LCM_shapefile"):
    land_cover = "MODEL_LCM_shapefile"
    land_cover_type = 'LCM 2007'
    arcpy.AddMessage("LCM 2007 land cover data detected")
    arcpy.AddMessage("-------------------------")
    land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover, "grid_code", "MODEL_Landcover_LCM_Altered", cell_size)
    arcpy.AddMessage("Land cover converted to raster")

elif arcpy.Exists("MODEL_CORINE_shapefile"):
    land_cover = "MODEL_CORINE_shapefile"
    land_cover_type = 'CORINE 2006'
    arcpy.AddMessage("CORINE 2006 land cover data detected")
    arcpy.AddMessage("-------------------------")
    land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover, "grid_code", "MODEL_Landcover_CORINE_Altered", cell_size)
    arcpy.AddMessage("Land cover converted to raster")

elif arcpy.Exists("MODEL_SPS_shapefile"):
    land_cover = "MODEL_SPS_shapefile"
    land_cover_type = 'COMBINE'
    arcpy.AddMessage("Natural England SPS and LCM 2007 combined land cover data detected")
    arcpy.AddMessage("-------------------------")
    land_cover_raster = arcpy.FeatureToRaster_conversion(land_cover, "gridcode", "MODEL_COMBINE_LC_Altered", cell_size)
    arcpy.AddMessage("Land cover converted to raster")