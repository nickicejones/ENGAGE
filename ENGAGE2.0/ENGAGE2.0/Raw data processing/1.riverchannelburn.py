##### Description of this python file #####
# This is the start location for the river channel burn section of ENGAGE


##### VARIABLES - Used in this file#####
# workspace is the environmental workspace (geodatabase on your machine)
# decay_parameter 
# maximum_depth_change
# DTM - digital terrain model (elevation of catchment)
# pre_catchment_clip - small area to burn in any river channels
# river_network - river network as a polyline
# pour point - the pour point of the river network.

#---------------------------------------------------------------------#
##### START OF CODE #####

# Import the required modules
import arcpy

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True
from arcpy.sa import *

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Set the environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)
workspace = arcpy.env.workspace

# Values that control the rate at which the depth of the channel changes
decay_parameter = int(arcpy.GetParameterAsText(1))
maximum_depth_change = int(arcpy.GetParameterAsText(2))

# The DTM that is going to have the river channel burned in
DTM = arcpy.GetParameterAsText(3)

# The river network that is going to be burned into the DTM
river_network = arcpy.GetParameterAsText(4)

# the pour point of the river catchment - this is used to calculate the eclidian distance.
pour_point = arcpy.GetParameterAsText(5)
arcpy.AddMessage("-------------------------")
arcpy.AddMessage("Loaded datasets")
arcpy.AddMessage("-------------------------")


# Calculate the cell size of the DTM
DTM_cell_size = arcpy.GetRasterProperties_management(DTM, "CELLSIZEX")
#Get the elevation standard deviation value from geoprocessing result object
cell_size = DTM_cell_size.getOutput(0) 
arcpy.AddMessage("Calculated operating cell size")
arcpy.AddMessage("-------------------------")

# Clip the river network to the extent to the same as the DTM
# First calculate the extent of the DTM
pnt_array = arcpy.Array()
extent = arcpy.Raster(DTM).extent
pnt_array.add(extent.lowerLeft)
pnt_array.add(extent.lowerRight)
pnt_array.add(extent.upperRight)
pnt_array.add(extent.upperLeft)

# Turn the extents of the raster into a polygon to clip the river_network
clipping_polygon = arcpy.Polygon(pnt_array) 

# Clip the river network to the same as the digital terrain model
river_network = arcpy.Clip_analysis(river_network, clipping_polygon, "out_river")

# Add fields to the river network polyline
arcpy.AddField_management(river_network, "river_depth", "SHORT")
arcpy.AddField_management(river_network, "river_cell_size", "SHORT")
arcpy.AddMessage("River network clipped and added new fields to the table")
arcpy.AddMessage("-------------------------")

def extents(fc):
    extent = arcpy.Describe(fc).extent
    west = round(extent.XMin) 
    south = round(extent.YMin) 
    east = round(extent.XMax)
    north = round(extent.YMax) 
    return west, south, east, north

# Obtain extents of the river network
XMin, YMin, XMax, YMax = extents(river_network)

# Set the extent environment
arcpy.AddMessage("The catchment extent is " + "%s %s %s %s" % (XMin, YMin, XMax, YMax))
catch_extent = "%s %s %s %s" % (XMin, YMin, XMax, YMax)
arcpy.AddMessage("-------------------------")

# Set the environment to the calculated extent
arcpy.env.extent = catch_extent

# Convert the point to a raster
point_raster = arcpy.PointToRaster_conversion(pour_point, '#', "point_raster", '#', '#', cell_size)

# Execute EucDistance
outEucDistance = EucDistance(point_raster, '#', cell_size)

# Save the output 
#outEucDistance.save("eucdist")
arcpy.AddMessage("Calculated eucludian distance")
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



#### THE WHITE BOX DECAY ALGORITHM ####
# Z = E – (G/G+D))k * H Z = newly calculated grid cell elevation (m) 
# E = old grid cell elevation (m) 
# G = grid resolution (m) 
# D = distance from a stream cell (m) 
# k = decay coefficient 
# H = elevation decrement (m) 

# Add the EUC and river cell size together
#arcpy.gp.RasterCalculator_sa("""Con("river_raster_cell2" > 0,"river_raster_cell2"+"eucdist")""","part1")
EUCPlusRiverCell = Con(river_network_cell_size2 > 0, (outEucDistance+river_network_cell_size2))
#EUCPlusRiverCell.save("part1")

# divide the river cell by the grid resolution + distance from stream cell.
euc_final = river_network_cell_size1 / EUCPlusRiverCell
#euc_final.save("part2")

power_euc_distance = Power(euc_final, decay_parameter)
#power_euc_distance.save("part3")
arcpy.AddMessage("Calculated power")

maximum_depth = power_euc_distance * maximum_depth_change
#maximum_depth.save("depth_change")

# Take the calculated depth from the raster
new_dtm_elevation = DTM - maximum_depth
#new_dtm_elevation.save("Depth_changed")

outCon = Con(IsNull(new_dtm_elevation), DTM, new_dtm_elevation)
outCon.save("MODEL_DTM")

#arcpy.MosaicToNewRaster_management("MODEL_DTM_new_fixed;MODEL_DTM", workspace,"MODEL_DTM_Channel_Burned", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]","32_BIT_FLOAT", cell_size,"1","FIRST","FIRST")

arcpy.AddMessage("Calculated and saved new model elevation")
arcpy.AddMessage("-------------------------")

# Small part of code to delete the unused/not needed parts
def delete_temp_files(delete_list):
    for item in delete_list:
        if arcpy.Exists(item):
            arcpy.Delete_management(item)
delete_list = ["river_raster", "river_raster_cell1", "river_raster_cell2", "MODEL_DTM_new_fixed", "point_raster", "out_river"]
delete_temp_files(delete_list)
arcpy.AddMessage("Deleted temporary files")