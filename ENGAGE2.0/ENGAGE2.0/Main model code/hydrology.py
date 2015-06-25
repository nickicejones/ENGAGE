#---------------------------------------------------------------------#
##### START OF CODE #####
# Import statements
import math
import arcpy
import time
import os
import subprocess
import sys
import numpy as np
from arcpy.sa import *

# Create a Hydrology class to store all the calculations required to calculate
# daily hydrology.
class SCSCNQsurf(object):

    def check_baseflow(self, precipitation, baseflow_provided):
        if baseflow_provided == True: 
            precipitation_split = precipitation.split()
            precipitation = precipitation_split[0]
            arcpy.AddMessage("Today precipitation is " + str(precipitation))

            baseflow = precipitation_split[1]
            arcpy.AddMessage("Baseflow is " + str(baseflow))
            arcpy.AddMessage("-------------------------") 

        else:
            baseflow = 0
            precipitation = precipitation
            arcpy.AddMessage("Today precipitation is " + str(precipitation))
            
        return precipitation, baseflow

    def check_slope_flow_directions(self, first_loop, use_dinfinity, day_of_year, CN2_d, DTM, baseflow_provided, numpy_array_location):
                 
        arcpy.AddMessage("Recalculating elevation, slope and flow directions")
        arcpy.AddMessage("-------------------------") 
        if use_dinfinity == True:
            slope, DTM, flow_direction_np, flow_direction_raster, ang = SCSCNQsurf().calculate_slope_fraction_flow_direction_dinf(DTM, numpy_array_location)
            flow_accumulation = 0

        else:
            ang = 0
            slope, DTM, flow_direction_np, flow_direction_raster, flow_accumulation = SCSCNQsurf().calculate_slope_fraction_flow_direction_d8(DTM, baseflow_provided)
                                 
        arcpy.AddMessage("New elevation, slope and flow directions calculated")
        arcpy.AddMessage("-------------------------") 

        # Calculate CN1_numbers and CN3_numbers adjusted for antecedent conditions
        CN2s_d, CN1s_d, CN3s_d = SCSCNQsurf().combineSCSCN(CN2_d, slope)      
                            
        return slope, DTM, flow_direction_np, flow_direction_raster, flow_accumulation, CN2s_d, CN1s_d, CN3s_d, ang  
            
    # Function to convert the slope from a degrees to a fraction d8 methodology
    def calculate_slope_fraction_flow_direction_d8(self, DTM, baseflow_provided):   
        start = time.time()
        
        # Old ArcGIS method but still used for the sediment transport aspect
        DTM = Fill(DTM)
        flow_direction_raster = FlowDirection(DTM)
        arcpy.AddMessage("Flow direcion Calculated")
        arcpy.AddMessage("-------------------------")
        slope = Slope(DTM, "DEGREE")
        arcpy.AddMessage("Slope calculated")
        arcpy.AddMessage("-------------------------")

        # Convert fill, slope, flow direction to numpy array
        DTM = arcpy.RasterToNumPyArray(DTM,'#','#','#', -9999)
        slope = arcpy.RasterToNumPyArray(slope, '#','#','#', -9999)
        flow_direction_np = arcpy.RasterToNumPyArray(flow_direction_raster, '#','#','#', -9999)

        np.radians(slope)
        np.tan(slope)
        slope[slope == 0] = 0.0001

        if baseflow_provided == True:
            # Calculate flow accumulation
            flow_accumulation = FlowAccumulation(flow_direction_raster)
            arcpy.AddMessage("Calculated flow accumulation")
            arcpy.AddMessage("-------------------------") 

        else:
            flow_accumulation = '#'

        arcpy.AddMessage("Calculating took " + str(round(time.time() - start,2)) + "s.")
        arcpy.AddMessage("-------------------------")
        
        return slope, DTM, flow_direction_np, flow_direction_raster, flow_accumulation

    # Function to convert the slope from a degrees to a fraction
    def calculate_slope_fraction_flow_direction_dinf(self, DTM, numpy_array_location):   
        start = time.time()
        
        # Execute flow direction and slope on the first day of model operation or at the end of each month
        output_asc = numpy_array_location + "\output_asc.asc"
        output_tiff = numpy_array_location + "\output_tif.tif"

        # Input
        ele_ascii = arcpy.RasterToASCII_conversion(DTM, output_asc)
        ele_tiff = arcpy.ASCIIToRaster_conversion(ele_ascii, output_tiff, "FLOAT")

        # New version for calculating flow directions     
        inlyr = ele_tiff
        desc = arcpy.Describe(inlyr)
        fel=str(desc.catalogPath)
        arcpy.AddMessage("\nInput Pit Filled Elevation file: "+fel)

        # Input Number of Processes
        inputProc=str(8)
        arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

        # Outputs
        ang = str(numpy_array_location + "\oang.tif")
        arcpy.AddMessage("\nOutput Dinf Flow Direction File: "+ang)
        slp = str(numpy_array_location + "\oslp.tif")
        arcpy.AddMessage("\nOutput Dinf Slope File: "+slp)

        # Construct command 
        cmd = 'mpiexec -n ' + inputProc + ' DinfFlowDir -fel ' + '"' + fel + '"' + ' -ang ' + '"' + ang + '"' + ' -slp ' + '"' + slp + '"'
        arcpy.AddMessage("\nCommand Line: "+cmd)

        # Submit command to operating system
        os.system(cmd)

        # Capture the contents of shell command and print it to the arcgis dialog box
        process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        arcpy.AddMessage('\nProcess started:\n')
        for line in process.stdout.readlines():
            arcpy.AddMessage(line)

        # Calculate statistics on the output so that it displays properly
        arcpy.AddMessage('Executing: Calculate Statistics\n')
        arcpy.CalculateStatistics_management(ang)
        arcpy.CalculateStatistics_management(slp)
      
        # Old ArcGIS method but still used for the sediment transport aspect
        DTM = Fill(DTM)
        flow_direction_raster = FlowDirection(DTM)
        arcpy.AddMessage("Flow Direcion Calculated")
        arcpy.AddMessage("-------------------------")
        slope = Slope(DTM, "DEGREE")
        arcpy.AddMessage("Slope Calculated")
        arcpy.AddMessage("-------------------------")

        # Convert fill, slope, flow direction to numpy array
        DTM = arcpy.RasterToNumPyArray(DTM,'#','#','#', -9999)
        slope = arcpy.RasterToNumPyArray(slope, '#','#','#', -9999)
        flow_direction_np = arcpy.RasterToNumPyArray(flow_direction_raster, '#','#','#', -9999)

        np.radians(slope)
        np.tan(slope)
        slope[slope == 0] = 0.0001
        arcpy.AddMessage("Calculating took " + str(round(time.time() - start,2)) + "s.")

        return slope, DTM, flow_direction_np, flow_direction_raster, ang

    def spatial_uniform_spatial_precip(self, precipitation, DTM, day_pcp_yr, precipitation_gauge_elevation):
        precipitation = float(precipitation)
                        
        #Calculate days of precipitation per year       
        if precipitation != 0 and precipitation_gauge_elevation != 0:
            arcpy.AddMessage("The precipiation is " + str(precipitation))              
            arcpy.AddMessage("The average number of days precipitation per year in the catchment is " + str(day_pcp_yr))
            plaps = 0.5                
            precip_array = ((DTM - float(precipitation_gauge_elevation)) * (plaps / (day_pcp_yr * 1000))) + float(precipitation)
            precip_array[DTM == -9999] = -9999
            arcpy.AddMessage("Orographic preciptation calculated")
            
        elif precipitation != 0 and precipitation_gauge_elevation == 0:
            # Create the precipitation array for the day
            precip_array = np.ones_like(DTM)
            precip_array = precip_array * float(precipitation)
            precip_array[DTM == -9999] = -9999
            arcpy.AddMessage("Spatially uniform precipitation calculated")
        
        else:
            arcpy.AddMessage("No precipitation today")
            precip_array = np.zeros_like(DTM)            
            precip_array[DTM == -9999] = -9999

        arcpy.AddMessage("-------------------------") 
        return precip_array

    def combineSCSCN(self, CN2_d, slope):

        start = time.time()

        # Calculate CN1 and CN3
        CN1_d = CN2_d - (20 * (100 - CN2_d )) / ((100 - CN2_d ) + np.exp(2.533 - 0.0636 * (100 - CN2_d)))
        CN3_d = CN2_d * np.exp(0.00673 * (100 - CN2_d))

        # Readd the nodata values
        CN1_d[CN2_d == -9999] = -9999
        CN3_d[CN2_d == -9999] = -9999

        arcpy.AddMessage("Calculating CN1 and CN3 numbers took " + str(round(time.time() - start,2)) + "s.")
        
        start = time.time()

        CN2s_d = ((CN3_d - CN2_d) / 3) * (1 - 2 * np.exp(-13.86 * slope)) + CN2_d

        np.putmask(CN2s_d, CN2_d == 100, CN2_d) # Ensure values of 100 remain at 100

        # Readd the nodata values
        CN2s_d[CN2_d == -9999] = -9999

        arcpy.AddMessage("Calculating CN2 adjusted for slope took " + str(round(time.time() - start,2)) + "s.")    
                          
        # Calculate CN1s and CN3s
        # CN1 (Wilting Point)
        CN1s_d = CN2s_d - (20 * (100 - CN2s_d )) / ((100 - CN2s_d ) + np.exp(2.533 - 0.0636 * (100 - CN2s_d)))

        # Calculate CN3 (Field Capacity)
        CN3s_d = CN2s_d * np.exp(0.00673 * (100 - CN2s_d))

        np.putmask(CN1s_d, CN2s_d == 100, CN2s_d) # Ensure values of 100 remain at 100
        np.putmask(CN3s_d, CN2s_d == 100, CN2s_d) # Ensure values of 100 remain at 100

        # Readd the nodata values
        CN1s_d[CN2s_d == -9999] = -9999
        CN3s_d[CN2s_d == -9999] = -9999

        arcpy.AddMessage("Calculating CN1 and CN3 adjusted for slope numbers took " + str(round(time.time() - start,2)) + "s.")      
        arcpy.AddMessage("-------------------------")
                   
        return CN2s_d, CN1s_d, CN3s_d
    
    # Method to calculate surface runoff not adjusted for evapotranspiration and antecdent conditions - correct checked 08/07/14
    def OldQsurf(self, precipitation, CN2s_d):
        ''' This method calculates the default Qsurf not taking into account the ETo varying retention parameter'''
         
        start = time.time()      
        
        # Calculate the Scurr
        Scurr = 25.4 * ((1000 / CN2s_d) - 10)
        Scurr[CN2s_d == -9999] = -9999
                
        # Determine Preciptiation Excess
        Scurr_threshold = 0.05 * Scurr # intial abstractions is often abreviated to 0.2S
        Scurr_threshold[CN2s_d == -9999] = -9999
        
        #Calculate for all cells
        Q_surf = ((precipitation - (0.05 * Scurr)) ** 2) / (precipitation + (0.95 * Scurr))
        
        Q_surf[precipitation <= Scurr_threshold] = 0
        Q_surf[Q_surf < 0] = 0

        # Check qsurf is not greater than the amount of precipitation
        #Q_surf[Q_surf > self.precipitation_d] = self.precipitation_d
        np.putmask(Q_surf, Q_surf > precipitation, precipitation)

        # Check to ensure there is adaquate precipitation
        #Q_surf[self.precipitation_d == 0] = self.precipitation_d
        np.putmask(Q_surf, precipitation == 0, precipitation)
        
        # Ensure that impervious areas generate 100% runoff
        np.putmask(Q_surf, CN2s_d == 100, precipitation)
        Q_surf[CN2s_d == -9999] = -9999
        arcpy.AddMessage("Calculating Qsurf old (Evapotranspiration not included) " + str(round(time.time() - start,2)) + "s.")
        arcpy.AddMessage("-------------------------")  

        return Q_surf
          
    # Method to caluclate the retention parameter - correct checked 08/07/14
    def RententionParameter(self, precipitation, CN1s_d, CN2_d, CN2s_d, ETo, Sprev, Q_surf, first_loop):
        # Variables RP = retention parameter, Smax = maximum retention
        # parameter, soil_water = soil water content, w1 = first shape
        # coefficient, w2 - second shape coefficient, FC =
        start = time.time()             
        # Variables needed for this equation to work
        cncoef = -1.0
        
        # Calculate Smax, which is calculated using CN1s_d, as it uses the
        # wilting point
         
        Smax = 25.4 * ((1000 / CN1s_d) - 10)
               

        SAT = 2.565656566
        
        # Calculate FC, which is calculated using the CN3s_d, as it using the
        # field at capacity
        # S3 = 25.4 * ((1000/CN3s_d) - 10)

        if first_loop == True:
            arcpy.AddMessage("This is the first day of model operation")
            Scurr = 0.9 * Smax
            Scurr[CN2s_d == -9999] = -9999
            
        else:
            Scurr = Sprev + ETo * np.exp((cncoef * Sprev) / Smax) - precipitation + Q_surf
            np.putmask(Scurr, Scurr > Smax, Smax)
            np.putmask(Scurr, np.logical_and(CN2_d != 100, Scurr < SAT), SAT)
            Scurr[CN2s_d == -9999] = -9999 

        arcpy.AddMessage("Calculating Scurr (includes antecedent conditions and evapotranspiration) took " + str(round(time.time() - start,2)) + "s.")
        arcpy.AddMessage("-------------------------") 
                
        return Scurr 
                    
    # Calculate surface runoff - correct checked 08/07/14
    def SurfSCS(self, precipitation, Scurr, CN2s_d):

        start = time.time()
             
        # Determine Preciptiation Excess
        Scurr_threshold = 0.05 * Scurr # intial abstractions is often abreviated to 0.2S
        Scurr_threshold[Scurr == -9999] = -9999
        
        #Calculate for all cells
        Q_surf = ((precipitation - (0.05 * Scurr)) ** 2) / (precipitation + (0.95 * Scurr))
        Q_surf[precipitation <= Scurr_threshold] = 0
        Q_surf[Q_surf < 0] = 0
        
        # Check qsurf is not greater than the amount of precipitation
        #Q_surf[Q_surf > self.precipitation_d] = self.precipitation_d
        np.putmask(Q_surf, Q_surf > precipitation, precipitation)

        # Check to ensure there is adaquate precipitation
        #Q_surf[self.precipitation_d == 0] = self.precipitation_d
        np.putmask(Q_surf, precipitation == 0, precipitation)

        # Ensure that impervious areas generate 100% runoff
        np.putmask(Q_surf, CN2s_d == 100, precipitation)

        Q_surf[Scurr == -9999] = -9999

        arcpy.AddMessage("Calculating Qsurf with antecedent conditions and evapotranspirtation factored in took " + str(round(time.time() - start,2)) + "s.")
        arcpy.AddMessage("-------------------------") 
        return Q_surf

    def FlowAccumulationDinf(self, ang, Qsurf, numpy_array_location):

        # Inputs
        inlyr = ang
        desc = arcpy.Describe(inlyr)
        ang=str(desc.catalogPath)
        arcpy.AddMessage("\nInput Dinf Flow Direction file: "+ang)

        # Execute flow direction and slope on the first day of model operation or at the end of each month
        output_asc = numpy_array_location + "\output_asc.asc"
        output_tiff = numpy_array_location + "\output_tif.tif"
        Qsurf_ascii = arcpy.RasterToASCII_conversion(Qsurf, output_asc)
        Qsurf_tiff = arcpy.ASCIIToRaster_conversion(Qsurf_ascii, output_tiff, "FLOAT")

        weightgrid= Qsurf_tiff
        if arcpy.Exists(weightgrid):
            desc = arcpy.Describe(weightgrid)
            wtgr=str(desc.catalogPath)
            arcpy.AddMessage("\nInput Weight Grid: "+wtgr)

        edgecontamination='false'
        arcpy.AddMessage("\nEdge Contamination: "+edgecontamination)

        # Input Number of Processes
        inputProc=str(8)
        arcpy.AddMessage("\nInput Number of Processes: "+inputProc)

        # Output
        sca = str(numpy_array_location + "\osca.tif")
        arcpy.AddMessage("\nOutput Dinf Specific Catchment Area Grid: "+sca)

        # Construct command
        cmd = 'mpiexec -n ' + inputProc + ' AreaDinf -ang ' + '"' + ang + '"' + ' -sca ' + '"' + sca + '"'

        if arcpy.Exists(weightgrid):
            cmd = cmd + ' -wg ' + '"' + wtgr + '"'
        if edgecontamination == 'false':
            cmd = cmd + ' -nc '
    
        arcpy.AddMessage("\nCommand Line: "+cmd)

        # Submit command to operating system
        os.system(cmd)

        # Capture the contents of shell command and print it to the arcgis dialog box
        process=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        arcpy.AddMessage('\nProcess started:\n')
        for line in process.stdout.readlines():
            arcpy.AddMessage(line)

        # Calculate statistics on the output so that it displays properly
        arcpy.AddMessage('Executing: Calculate Statistics\n')
        arcpy.CalculateStatistics_management(sca)
        
        return sca

    def BaseflowCalculation(self, baseflow, flow_accumulation):

        arcpy.AddMessage("Starting daily baseflow calculation")

        baseflow = float(baseflow)
        arcpy.AddMessage("Todays calculated baseflow at the outlet is " + str(baseflow))

        # Calculate the cell of highest flow accumulation
        max_flow_accumulation = arcpy.GetRasterProperties_management(flow_accumulation, "MAXIMUM")
        max_flow_accumulation = float(max_flow_accumulation.getOutput(0)) 
        arcpy.AddMessage("The max flow accumulation is " + str(max_flow_accumulation))

        # Calculate the baseflow
        baseflow_raster = (flow_accumulation / max_flow_accumulation) * baseflow
 
        return baseflow_raster

