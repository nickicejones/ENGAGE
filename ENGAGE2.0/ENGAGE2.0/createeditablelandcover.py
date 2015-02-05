# Import the required modules
import arcpy

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# Set the environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

if arcpy.Exists("MODEL_Landcover_LCM"):
    land_cover = "MODEL_Landcover_LCM"
    land_cover_type = 'LCM 2007'
    arcpy.AddMessage("LCM 2007 land cover data detected")
    arcpy.AddMessage("-------------------------")
elif arcpy.Exists("MODEL_Landcover_CORINE"):
    land_cover = "MODEL_Landcover_CORINE"
    land_cover_type = 'CORINE 2006'
    arcpy.AddMessage("CORINE 2006 land cover data detected")
    arcpy.AddMessage("-------------------------")
elif arcpy.Exists("MODEL_COMBINE_LC"):
    land_cover = "MODEL_COMBINE_LC"
    land_cover_type = 'COMBINE'
    arcpy.AddMessage("Natural England SPS and LCM 2007 combined land cover data detected")
    arcpy.AddMessage("-------------------------")

if land_cover_type == "LCM 2007":
    land_cover = "MODEL_Landcover_LCM"
    land_cover_shapefile = arcpy.RasterToPolygon_conversion(land_cover, "MODEL_LCM_shapefile", "NO_SIMPLIFY")
    arcpy.AddMessage("Land cover converted to shapefile for editing")
                            
elif land_cover_type == "CORINE 2006": 
    land_cover = "MODEL_Landcover_CORINE"
    land_cover_shapefile = arcpy.RasterToPolygon_conversion(land_cover, "MODEL_CORINE_shapefile", "NO_SIMPLIFY")
    arcpy.AddMessage("Land cover converted to shapefile for editing")

elif land_cover_type == 'COMBINE':
    land_cover = "MODEL_COMBINE_LC"
    land_cover_shapefile = arcpy.RasterToPolygon_conversion(land_cover, "MODEL_SPS_shapefile", "NO_SIMPLIFY")
    arcpy.AddMessage("Land cover converted to shapefile for editing")

arcpy.AddMessage("You can now find the shapefile of the landcover in your workspace ready for editing")
