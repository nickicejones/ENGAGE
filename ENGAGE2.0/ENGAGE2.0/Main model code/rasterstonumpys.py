# import statments
import arcpy

# Simple function to convert rasters to numpys
def convert_raster_to_numpy(list_of_rasters):
    list_of_numpy_arrays = []
    for raster in list_of_rasters:
        arcpy.AddMessage("Converting " + str(raster) + " raster to numpy array")
        numpy = arcpy.RasterToNumPyArray(raster, '#', '#', '#', -9999)        
        list_of_numpy_arrays.append(numpy)
            
    arcpy.AddMessage("-------------------------")
    arcpy.AddMessage("Successfully converted rasters to numpy arrays")
    arcpy.AddMessage("-------------------------")

    return list_of_numpy_arrays

def convert_numpy_to_raster(list_of_numpys, bottom_left_corner, cell_size, save_date):
    
    for name, numpy in list_of_numpys.iteritems():
        arcpy.AddMessage("Converting " + str(name) + " numpy array to raster")
        numpy = arcpy.NumPyArrayToRaster(numpy, bottom_left_corner, cell_size, cell_size, -9999)
        numpy.save(name + "_" + str(save_date))        
        del name, numpy
        
    arcpy.AddMessage("-------------------------")
    arcpy.AddMessage("Successfully converted numpy arrays to rasters")
    arcpy.AddMessage("-------------------------")