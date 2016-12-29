#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:31:21 2015

This analyses the failure condition (yes/no) for infrastructure 
exposed to a natural hazard such as a tropical cyclone (Hurricane flood and wind) 
or an earthquake, as well as a human threat.

Valid infrastructures:
'npgg' : Natural Gas Processing Plant
'npp' : Nuclear Power Plant
'epp': Electric Power Plant
'eps' : Electric Power Substation
'eptl' : Electric Power Transmission Lines

Inputs: GIS Shapefiles with infrastructures and hazards information, ASCII file with ASCE7 building code winds at the infrastructure sites
Outputs: GIS Shapefiles with additional 'Outaged' field, indicating infrastructure failure (Outaged=True) or noFailure (Outaged=False)

Dependencies: IIF_failure.py

Issues: Add hurricane flood hazards (see lines 277, 369, and 410)

Last modification: 2015/Sep/2
Author: Edwin Campos, ecampos@anl.gov, edwinfcampos@aol.com
"""

###### DEPENDENCIES ##########################################################################################
import time
start_time = time.time()
import shapefile
import numpy as np
import IIF_failure as IIFf


###### VARIABLE INPUTS TO BE MODIFIED BY USER ##########################################################################################

# Hurricane (Tropical Cyclone) Hazard variables
tc_datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneIvan'
tc_namehint = 'Ivan_windswath_out'  # From Hurrevac

# Electric Power Infrastructure variables
ep_datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneIvan'
ep_namehint = ['buses', 'lines']
ASCE7_epbuses_file = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/codes/ASCEwinds_getatAssets_epbusesFL.dat'
ASCE7_eplines_file = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/codes/ASCEwinds_getatAssets_eplinesFL.dat'

# Natural Gas Infrastructure variables
'''
ng_datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromRobinson_NGPP/fl_ngpp'
ng_namehint = 'ngpp_draft_FL'
ASCE7_ngpp_file = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/codes/ASCEwinds_getatAssets_ngppFL.dat'
'''
ng_datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromRobinson_NGPP/ngpp_east'
ng_namehint = 'ngpp_east'
ASCE7_ngpp_file = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/codes/ASCEwinds_getatAssets_ngppEast.dat'


want2printFailures  = 1  # 1 --> Will print in console the failure status for each asset; 2 --> Will print only basic information of program run

''' TO BE DELETED
tc_namehint = 'al182012_2012102912_Flat2'
ep_namehint = ['buses', 'lines']
datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/HurricaneSandy_fromCraig/ExampleData'
#out_datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/codes'
#outputplotname = 'FailureAnalyses_Ivan2004'
outputplotname = 'FailureAnalyses'
'''


##### INTERNAL FUNCTIONS/METHODS ##########################################################################################

# READ THE ASCE7 WINDGUST LOAD FROM A PREDETERMINED FILE
# The predetermined file 'which_ASCE7_file' was obtained by running ASCEwinds_getatAssets.py, with the same 'inputfile' there as in 'ng_datadir+/+ng_namehint' here
def readASCE7winds(which_ASCE7_file,ilon,ilat):
    asce_705_mph =float('nan')     # Default value
    asce_710_RCiii_mph = float('nan')  # Default value
    f = open(which_ASCE7_file, 'r')  #Open file for reading only
    # Read Header lines in file
    line = f.readline() # "Data downloaded from 'http://windspeed.atcouncil.org' on "+ time.strftime("%c %Z")+', where each column corresponds to...\n'   
    line = f.readline() # 'Latitude(degrees, positive north)\n' 
    line = f.readline() # 'Longitude(degrees, positive east)\n' 
    line = f.readline() # 'ASCE 7-05 Wind speeds (50-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)\n' 
    line = f.readline() # 'ASCE 7-10 Wind speeds (Risk Category III-IV: >1700-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)\n' 
    line = f.readline() # 'Asset name\n'    
    # Read the rest of the file
    for line in f.readlines():  
        #print line   # This line is used for TEST only
        #lat_buff, lon_buff, asce_705_buff, asce_710_RCiii_buff, name_buff = line.split('    ')  # This line does not work when the name is given as blank spaces
        splitted_line = line.split('    ')
        lat_buff = splitted_line[0]
        lon_buff = splitted_line[1]
        asce_705_buff = splitted_line[2]
        asce_710_RCiii_buff= splitted_line[3]
        #name_buff = splitted_line[4]
        if (lat_buff == str(ilat)) and (lon_buff == str(ilon)): 
            #print lat_buff, lon_buff, asce_705_buff, asce_710_RCiii_buff, name_buff
            asce_705_mph = int(asce_705_buff) 
            asce_710_RCiii_mph = int(asce_710_RCiii_buff)    
            break  # Terminate the for loop ==> stop reading lines            
    f.close()
    return (asce_705_mph, asce_710_RCiii_mph)


# TEST IF A POINT IS INSIDE A POLYGON
# Source http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html
def point_in_poly(x,y,poly):   
   if (x,y) in poly: return "IN"  # check if point is a vertex   
   for i in range(len(poly)):   # check if point is on a boundary
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return "IN"      
   n = len(poly)
   inside = False
   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y
   if inside: return "IN"
   else: return "OUT"


# FIND HURRICANE SUSTAINED WINDS GIVEN A PARTICULAR LOCATION
def findHurricaneWind(GISshapes,GISrecords,ilon,ilat):
# Find the wind speed at the bus site
    buswind = 0.0 # Default value for wind speed at the bus site, in kt
    ##failure = False  # Default value for wind at the bus site, in miles per hour, corresponding to 1-min max. sustained wind at 10m agl. 
    # Find the Tropical Cyclone polygons corresponding to the hurricane wind
    # The points attribute contains a list of tuples containing an (x,y) coordinate for each point in the shape. 
    for jj in xrange(len(GISshapes)): 
        #radii = float(GISrecords[jj][1])  #Wind speed in knots
        ##tc_lon,tc_lat = GISshapes[jj].points     
        if point_in_poly(ilon,ilat,GISshapes[jj].points) == "IN":
            # Find the wind corresponding to the bus longitude,latutude
            #buswind_kt =  max( buswind_kt, float(GISrecords[jj][1]) )  # radii = float(records[ii][1]) = Wind speed in knots
            buswind =  max( buswind, float(GISrecords[jj][0]) ) # If fields_tc[last shape] [0] equals 'ID', then records_tc[-1] [0] = wind speed every 2 mhp
            #print ii,buswind
    return buswind  # in the units of the GISshapes and GISrecords


##### INGEST SHAPE FILES ##########################################################################################

# Read shape files for NATURAL GAS Buses (for now the only assets are Processing Plants)
myshp_ngbuses = ng_datadir+'/'+ng_namehint # 
sf_ngbu = shapefile.Reader(myshp_ngbuses)
shapes_ngbuses = sf_ngbu.shapes()  # Geometry: shp file with geometries # Every geometry/shape must have a corresponding record
fields_ngbuses = sf_ngbu.fields    # Atributes: shx file with headers  # fields[ #ofrecords[:,i]+1, 4]
records_ngbuses= sf_ngbu.records() # Records: dbf file with contents # records[ #ofshapes, #offields[:,i] -1]   # This particular Natural Gas Processing Plant *.dbf file have the records as a LIST
# Verify if the 'outage' field already exists
if ('OUTAGE' in fields_ngbuses[-1]) or ('Outage' in fields_ngbuses[-1]) or ('outage' in fields_ngbuses[-1]): 
    NeedNewOutageField_ngbuses = 0    # This code does NOT NEED to create a new Outage field and record
else:
    NeedNewOutageField_ngbuses = 1    # This code NEEDS to create a new Outage field and record
numberof_ngbuses = len(shapes_ngbuses)
#print(fields_ngbuses)
#[('DeletionFlag', 'C', 1, 0), ['OBJECTID', 'N', 9, 0], ['PROCID', 'C', 15, 0], ['NAME', 'C', 120, 0], ['COMPNAME', 'C', 80, 0], ['TYPE', 'C', 125, 0], ['FACADDR', 'C', 180, 0], ['CITY', 'C', 75, 0], ['COUNTY', 'C', 50, 0], ['COUNTYFIPS', 'C', 5, 0], ['STATE', 'C', 2, 0], ['ZIP', 'C', 7, 0], ['ZIP4', 'C', 4, 0], ['COUNTRY', 'C', 15, 0], ['LATITUDE', 'F', 19, 11], ['LONGITUDE', 'F', 19, 11], ['SOURCE', 'C', 254, 0], ['SOURCE_DAT', 'D', 8, 0], ['VAL_METHOD', 'C', 150, 0], ['VAL_DATE', 'D', 8, 0], 
#['POSREL', 'C', 50, 0], ['NAICS_CODE', 'C', 15, 0], ['NAICS_DESC', 'C', 150, 0], ['WEBSITE', 'C', 100, 0], ['STATUS', 'C', 12, 0], ['TELEPHONE', 'C', 15, 0], ['FAC_EMAIL', 'C', 50, 0], ['CONTACT', 'C', 50, 0], ['CONTITLE', 'C', 50, 0], ['CONEMAIL', 'C', 50, 0], ['OPERATOR', 'C', 80, 0], ['OPERADDR', 'C', 60, 0], ['OPERCITY', 'C', 20, 0], ['OPERSTATE', 'C', 4, 0], ['OPERZIP', 'C', 20, 0], ['OPERPHONE', 'C', 15, 0], ['OPERURL', 'C', 100, 0], ['GASCAP', 'F', 19, 11], ['PROCAMTLBS', 'F', 19, 11], 
#['BASIN', 'C', 50, 0], ['PLANTFLOW', 'F', 19, 11], ['BTUCONTENT', 'F', 19, 11], ['GASSTORCAP', 'F', 19, 11], ['LIQSTORCAP', 'F', 19, 11], ['RMP_ID', 'C', 10, 0], ['EPA_ID', 'C', 12, 0], ['NUMBERFTES', 'F', 19, 11]]


# Read shape files for ELECTRIC POWER BUSES
myshp_epbuses = ep_datadir+'/'+ep_namehint[0] # Recall that ep_namehint = ['buses', 'lines'] 
sf_epbu = shapefile.Reader(myshp_epbuses)
shapes_epbuses = sf_epbu.shapes()  # Geometry: shp file with geometries # Every geometry/shape must have a corresponding record
fields_epbuses = sf_epbu.fields    # Atributes: shx file with headers  # fields[ #ofrecords[:,i]+1, 4]
records_epbuses= sf_epbu.records() # Records: dbf file with contents # records[ #ofshapes, #offields[:,i] -1]
# Verify if the 'outage' field already exists
if ('OUTAGE' in fields_epbuses[-1]) or ('Outage' in fields_epbuses[-1]) or ('outage' in fields_epbuses[-1]): 
    NeedNewOutageField_epbuses = 0    # This code does NOT NEED to create a new Outage field and record
else:
    NeedNewOutageField_epbuses = 1    # This code NEEDS to create a new Outage field and record
numberof_epbuses = len(shapes_epbuses)
#print(fields_epbuses)
#[('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['Bus', 'C', 60, 0], ['Type', 'N', 11, 0], ['GenOutput', 'F', 19, 11], ['Load', 'F', 19, 11], ['VarLoad', 'F', 19, 11], ['GenRating', 'F', 19, 11], ['MinGen', 'F', 19, 11], ['Voltage', 'F', 19, 11], ['Angle', 'F', 19, 11], ['Latitude', 'F', 19, 11], ['Longitude', 'F', 19, 11], ['Name', 'C', 60, 0], ['Island', 'N', 11, 0], ['FinalGen', 'F', 19, 11], ['FinalLoad', 'F', 19, 11], ['Stable', 'C', 60, 0], ['Feasible', 'C', 60, 0], ['outage', 'C', 5, 0]]
# In the field format 'C' is for strings, 'N' is for integers, and 'F' is for float numbers
# From Brian Craig's (Argonne-GSS) email on 2015 June 25: 'The load/gen and gen ratings are in MW.'

    
# Read shape files for ELECTRIC POWER LINES
myshp_eplines = ep_datadir+'/'+ep_namehint[1] # Recall that ep_namehint = ['buses', 'lines'] 
sf_epli = shapefile.Reader(myshp_eplines)
shapes_eplines = sf_epli.shapes()  # shp file contents
fields_eplines = sf_epli.fields    # Headers
records_eplines= sf_epli.records() #dbf file contents
# Verify if the 'outage' field already exists
if ('OUTAGE' in fields_eplines[-1]) or ('Outage' in fields_eplines[-1]) or ('outage' in fields_eplines[-1]): 
    NeedNewOutageField_eplines = 0    # This code does NOT NEED to create a new Outage field and record
else:
    NeedNewOutageField_eplines = 1    # This code NEEDS to create a new Outage field and record
numberof_eplines = len(shapes_eplines)
#print(fields_eplines)
#[('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['FromBus', 'N', 11, 0], ['ToBus', 'N', 11, 0], ['Circuit', 'N', 11, 0], ['Resistance', 'F', 19, 11], ['Reactance', 'F', 19, 11], ['ChargingR', 'F', 19, 11], ['CapacityPU', 'F', 19, 11], ['Branch', 'N', 11, 0], ['FromIsland', 'N', 11, 0], ['ToIsland', 'N', 11, 0], ['FlowMW', 'F', 19, 11], ['PctLoading', 'F', 19, 11], ['Status', 'C', 60, 0], ['outage', 'C', 5, 0]]


# Read shape files for HURRICANE Hazard
myshp_tc = tc_datadir+'/'+tc_namehint
sf = shapefile.Reader(myshp_tc)
shapes_tc = sf.shapes()   # shp file contents
fields_tc = sf.fields     # Headers
records_tc= sf.records()  #dbf file contents
#print(fields_tc)
#[('DeletionFlag', 'C', 1, 0), ['OBJECTID', 'N', 9, 0], ['RADII', 'F', 19, 11], ['STORMID', 'C', 20, 0], ['BASIN', 'C', 20, 0], ['STORMNUM', 'F', 19, 11], ['VALIDTIME', 'C', 20, 0], ['SYNOPTIME', 'C', 20, 0], ['TAU', 'F', 19, 11], ['NE', 'F', 19, 11], ['SE', 'F', 19, 11], ['SW', 'F', 19, 11], ['NW', 'F', 19, 11], ['Shape_Leng', 'F', 19, 11], ['Shape_Area', 'F', 19, 11], ['InPoly_FID', 'N', 9, 0], ['SmoPgnFlag', 'N', 9, 0]]
##synoptime = records[0][6]
##validtime = records[0][5]
##radii = float(records[0][1])  #Wind speed in knots
# If fields_tc[last shape] [0] equals 'ID', then records_tc[-1] [0] = wind speed every 2 mhp


##### ADD OUTAGED FIELD IN INFRASTRUCTURE SHAPE FILES ##########################################################################################

# Create a new field & record in the NATURAL GAS bus shapefiles: 'Outaged' = 'False'
if NeedNewOutageField_ngbuses == 1:    
    fields_ngbuses.append(['outage', 'C', 5, 0])
    ngitem2Bappended = 'False'
    for nn in xrange(len(shapes_ngbuses)):
        records_ngbuses[nn].append(ngitem2Bappended)  # This is appending an ITEM at the end of the LIST. Recall that the GIS shapefiles for Natural Gas have its records as a LIST.


# Create a new field & record in the ELECTRIC POWER Bus shapefiles: 'Outaged' = 'False'
if NeedNewOutageField_epbuses == 1:    
    fields_epbuses.append(['outage', 'C', 5, 0])
    eplist2Bappended = [['False']] * (len(shapes_epbuses))  # Important, use [[]] to make a column ARRAY
    records_epbuses = np.hstack((records_epbuses,eplist2Bappended))  # This is appending/concatenating the new column ARRAY into the records ARRAY, as the last column. Recall that the GIS shapefiles for Electric Power have its records as an ARRAY.


# Create a new field & record in the ELECTRIC POWER Lines shapefiles: 'Outaged' = 'False'
if NeedNewOutageField_eplines == 1:    
    fields_eplines.append(['outage', 'C', 5, 0])
    eplist2Bappended = [['False']] * (len(shapes_eplines)) 
    records_eplines = np.hstack((records_eplines,eplist2Bappended))  # This is appending/concatenating the new column ARRAY into the records ARRAY, as the last column. Recall that the GIS shapefiles for Electric Power have its records as an ARRAY.

''' TO BE DELETED
if len(shapes_ngbuses) == 1:
    ngitem2Bappended = 'False'
    records_ngbuses[0].append(ngitem2Bappended)  # This is appending nglist2Bappended at the end of the list
    #records_ngbuses.insert(len(records_ngbuses),nglist2Bappended)
else:
    ngitem2Bappended = 'False'
    for nn in xrange(len(shapes_ngbuses)):
        records_ngbuses[nn].append(ngitem2Bappended) 
    #nglist2Bappended = [['False']] * (len(shapes_ngbuses))  # Important, use [[]] to make a column array
    #records_ngbuses = np.hstack((records_ngbuses,nglist2Bappended))  #Append/concatenate the new column array into the records list, as the last column
'''


##### LOOP ON THE INFRASTRUCTURE ASSETS AND DETERMINE WHICH WILL FAIL ##########################################################################################

# Loop through the Natural Gas assets
if want2printFailures == 2:
    print '----------------------------------- ANALYZING '+str(numberof_ngbuses)+' NATURAL GAS BUSES -----------------------------------'
for ii in xrange(len(shapes_ngbuses)):
    shape = shapes_ngbuses[ii]
    if len(shape.points) == 1:   # This is for cases where the shape correspond to a single lat,lon point
        [[lons,lats]] = shape.points  # Define latitudes and longitudes for a given shape    
        ilat = lats
        ilon = lons        
        # Read value of ASCE-7 windgust at asset site       
        asce_705_mph, asce_710_RCiii_mph = readASCE7winds(ASCE7_ngpp_file,ilon,ilat)         
        # Obtain value of Hurricane sustained winds at asset site
        hazard_wind_mph = findHurricaneWind(shapes_tc,records_tc,ilon,ilat)   # Validation: For the Hurricane Ivan Adv.#53 and the Nat. Gas Processing Plant, hazard_wind_mph = 88.0
        #hazard_wind_mph = 150.0  # This line would be used for TEST only
        
        # Compute "floodlvl_m" here, and pass the value into IIFf.failureFunction   
    
        # Run failureFunction to determine if the bus will fail
        failure = IIFf.failureFunction(asset='ngpp', wind_mph=hazard_wind_mph, gust_threshold_mph=asce_705_mph )
    
        if want2printFailures == 1:
            #Typically in a hurricane environment, the value of the maximum 3 second gust over a 1 minute period 
            # is on the order of 1.3 times (or 30% higher than) than the 1 min sustained wind. 
            # Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html        
            hazard_gust_mph = 1.3 * hazard_wind_mph    # Recall that 1 mph wind = 1.3 mph gust
            print ii+1,', hurricane gust(mph):', hazard_gust_mph,', ASCE7-05 gust(mph):', asce_705_mph, ', failure: ', failure,', ', records_ngbuses[ii][2]
    
        if failure:
            records_ngbuses[ii][-1] = 'True' # Recall that records_epbuses[ii][-1] = 'False' # bus 'outage'
            #break
    #print ii+1,', hurricane gust(mph):', hazard_gust_mph,', ASCE7-05 gust(mph):', asce_705_mph, ', records_ngbuses[ii][-1]: ', records_ngbuses[ii][-1],', ', records_ngbuses[ii][2]
    #if failure: break            


# Loop through the Electric Power Buses
if want2printFailures == 2:
    print '----------------------------------- ANALYZING '+str(numberof_epbuses)+' ELECTRIC POWER BUSES -----------------------------------'
n_epp_generators = 0  # Number of Electric Power Plants (power generators)
n_eps_loads = 0       # Number of Electric Power Substations (power loads)
for ii in xrange(len(shapes_epbuses)):
    busclas= records_epbuses[ii][0]  # Bus class, e.g., busclas= '                                                            '
    busnum = float(records_epbuses[ii][1]) # Bus number, e.g., busnum = 1.0
    bustype= int(records_epbuses[ii][2]) # Bus type, where 2=Generator, 3=Load, 1=SlackGenerator (Slack Generators are treated as Generators by EPfast)   As per Brian Craig email to Mark Hereld and Edwin Campos on 2015 Aug 19
    busGenOut=float(records_epbuses[ii][3]) # Power Generation, for example busGenOut=296.152, in MW, as per Brian Craig's (Argonne-GSS) email to Edwin Campos on 2015 June 25
    busLoad= float(records_epbuses[ii][4]) # Power load, for example busLoad=0.00000000000e+000, in MW, as per Brian Craig's (Argonne-GSS) email to Edwin Campos on 2015 June 25
    busGnRt= float(records_epbuses[ii][6]) # Bus generation rating, in MegaWatts, also known as Name Plate Capacity (Brian Craig and Edgar Portante, Personnal Communication to Edwin Campos on 2015 July 15). For example, busGnRt = 600.0
    busVolt= float(records_epbuses[ii][8]) # Bus voltage, in Kilovolts (Edgar Portante, Personal Communication to Edwin Campos on 2015 July 15)
    #buslat = float(records_epbuses[ii][10]) # Bus latutude, in degrees from equator. It is best to read the latitudes from the *.shp file, such as [[lons,lats]] = shapepoints
    #buslon = float(records_epbuses[ii][11]) # Bus longiture, in degrees from Greenwich. It is best to read the longitudes from the *.shp file, such as [[lons,lats]] = shapepoints
    busname= records_epbuses[ii][12] # Bus site name, state
    stable = records_epbuses[ii][-3] # bus stability, 'True' or 'False'
    feasibl= records_epbuses[ii][-2] # bus feasibility, 'True' or 'False'    
    outaged= records_epbuses[ii][-1] # bus feasibility, 'True' or 'False'
    # From Brian Craig's email (Argonne's GSS division) on 2015 June 25: 
    # The stable and feasible are parameters from the islanding analysis.
    # Feasible false means the linear solver could not converge, meaning you have bad data.  
    # Stable true means that the bus is in an island that has settled and no longer needs to be simulated.
    
    # From Brian Craig's email (Argonne's GSS division) on 2015 June 25: 
    # Remember there's a difference between an outaged bus and a bus whose generation drops to 0.
    # Outage means the bus is dead (destroyed/damaged).  The bus is part of the connectivity. Thus the lines connecting the bus are also out.
    # If say the generation or load level of a bus drops to zero, it can still be used as an interconnect.  It just means the customers or power plant are inoperative. 
    
    '''
    Look in Hazus-MH 2.1 CDMS Data Dictionary for p.92 (https://www.fema.gov/media-library/assets/documents/24609?id=5120)
    (For Hurricanes & winds, infrastructure types depend on building # of stories, see Table D.45 in p. 122)
    Transmission Substations
    ESSL Low Voltage (115 KV) Substation [different combinations for with or without anchored components]
    ESSM Medium Voltage (230 KV) Substation [different combinations for with or without anchored
    ESSH High Voltage (500 KV) Substation [different combinations for with or without anchored components]
    Distribution Circuits
    EDC Distribution Circuits (either Seismically Designed Components or Standard Components)
    Generation Plants
    EPPL Large Power Plants ( > 500 MW ) [different combinations for with or without anchored components]
    EPPM Medium Power Plants ( 100 - 500 MW ) [different combinations for with or without anchored
    EPPS Small Power Plants ( < 100 MW ) [different combinations for with or without anchored components]
    '''
    
    # Determine if the current bus shape corresponds to a Power Plant or Substation    
    # As per Brian Craig (EPFast software developer at GSS) email to Mark Hereld and Edwin Campos on 2015 Aug 19, and 
    # Edgar Portante (infrastructure analyst at GSS) email to Edwin Campos on 2015 Sep 2
    if (busGenOut - busLoad) > 0 : 
        which_asset = 'epp'  # Electric Power Plant (Generator in EPFast?)
        n_epp_generators = n_epp_generators + 1.0
    else:
        which_asset = 'eps'  # Electric Power Substation (Load in EPFast?) 
        n_eps_loads = n_eps_loads + 1.0
    '''
    # Another way to determine if the bus is a Power Plant or Substation is...
    if bustype == 1:
        print which_asset+', bustype = Slack Generator'  # Power Plant
    elif bustype == 2:
        print which_asset+', bustype = Generator'        # Power Plant
    elif bustype == 3:
        print which_asset+', bustype = Load'             # Substation
    else:
        print 'bustype ='+str(bustype)
    # We may also use busGnRt and busVolt to determine if the bus is a Power Plant or Substation
    '''
    
    shape = shapes_epbuses[ii]
    if len(shape.points) == 1:   # Making sure that this is for cases where the shape correspond to a single lat,lon point
        [[lons,lats]] = shape.points  # Define latitudes and longitudes for a given shape    
        ilat = lats
        ilon = lons        
        # Read value of ASCE-7 windgust at asset site       
        asce_705_mph, asce_710_RCiii_mph = readASCE7winds(ASCE7_epbuses_file,ilon,ilat)         
        # Obtain value of Hurricane sustained winds at asset site
        hazard_wind_mph = findHurricaneWind(shapes_tc,records_tc,ilon,ilat)   # Validation: For the Hurricane Ivan Adv.#53 and the Nat. Gas Processing Plant, hazard_wind_mph = 88.0
        #hazard_wind_mph = 150.0  # This line would be used for TEST only
        
        # Compute "floodlvl_m" here, and pass the value into IIFf.failureFunction    
    
        # Run failureFunction to determine if the bus will fail
        failure = IIFf.failureFunction(asset=which_asset, wind_mph=hazard_wind_mph, gust_threshold_mph=asce_705_mph )
    
        if want2printFailures == 1:
            #Typically in a hurricane environment, the value of the maximum 3 second gust over a 1 minute period 
            # is on the order of 1.3 times (or 30% higher than) than the 1 min sustained wind. 
            # Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html        
            hazard_gust_mph = 1.3 * hazard_wind_mph    # Recall that 1 mph wind = 1.3 mph gust  
            print ii+1,', hurricane gust(mph):', hazard_gust_mph,', ASCE7-05 gust(mph):', asce_705_mph, ', failure: ', failure,', '+busname[0:25]
    
        if failure:
            #records_epbuses[ii][-3] = 'False'  # Recall that records_epbuses[ii][-3] = 'False'  # bus 'Stable'
            #records_epbuses[ii][-2] = 'False' # Recall that records_epbuses[ii][-2] = 'False' # bus 'Feasible'
            records_epbuses[ii][-1] = 'True' # Recall that records_epbuses[ii][-1] = 'False' # bus 'outage'

if want2printFailures == 2:
    print 'Number of Electric Power Plants (power generators) = '+ str(n_epp_generators)
    print 'Number of Electric Power Substations (power loads) = '+ str(n_eps_loads)          

# Loop through the Electric Power Lines
if want2printFailures == 2:
    print '----------------------------------- ANALYZING '+str(numberof_eplines)+' ELECTRIC POWER LINES -----------------------------------'
for ii in xrange(len(shapes_eplines)):    #for shape,record in shapes,records:
    shape = shapes_eplines[ii]    
    failure = False    
    if len(shape.points) != 1:  # This is for cases where the shape correspond to a line or a polygon
        lons_lats_list = shape.points
        lons_lats_array = np.array(lons_lats_list)
        lons = lons_lats_array[:,0]
        lats = lons_lats_array[:,1]
        asset_name = 'Branch # '+str(records_eplines[ii] [8])  # Recall that records_eplines[ii] [8] corresponds to fields_eplines[ii] [8] = ['Branch', 'N', 11, 0], which is the branch number, given as an integer
        for ilat in lats:
            for ilon in lons:
                #print(ilon,ilat,asset_name)
                #f.write( str(ii)+'    '+str(ilat)+'    '+str(ilon)+'    '+asset_name+'\n')  # TEST: Write Data
            
                # Read value of ASCE-7 windgust at asset site       
                asce_705_mph, asce_710_RCiii_mph = readASCE7winds(ASCE7_eplines_file,ilon,ilat)         
                # Obtain value of Hurricane sustained winds at asset site
                hazard_wind_mph = findHurricaneWind(shapes_tc,records_tc,ilon,ilat)   # Validation: For the Hurricane Ivan Adv.#53 and the Nat. Gas Processing Plant, hazard_wind_mph = 88.0
                #hazard_wind_mph = 150.0  # This line would be used for TEST only
            
                # Compute "floodlvl_m" here, and pass the value into IIFf.failureFunction    
    
                # Run failureFunction to determine if the bus will fail
                failure = IIFf.failureFunction(asset='eptl', wind_mph=hazard_wind_mph, gust_threshold_mph=asce_705_mph )
    
                if want2printFailures == 1:
                    #Typically in a hurricane environment, the value of the maximum 3 second gust over a 1 minute period 
                    # is on the order of 1.3 times (or 30% higher than) than the 1 min sustained wind. 
                    # Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html        
                    hazard_gust_mph = 1.3 * hazard_wind_mph    # Recall that 1 mph wind = 1.3 mph gust  
                    print ii+1,', hurricane gust(mph):', hazard_gust_mph,', ASCE7-05 gust(mph):', asce_705_mph, ', failure: ', failure,', '+asset_name
    
                if failure:  
                    records_eplines[ii][-1] = 'True' # Recall that records_eplines[ii][-1] = 'False' # bus 'Outaged'
                    break  # Terminate the "for ilon" loop 
            if failure:
                break  # Terminate the "for ilat" loop and start analysing the next shape (the next iteration in the for ii loop)


##### GENERATE OUTPUTS ##########################################################################################
'''
Recall that the set of 3 GIS shapefiles is called a layer:
.shp – geographical information (latitudes and longitudes)
.dbf – dbase III table containing attribute information for the shapes in the .shp file
.shx – shape index file, contains the offset of the records in the .shp file (for random access reading)
For details visit https://pypi.python.org/pypi/pyshp
'''

# Update/Re-write the Natural Gas Buses shapefiles with the new failure criteria
# For details visit https://pypi.python.org/pypi/pyshp
w = shapefile.Writer(shapeType=shapefile.POINT)  # Recall that sf_ngbu.shapeType = 1 ==> Point
w.fields = list(fields_ngbuses)    # Atributes: shx file  #Do not use sf_ngbu.fields, because it does not have the new 'Outaged' atribute
w._shapes = list(sf_ngbu.shapes()) # Geometry: shp file
w.records = list(records_ngbuses)  # Records: dbf file
if want2printFailures == 2: 
    print 'Writing NGBuses output shapefiles at... '+myshp_ngbuses+'_analyzed.*'
w.save(myshp_ngbuses+'_analyzed')


# Update/Re-write the Electric Power Buses shapefiles with the new failure criteria
w = shapefile.Writer(shapeType=shapefile.POINT)  # Recall that sf_epbu.shapeType = 1 ==> Point
w.fields = list(fields_epbuses)    # Atributes: shx file  #Do not use sf_epbu.fields, because it does not have the new 'Outaged' atribute
w._shapes = list(sf_epbu.shapes()) # Geometry: shp file
w.records = list(records_epbuses)  # Records: dbf file
#w.point(sf_epbu.shapes()) #shapes_epbuses)    # Geometry: shp file
#w.field(sf_epbu.fields)    # Atributes: shx file
#w.record(records_epbuses)  #Records: dbf file
if want2printFailures == 2: 
    print 'Writing EPbuses output shapefiles at... '+myshp_epbuses+'_analyzed.*'
w.save(myshp_epbuses+'_analyzed')


# Update/Re-write the Electric Power Lines shapefiles with the new failure criteria
w = shapefile.Writer(shapeType=shapefile.POLYGON)  # Recall that sf_eplines.shapeType = 2 ==> Polygon
w.fields = list(fields_eplines)    # Atributes: shx file  #Do not use sf_epbu.fields, because it does not have the new 'Outaged' atribute
w._shapes = list(sf_epli.shapes()) # Geometry: shp file
w.records = list(records_eplines)  # Records: dbf file
#w.point(sf_epbu.shapes()) #shapes_epbuses)    # Geometry: shp file
#w.field(sf_epbu.fields)    # Atributes: shx file
#w.record(records_epbuses)  #Records: dbf file
if want2printFailures == 2: 
    print 'Writing EPlines output shapefiles at... '+myshp_eplines+'_analyzed.*'
w.save(myshp_eplines+'_analyzed')

elapsed_time = (time.time() - start_time)
if (want2printFailures == 2) or (want2printFailures == 1):
    print 'Program wall-clock time = '+str(elapsed_time)+' seconds'

'''
******************************************************************************
                         ***LICENSE NOTICE***
******************************************************************************
Copyright (c) 2015: Open Source Software Distribution MIT License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
******************************************************************************
'''