# import statments
import arcpy

# set environmental workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# set the environmental workspace
workspace = arcpy.env.workspace

# select input rasters
input_rasters = arcpy.GetParameterAsText(1)

arcpy.AddMessage("Selected input dtm cell size is " + str(cell_size))

arcpy.MosaicToNewRaster_management(input_rasters, workspace,"Merged_elevation","#","32_BIT_FLOAT","#","1","LAST","FIRST")

arcpy.AddMessage("Process Successfull")