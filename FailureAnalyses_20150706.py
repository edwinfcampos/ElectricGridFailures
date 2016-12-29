#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:31:21 2015

This analyses the failure condition (yes/no) for infrastructure 
exposed to a natural hazard such as a tropical storm (flood and wind) or 
an earthquake, as well as a human threat.

Dependencies: EPfailureFunction() 

Issues: How to differentiate between a power plant and an substation (around line 165)? 
How to differentiate between outage and power drops (around line 176)?
Confirm if 'float(records_epbuses[ii][8])' corresponds to the Bus voltage in Kilovolts (around line 165).

Last modification: 2015/June/25
@author: edwincampos
"""
# Dependencies
import shapefile
import numpy as np
import EPfailure as EPf

# Variable inputs (to be modified by user). 
tc_namehint = 'al182012_2012102912_Flat2'
ep_namehint = ['buses', 'lines']
datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/HurricaneSandy_fromCraig/ExampleData'
outputplotname = 'FailureAnalyses'

# Function to test if a point is inside a polygon
# Source http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html
def point_in_poly(x,y,poly):

   # check if point is a vertex
   if (x,y) in poly: return "IN"

   # check if point is on a boundary
   for i in range(len(poly)):
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

# Read shape files for Electric Power Buses
myshp_epbuses = ep_namehint[0] # = ['buses', 'lines'] 
sf_epbu = shapefile.Reader(datadir+'/'+myshp_epbuses)
shapes_epbuses = sf_epbu.shapes()  # Geometry: shp file with geometries # Every geometry/shape must have a corresponding record
fields_epbuses = sf_epbu.fields    # Atributes: shx file with headers  # fields[ #ofrecords[:,i]+1, 4]
records_epbuses= sf_epbu.records() # Records: dbf file with contents # records[ #ofshapes, #offields[:,i] -1]
#print(fields_epbuses)
#[('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['Bus', 'C', 60, 0], ['Type', 'N', 11, 0], ['GenOutput', 'F', 19, 11], ['Load', 'F', 19, 11], ['VarLoad', 'F', 19, 11], ['GenRating', 'F', 19, 11], ['MinGen', 'F', 19, 11], ['Voltage', 'F', 19, 11], ['Angle', 'F', 19, 11], ['Latitude', 'F', 19, 11], ['Longitude', 'F', 19, 11], ['Name', 'C', 60, 0], ['Island', 'N', 11, 0], ['FinalGen', 'F', 19, 11], ['FinalLoad', 'F', 19, 11], ['Stable', 'C', 60, 0], ['Feasible', 'C', 60, 0]]

# Create a new field & record in the bus shapefiles: 'Outaged' = 'False'
fields_epbuses.append(['Outaged', 'C', 60, 0])
list2Bappended = [['False']] * (len(shapes_epbuses))  # Important, use [[]] to make a column array
records_epbuses = np.hstack((records_epbuses,list2Bappended))  #Append/concatenate the new column array into the records list, as the last column
    
# Read shape files for Electric Power Lines
myshp_eplines = ep_namehint[1] # = ['buses', 'lines'] 
sf_epli = shapefile.Reader(datadir+'/'+myshp_eplines)
shapes_eplines = sf_epli.shapes()  # shp file contents
fields_eplines = sf_epli.fields    # Headers
records_eplines= sf_epli.records() #dbf file contents
#print(fields_eplines)
#[('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['FromBus', 'N', 11, 0], ['ToBus', 'N', 11, 0], ['Circuit', 'N', 11, 0], ['Resistance', 'F', 19, 11], ['Reactance', 'F', 19, 11], ['ChargingR', 'F', 19, 11], ['CapacityPU', 'F', 19, 11], ['Branch', 'N', 11, 0], ['FromIsland', 'N', 11, 0], ['ToIsland', 'N', 11, 0], ['FlowMW', 'F', 19, 11], ['PctLoading', 'F', 19, 11], ['Status', 'C', 60, 0]]

# Read shape files for Tropical Cyclone Hazard
myshp_tc = tc_namehint
sf = shapefile.Reader(datadir+'/'+myshp_tc)
shapes = sf.shapes()   # shp file contents
fields = sf.fields     # Headers
records= sf.records()  #dbf file contents
#print(fields)
#[('DeletionFlag', 'C', 1, 0), ['OBJECTID', 'N', 9, 0], ['RADII', 'F', 19, 11], ['STORMID', 'C', 20, 0], ['BASIN', 'C', 20, 0], ['STORMNUM', 'F', 19, 11], ['VALIDTIME', 'C', 20, 0], ['SYNOPTIME', 'C', 20, 0], ['TAU', 'F', 19, 11], ['NE', 'F', 19, 11], ['SE', 'F', 19, 11], ['SW', 'F', 19, 11], ['NW', 'F', 19, 11], ['Shape_Leng', 'F', 19, 11], ['Shape_Area', 'F', 19, 11], ['InPoly_FID', 'N', 9, 0], ['SmoPgnFlag', 'N', 9, 0]]
synoptime = records[0][6]
validtime = records[0][5]
radii = float(records[0][1])  #Wind speed in knots
"""
[('DeletionFlag', 'C', 1, 0), 

['OBJECTID', 'N', 9, 0],

['RADII', 'F', 19, 11],
# The wind speed in knots associated with the bounding polygon. 
# 34 Knot- Tropical Storm Force Wind Radii.
# 50 Knot - 50 Knot Wind Radii
# 64 Knot - Hurricane Force Wind Radii

['STORMID', 'C', 20, 0],
# A unique character string that is specific to each tropical cyclone.  
# The string follows the pattern BBNNYYYY, where BB is AL for Atlantic, EP for East Pacific, 
# and CP for Central Pacific; NN is the sequential number of the storm during the season; 
# and YYYY is the year.

['BASIN', 'C', 20, 0], 
# The ocean where the tropical cyclone is located
# AL: Atlantic, EP: East Pacific

['STORMNUM', 'F', 19, 11],
# The sequential number of the tropical cyclone for a particular BASIN according 
# to the time that the first advisory is issued.
 
['VALIDTIME', 'C', 20, 0], 
# the time in which a forecast or warning is in effect, until it is updated or superseded by a new forecast issuance

['SYNOPTIME', 'C', 20, 0],
# Initial time in the forecast cycle in which a tropical cyclone's intensity and size are analyzed, occurring at 0000, 0600, 1200, or 1800 UTC.
 
['TAU', 'F', 19, 11],
# Number of hours from the forecast valid time for which a forecast is made.

['NE', 'F', 19, 11],
# The largest distance of wind speed in Nautical Miles in the NE (0 - 90 degree) quadrant.
 
['SE', 'F', 19, 11], 
# The largest distance of wind speed in Nautical Miles in the SE (90 - 180 degree) quadrant.

['SW', 'F', 19, 11], 
# The largest distance of wind speed in Nautical Miles in the SW (180 - 270 degree) quadrant.

['NW', 'F', 19, 11],
# The largest distance of wind speed in Nautical Miles in the NW (270 - 360 degree) quadrant.

['Shape_Leng', 'F', 19, 11], 

['Shape_Area', 'F', 19, 11], 

['InPoly_FID', 'N', 9, 0], 

['SmoPgnFlag', 'N', 9, 0]]

