# Import the required modules
import arcpy
from arcpy import env

# Set the environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# get the map document
mxd = arcpy.mapping.MapDocument("CURRENT")

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

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
    land_cover_shapefile = arcpy.RasterToPolygon_conversion(land_cover, "MODEL_COMBINE_shapefile", "NO_SIMPLIFY")
    land_cover_shapefile = "MODEL_COMBINE_shapefile"
    arcpy.AddMessage("Land cover converted to shapefile for editing")

# create a new layer
newlayer = arcpy.mapping.Layer(land_cover_shapefile)

# add the layer to the map at the bottom of the TOC in data frame 0
arcpy.mapping.AddLayer(df, newlayer, "TOP")

arcpy.AddMessage("You can now find the shapefile of the landcover in your workspace ready for editing")
