# Import statments
import math
import arcpy

### Import Script Files NJ created ###
import temperatureregion

class Evapotranspiration(object):
    """description of class"""
    # Function for the evapotranspiration
    def MinMaxMeanTemp(self, region, current_date):
    # Calculate the average temperature information
        if region == "England SW/ Wales S":
            temperatures = temperatureregion.englandSW_walesS()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "Scotland N":
            temperatures = temperatureregion.scotlandN()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "Scotland E":
            temperatures = temperatureregion.scotlandE()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "Scotland W":
            temperatures = temperatureregion.scotlandW()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "England E & NE":
            temperatures = temperatureregion.englandE_NE()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "England NW/ Wales N":
            temperatures = temperatureregion.englandNW_walesN
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "Midlands":
            temperatures = temperatureregion.midlands()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "East Anglia":
            temperatures = temperatureregion.east_anglia()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        elif region == "England SE/ Central S":
            temperatures = temperatureregion.englandSE_centralS()
            mean_temp, max_temp, min_temp = temperatures.gettemperature(current_date)
        arcpy.AddMessage("The mean temp is " + str(mean_temp) + ". The max temp is " + str(max_temp) + ". The min temp is " + str(min_temp))   
        arcpy.AddMessage("-------------------------") 
        return mean_temp, max_temp, min_temp

    # Function to get the latitude based upon the users selection
    def UKlatituderadians(self, region, river_catchment_poly):
        if arcpy.CheckProduct("ArcInfo") == "Available":

            def getlatituderadiansrivercatchment(river_catchment_poly):
                centre_point = arcpy.FeatureToPoint_management(river_catchment_poly,"out_centre_point","INSIDE")
   
                dsc = arcpy.Describe(centre_point)
                cursor = arcpy.UpdateCursor(centre_point, "", "Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984.prj")
                for row in cursor:
                    shape=row.getValue(dsc.shapeFieldName)
                    geom = shape.getPart(0)
                    lat_deg = geom.Y
    
                del cursor, row
                latitude = (lat_deg * math.pi)  / 180
                arcpy.AddMessage("The latitude of the river catchment is " + str(lat_rad))

                return latitude
            latitude = getlatituderadiansrivercatchment(river_catchment_poly)
            
        else:
            def getlatituderadiansregion(region):

                if region == "England SW/ Wales S":
                    latitude = 0.914150067228
                elif region == "Scotland N":
                    latitude = 1.05058554677
                elif region == "Scotland E":
                    latitude = 0.971535474685
                elif region == "Scotland W":
                    latitude = 0.968875753818
                elif region == "England E & NE":
                    latitude = 0.941819912486
                elif region == "England NW/ Wales N":
                    latitude = 0.943263614828
                elif region == "Midlands":
                    latitude = 0.915926640792
                elif region == "East Anglia":
                    latitude = 0.911835053377
                elif region == "England SE/ Central S":
                    latitude = 0.891900143109
                arcpy.AddMessage("The latitude for region " + str(region) + " is " + str(latitude))
                arcpy.AddMessage("-------------------------") 

                return latitude
            latitude = getlatituderadiansregion(region)
            arcpy.AddMessage("ArcGIS for Desktop Advanced license not available")          

        return latitude

    def ReferenceEvapotranspiration(self, latitude, day_of_year, max_temp, min_temp, mean_temp):
        # Variables
        
        # SC is the solar constant
        SC = 0.0820
        
        # Caluclate TR which is the mean daily 
        TR = max_temp - min_temp
        
        # Rela_dist is the inverse relative distance
        rela_dist = 1 + 0.033 * math.cos(((2 * math.pi) / 365) * day_of_year)

        # SD, Solar decimation
        SD = 0.409 * math.sin(((2 * math.pi) / 365) * day_of_year - 1.39)
        
        # SHA, Sunset hour angle
        SHA = math.acos(-math.tan(latitude) * math.tan(SD))
        
        # Ra is extraterrestial radiation
        Ra = ((24 * 60) / math.pi) * SC * rela_dist * (SHA * (math.sin(latitude) * math.sin(SD)) + (math.cos(latitude) * (math.cos(SD) * math.sin(SHA))))
        
        # ET is reference crop evapotranspiration, Ra is extraterrestrial
        # radiation, TR daily temperature range, TC mean air temperature
        ETo = 0.0029 * Ra * (mean_temp + 20) * (TR ** 0.4)
        arcpy.AddMessage("Evapotranspiration for region is " + str(ETo))
        arcpy.AddMessage("-------------------------") 

        return ETo