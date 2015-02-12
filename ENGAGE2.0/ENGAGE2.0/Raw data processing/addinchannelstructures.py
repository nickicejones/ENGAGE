# Import the required modules
import arcpy

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True
from arcpy.sa import *

# Set the environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

in_channel_structure = arcpy.GetParameterAsText(1)

workspace = arcpy.env.workspace

# Locate the model DTM
if arcpy.Exists("MODEL_DTM"):
    DTM = "MODEL_DTM"
    arcpy.env.mask = DTM
    arcpy.env.extent = DTM
    if arcpy.Exists("MODEL_DTM_Channel_Burned"):
        DTM = "MODEL_DTM_Channel_Burned"
    arcpy.AddMessage("Model elevation detected (DTM)")
    arcpy.AddMessage("-------------------------")

# Find the cell size
DTM_cell_size = arcpy.GetRasterProperties_management(DTM, "CELLSIZEX")
#Get the elevation standard deviation value from geoprocessing result object
cell_size = DTM_cell_size.getOutput(0) 

# Add a temporary field to the polygon
arcpy.AddField_management(in_channel_structure, "dam_height", "SHORT")
arcpy.AddMessage("Added new fields to the table")
arcpy.AddMessage("-------------------------")

# Create update cursor for feature class 
rows = arcpy.UpdateCursor(in_channel_structure) 

for row in rows:
    row.dam_height = -5    
    rows.updateRow(row) 

del row
del rows

# Convert the polygon to a raster
dam_area = arcpy.PolygonToRaster_conversion(in_channel_structure, "dam_height", "dam_raster", '#', '#', cell_size)
arcpy.AddMessage("Area of influence converted to polygon")

new_dtm = Plus(DTM, dam_area)
new_dtm.save("Altered_DTM")

combined_dtm = arcpy.MosaicToNewRaster_management("Altered_DTM;MODEL_DTM", workspace,"Altered_DTM_withflat", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]","32_BIT_FLOAT", cell_size,"1","FIRST","FIRST")

def extents(fc):
    extent = arcpy.Describe(fc).extent
    west = round(extent.XMin) 
    south = round(extent.YMin) 
    east = round(extent.XMax)
    north = round(extent.YMax) 
    return west, south, east, north

# Obtain extents of two shapes
XMin, YMin, XMax, YMax = extents(DTM)

# Set the extent environment
arcpy.AddMessage("The catchment extent is " + "%s %s %s %s" % (XMin, YMin, XMax, YMax))

catch_extent = "%s %s %s %s" % (XMin, YMin, XMax, YMax)

# Clip the DTM
DTM_Clip = arcpy.Clip_management(combined_dtm, catch_extent, "model_correct", "#","-3.402823e+038","NONE")
arcpy.AddMessage("Corrected the DTM extent")
arcpy.AddMessage("-------------------------")

outFill = Fill("model_correct")
outFill.save("MODEL_DTM")
arcpy.AddMessage("Filled any sinks")
arcpy.AddMessage("-------------------------")

arcpy.AddMessage("Calculated and saved new model elevation")
arcpy.AddMessage("-------------------------")

# Small part of code to delete the unused/not needed parts
def delete_temp_files(delete_list):
    for item in delete_list:
        if arcpy.Exists(item):
            arcpy.Delete_management(item)
delete_list = ["Altered_DTM_withflat", "dam_raster", "model_correct", "Altered_DTM"]
delete_temp_files(delete_list)
arcpy.AddMessage("Deleted temporary files")
