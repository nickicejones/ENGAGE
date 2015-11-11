##### Description of this python file #####
# This is the start location for the river channel burn section of ENGAGE


##### VARIABLES - Used in this file#####
# workspace is the environmental workspace (geodatabase on your machine)
# decay_parameter 
# maximum_depth_change
# DTM - digital terrain model (elevation of catchment)
# pre_catchment_clip - small area to burn in any river channels
# river_network 

#---------------------------------------------------------------------#
##### START OF CODE #####


# Import the required modules
import arcpy

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True
from arcpy.sa import *

# Set the environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

workspace = arcpy.env.workspace

decay_parameter = int(arcpy.GetParameterAsText(1))

maximum_depth_change = int(arcpy.GetParameterAsText(2))

DTM = arcpy.GetParameterAsText(3)

river_network = arcpy.GetParameterAsText(4)

pour_point = arcpy.GetParameterAsText(5)

# Clip the river network to the extent to the same as the DTM
pnt_array = arcpy.Array()
extent = arcpy.Raster(in_raster).extent
pnt_array.add(extent.lowerLeft)
pnt_array.add(extent.lowerRight)
pnt_array.add(extent.upperRight)
pnt_array.add(extent.upperLeft)

poly = arcpy.Polygon(pnt_array)

# Clip the river network to the same as the digital terrain model
arcpy.Clip_analysis(river_network, poly, "out_dataset")

# Set the environment extent to the same as the DTM
arcpy.env.extent = pnt_array

# Convert the point to a raster

# Calculate Euc Distance

DTM_cell_size = arcpy.GetRasterProperties_management(DTM, "CELLSIZEX")
#Get the elevation standard deviation value from geoprocessing result object
cell_size = DTM_cell_size.getOutput(0) 

arcpy.AddField_management(river_network, "river_depth", "SHORT")
arcpy.AddField_management(river_network, "river_cell_size", "SHORT")

arcpy.AddMessage("Added new fields to the table")
arcpy.AddMessage("-------------------------")

# Create update cursor for feature class 
rows = arcpy.UpdateCursor(river_network) 

for row in rows:
    row.river_depth = 1
    row.river_cell_size = cell_size
    rows.updateRow(row) 

# Delete cursor and row objects to remove locks on the data 
del row 
del rows

river_network_raster = arcpy.PolylineToRaster_conversion(river_network, "river_depth", "river_raster", '#', '#', cell_size)
arcpy.AddMessage("Converted river network to raster")
arcpy.AddMessage("-------------------------")

river_network_cell_size1 = arcpy.PolylineToRaster_conversion(river_network, "river_cell_size", "river_raster_cell1", '#', '#', cell_size)
river_network_cell_size2 = arcpy.PolylineToRaster_conversion(river_network, "river_cell_size", "river_raster_cell2", '#', '#', cell_size)
arcpy.AddMessage("Converted river cell_size to raster")
arcpy.AddMessage("-------------------------")

euc_distance = EucDistance(river_network_raster)
arcpy.AddMessage("Calculated eucludian distance")
euc_final = river_network_cell_size1 / (river_network_cell_size2 + euc_distance)
power_euc_distance = Power(euc_final, decay_parameter)
arcpy.AddMessage("Calculated power")
maximum_depth = power_euc_distance * maximum_depth_change

# Use the whitebox decay algorithm
new_dtm_elevation = DTM - maximum_depth

outCon = Con(IsNull(new_dtm_elevation), DTM, new_dtm_elevation)
outCon.save("MODEL_DTM_new_fixed")

arcpy.MosaicToNewRaster_management("MODEL_DTM_new_fixed;MODEL_DTM", workspace,"MODEL_DTM_Channel_Burned", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]","32_BIT_FLOAT", cell_size,"1","FIRST","FIRST")

arcpy.AddMessage("Calculated and saved new model elevation")
arcpy.AddMessage("-------------------------")

# Small part of code to delete the unused/not needed parts
def delete_temp_files(delete_list):
    for item in delete_list:
        if arcpy.Exists(item):
            arcpy.Delete_management(item)
delete_list = ["river_raster", "river_raster_cell1", "river_raster_cell2", "MODEL_DTM_new_fixed"]
delete_temp_files(delete_list)
arcpy.AddMessage("Deleted temporary files")