# Recall that records[shape index] [fields_index -1)]. 
# For example to obtain the wind speed (fields[1] = 'RADII', in kt) associated to the 1st shape (shapes[0]), write: 
print(records[0] [0])
# to obtain the forecast time (fields[5] = 'VALIDTIME', as YYYYMMDDHH in UTC) associated to the 1st shape (shapes[0]), write: 
print(records[0] [4])
"""

# Loop on the infrastructure buses and determine which will fail
# [('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['Bus', 'C', 60, 0], ['Type', 'N', 11, 0], ['GenOutput', 'F', 19, 11], ['Load', 'F', 19, 11], ['VarLoad', 'F', 19, 11], ['GenRating', 'F', 19, 11], ['MinGen', 'F', 19, 11], ['Voltage', 'F', 19, 11], ['Angle', 'F', 19, 11], ['Latitude', 'F', 19, 11], ['Longitude', 'F', 19, 11], ['Name', 'C', 60, 0], ['Island', 'N', 11, 0], ['FinalGen', 'F', 19, 11], ['FinalLoad', 'F', 19, 11], ['Stable', 'C', 60, 0], ['Feasible', 'C', 60, 0]]
# From Brian Craig's (Argonne-GSS) email on 2015 June 25: 'The load/gen and gen ratings are in MW. Not sure on the voltage, i would assume kV.'
for ii in xrange(len(shapes_epbuses)):
    busclas= records_epbuses[ii][0]  # Bus class
    busnum = float(records_epbuses[ii][1]) # Bus number
    busGnRt= float(records_epbuses[ii][6]) # Bus generation rating, in MegaWatts
    busVolt= float(records_epbuses[ii][8]) # Bus voltage, in Kilovolts?
    buslat = float(records_epbuses[ii][10]) # Bus latutude, in degrees from equator
    buslon = float(records_epbuses[ii][11]) # Bus longiture, in degrees from Greenwich
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
    #print(busGnRt,busVolt)
    
    # Find the wind speed at the bus site
    buswind_kt = 0.0 # Default value for wind speed at the bus site, in kt
    failure = False  # Default value for wind at the bus site, in miles per hour, corresponding to 1-min max. sustained wind at 10m agl. 
    # Find the Tropical Cyclone polygons corresponding to the hurricane wind
    # The points attribute contains a list of tuples containing an (x,y) coordinate for each point in the shape. 
    for jj in xrange(len(shapes)): 
        radii = float(records[jj][1])  #Wind speed in knots
        #tc_lon,tc_lat = shapes[jj].points     
        if point_in_poly(buslon,buslat,shapes[jj].points) == "IN":
            # Find the wind corresponding to the bus longitude,latutude
            buswind_kt =  max( buswind_kt, float(records[jj][1]) )  # radii = Wind speed in knots
            #print ii,buswind_kt
    buswind_mph = buswind_kt * 1.15077945 # Recall that 1 kt = 1.15077945 miles per hour
        
    # Run EPfailureFunction to determine is the bus will fail
    failure = EPf.EPfailureFunction(wind_mph=buswind_mph)
    print ii+1,', wind(mph):', buswind_mph, ', failure: ', failure,', '+busname[0:25] 
    if failure:
        #records_epbuses[ii][-3] = 'False'  # Recall that records_epbuses[ii][-3] = 'False'  # bus 'Stable'
        #records_epbuses[ii][-2] = 'False' # Recall that records_epbuses[ii][-2] = 'False' # bus 'Feasible'
        records_epbuses[ii][-1] = 'True' # Recall that records_epbuses[ii][-1] = 'False' # bus 'Outaged'
        #break
    #print ii+1,', wind(mph):', float(records[jj][1]), ', failure: ', failure,', '+busname[0:25] 
    #if failure: break            
            
# Update/Re-write the Buses shapefiles with the new failure criteria
# For details visit https://pypi.python.org/pypi/pyshp
w = shapefile.Writer(shapeType=shapefile.POINT)  # Recall that sf_epbu.shapeType = 1 ==> Point
w.fields = list(fields_epbuses)    # Atributes: shx file  #Do not use sf_epbu.fields, because it does not have the new 'Outaged' atribute
w._shapes = list(sf_epbu.shapes()) # Geometry: shp file
w.records = list(records_epbuses)  # Records: dbf file
#w.point(sf_epbu.shapes()) #shapes_epbuses)    # Geometry: shp file
#w.field(sf_epbu.fields)    # Atributes: shx file
#w.record(records_epbuses)  #Records: dbf file
print 'Writing output shapefiles at... '+datadir+'/'+myshp_epbuses+'_analyzed.*'
w.save(datadir+'/'+myshp_epbuses+'_analyzed')