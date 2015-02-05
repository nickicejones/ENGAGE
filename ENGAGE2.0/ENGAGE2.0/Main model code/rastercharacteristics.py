# import statments
import arcpy

def get_cell_size_bottom_corner(elevation):

    arcpy.AddMessage("-------------------------")
    # Determine cell size
    describe_elevation = arcpy.Describe(elevation)
    cell_size = describe_elevation.meanCellHeight
    arcpy.AddMessage("The model is working on a cell size of " + str(cell_size) + " metres.")
    arcpy.AddMessage("-------------------------")

    # The below text takes the input raster and calculates the bottom left corner
    extent_xmin_result = arcpy.GetRasterProperties_management(elevation, "LEFT")
    extent_xmin = float(extent_xmin_result.getOutput(0))
    extent_ymin_result = arcpy.GetRasterProperties_management(elevation, "BOTTOM")
    extent_ymin = float(extent_ymin_result.getOutput(0))
    
    # Turns the corner into a point
    bottom_left_corner = arcpy.Point(extent_xmin, extent_ymin)
    arcpy.AddMessage("Calculated the bottom left corner of the input raster")
    arcpy.AddMessage("-------------------------")

    return cell_size, bottom_left_corner