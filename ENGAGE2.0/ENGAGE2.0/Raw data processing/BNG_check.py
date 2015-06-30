##### Description of this python file #####
# This is the start location for preprocessing script for the data preparation prior to running the model


##### VARIABLES - Used in this file#####
# 

#---------------------------------------------------------------------#
##### START OF CODE #####
### Import statements - Python ###
import arcpy
from arcpy.sa import *

# Check if the user is working in British National Grid
def convert_BNG(BNG, DTM_fill, soil, land_cover, orgC, river_catchment_polygon):

    if BNG == True:
        # Define the projection of the shapefiles
        
        # Check the soil type
        desc_soil = arcpy.Describe(soil)
        soil_type = desc_soil.datasetType

        # Check the land cover type
        desc_land = arcpy.Describe(land_cover)
        land_type = desc_land.datasetType
        
        # Check the orgC type
        desc_orgC = arcpy.Describe(orgC)
        orgC_type = desc_orgC.datasetType

         # River Catchemnt Projection 
        river_catchment_BNG = river_catchment_polygon   
        #river_catchment_BNG = arcpy.Project_management(river_catchment_polygon, "catchment_BNG", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
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

        if orgC_type =='FeatureClass':

            orgC_BNG = arcpy.Project_management(orgC, "orgC_BNG", "PROJCS['British_National_Grid',GEOGCS['GCS_OSGB_1936',DATUM['D_OSGB_1936',SPHEROID['Airy_1830',6377563.396,299.3249646]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',400000.0],PARAMETER['False_Northing',-100000.0],PARAMETER['Central_Meridian',-2.0],PARAMETER['Scale_Factor',0.9996012717],PARAMETER['Latitude_Of_Origin',49.0],UNIT['Meter',1.0]]")
            arcpy.AddMessage("Organic Carbon" + " is now in British National Grid projection")
            
    else:
        DTM_BNG = DTM_fill
        soil_BNG = soil
        land_cover_BNG = land_cover
        river_catchment_BNG = river_catchment_polygon
        orgC_BNG = orgC

    arcpy.AddMessage("Projection set for all files")
    arcpy.AddMessage("-------------------------")
           
    return DTM_BNG, soil_BNG, land_cover_BNG, river_catchment_BNG, orgC_BNG

