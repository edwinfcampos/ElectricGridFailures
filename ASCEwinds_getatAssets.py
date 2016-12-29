#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:38:27 2015

This code retrieves maximum windspeed loads as a function of building geolocation
from construction codes ASCE 7-10 and ASCE 7-05.

Inputs: Shapefiles for critical infrastructures (e.g., Electric Power grid, Natural Gas network, etc.)

References: http://windspeed.atcouncil.org

Dependencies: shapefile, numpy, time, urllib2, and urllib 

Issues: None

Last modification: 2015/Sep/2
Author: Edwin Campos, ecampos@anl.gov, edwinfcampos@aol.com
"""

###### VARIABLE INPUTS TO BE MODIFIED BY USER ##########################################################################################

which_inputfile = 3  # Valid values 0, 1, 2, and 3
outputfile = './ASCEwinds_getatAssets.dat' 

if which_inputfile == 0 : # It takes 2h17min with the bbox and resol_lat_lon settings below
    inputfile = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneIvan/lines'  # Electric Power Lines: Shapefiles WITHOUT file extension
elif which_inputfile == 1 :
    inputfile = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneIvan/buses'  # Electric Power Buses: Shapefiles WITHOUT file extension
elif which_inputfile == 2:
    inputfile = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromRobinson_NGPP/ngpp_east/ngpp_east'  # Natural Gas Processing Plant near the USA Gulf of Mexico coast: Shapefiles WITHOUT file extension
elif which_inputfile == 3:
    inputfile = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromRobinson_NGPP/fl_ngpp/ngpp_draft_FL'  # Natural Gas Processing Plant in Florida: Shapefiles WITHOUT file extension
    
# CONSTANT 
which_url = 'http://windspeed.atcouncil.org/domains/atcwindspeed/process/'


###### DEPENDENCIES ##########################################################################################

import shapefile  #http://gis.humboldt.edu/OLM/GSP_318/09_3_ShapefilePY.html or https://code.google.com/p/pyshp/wiki/PyShpDocs
import numpy as np
import time
import urllib2
import urllib


##### INTERNAL FUNCTIONS/METHODS ##########################################################################################

# INTERNAL FUNCTION TO INTERROGATE URL 
def getASCE7winds(url,ilon,ilat):       
        # Input values: Desired lat, Lon
        requests = {}  # Define list with website access parameters
        requests['dec'] ='1'   # This allows display of Lat and Lon values in html file of specified url
        requests['zoom'] = '4' # This determines the size of the Google map in specified url
    
        requests['latt'] = str(ilat)  # '41.7152'
        requests['longt'] = str(ilon) # '-87.9835'
        #requests['dec'] ='1'   # This allows display of Lat and Lon values in html file
        #requests['zoom'] = '4' # This determines the size of the Google map

        url_values = urllib.urlencode(requests)
        #print url_values  # The order may differ. 
        #url = 'http://windspeed.atcouncil.org/domains/atcwindspeed/process/'
        full_url = url + '?' + url_values
        #print full_url

        response = urllib2.urlopen(full_url)
        output_url_string = response.geturl()
        #print output_url_string
        ##print response.read()  # This will print the entire htlm code in the file.

        output_url_list = output_url_string.split('&')
        #which_string = ['asce_705', 'risk_category_iii']
        for item in output_url_list:
            if (item.find("asce_705") != -1) and (len(item) <= 9):
                #print '1:'+item
                asce_705_mph = 'NaN' #float('NaN')     # Not-a-Number value because the point is not over land
            elif (item.find("asce_705") != -1) and (len(item) > 9):
                #print '2:'+item
                asce_705_mph = item[9:] #float(item[9:])  # Wind Design Load according to ASCE 7-05 (90-years Mean Recurrence Interval) construction code, in miles per hour
            elif (item.find("risk_category_iii") != -1) and (len(item) <= 18): 
                #print '3:'+item
                asce_710_RCiii_mph = 'NaN'     # Not-a-Number value because the point is not over land
            elif (item.find("risk_category_iii") != -1) and (len(item) > 18):
                #print '4:'+item
                asce_710_RCiii_mph = item[18:] # Wind Design Load according to ASCE 7-10 (Risk Category III-IV) construction code, in miles per hour
            else: continue
        return asce_705_mph, asce_710_RCiii_mph


##### INGEST SHAPE FILES ##########################################################################################

# READ SHAPEFILES WITH CRITICAL INFRASTRUCTURE INFORMATION
sf = shapefile.Reader(inputfile)  # Open, read, and close the shapefiles
shapes = sf.shapes()  # Geometry: shp file with points, polygons, or polines
fields = sf.fields    # Atributes: shx file with headers. This file is optional for reading.
records= sf.records() # Records: dbf file with contents
# Recall that, for Failure-analyzed Electric Power Buses, ...
#             records[ii][11] = '-7.54970754047e+001' # 'Longitude'
#             records[ii][12] = 'Orland Hills, IL'  # 'Name'
#             records[ii][-2] = 'False'  # bus 'Stable'
#             records[-1] = ' False' # bus 'Feasible'
#print(fields)
#print('NumShapes=',len(shapes))
#[[longi,lati]] = shapes[3].points


##### INTERROGATE WEBSITE AND GENERATE OUTPUTS ##########################################################################################

# OPEN OUTPUT FILE AND START WRITING
f = open(outputfile, 'w')  #Open output file for writing
# Write Header lines in output file
f.write( "Data downloaded from 'http://windspeed.atcouncil.org' on "+ time.strftime("%c %Z")+', where each column corresponds to...\n' )  
f.write( 'Latitude(degrees, positive north)\n' )
f.write( 'Longitude(degrees, positive east)\n' )
f.write( 'ASCE 7-05 Wind speeds (50-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)\n' )
f.write( 'ASCE 7-10 Wind speeds (Risk Category III-IV: >1700-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)\n' )
f.write( 'Asset name\n')
    
for ii in xrange(len(shapes)):    #for shape,record in shapes,records:
    shape = shapes[ii]    
        
    # RETRIEVE THE ASCE 7 WINDS CORRESPONDING TO EACH ASSET (SHAPE) IN THE SHAPEFILE   
    if len(shape.points) == 1:   # This is for cases where the shape correspond to a single lat,lon point
        [[lons,lats]] = shape.points  # Define latitudes and longitudes for a given shape
        if which_inputfile == 1 :        
            asset_name = records[ii][12]
        elif which_inputfile == 2:
            asset_name = records[ii][2]
        print(lons,lats,asset_name)
        #f.write( str(ii)+'    '+str(lats)+'    '+str(lons)+'    '+asset_name+'\n')  # TEST: Write Data
        
        ilat = lats
        ilon = lons
        
        # INTERROGATE URL        
        asce_705_mph, asce_710_RCiii_mph = getASCE7winds(which_url,ilon,ilat)         
        
        ''' TO BE DELETED
        # Input values: Desired lat, Lon
        #requests = {}
        requests['latt'] = str(ilat)  # '41.7152'
        requests['longt'] = str(ilon) # '-87.9835'
        #requests['dec'] ='1'   # This allows display of Lat and Lon values in html file
        #requests['zoom'] = '4' # This determines the size of the Google map

        url_values = urllib.urlencode(requests)
        #print url_values  # The order may differ. 
        #which_url = 'http://windspeed.atcouncil.org/domains/atcwindspeed/process/'
        full_url = which_url + '?' + url_values
        #print full_url

        response = urllib2.urlopen(full_url)
        output_url_string = response.geturl()
        #print output_url_string
        ##print response.read()  # This will print the entire htlm code in the file.

        output_url_list = output_url_string.split('&')
        #which_string = ['asce_705', 'risk_category_iii']
        for item in output_url_list:
            #print item
            if (item.find("asce_705") != -1) and (len(item) <= 9):
                #print item
                asce_705_mph = 'NaN' #float('NaN')     # Not-a-Number value because the point is not over land
            elif (item.find("asce_705") != -1) and (len(item) > 9):
                #print item
                asce_705_mph = item[9:] #float(item[9:])  # Wind Design Load according to ASCE 7-05 (90-years Mean Recurrence Interval) construction code, in miles per hour
            elif (item.find("risk_category_iii") != -1) and (len(item) <= 18): 
                #print item
                asce_710_RCiii_mph = 'NaN'     # Not-a-Number value because the point is not over land
            elif (item.find("risk_category_iii") != -1) and (len(item) > 18):
                #print item
                asce_710_RCiii_mph = item[18:] # Wind Design Load according to ASCE 7-10 (Risk Category III-IV) construction code, in miles per hour
            else: continue
        '''
        
        # OUTPUT VALUES INTO A FILE
        f.write(str(ilat)+'    '+str(ilon)+'    '+asce_705_mph+'    '+asce_710_RCiii_mph+'    '+asset_name+'\n')  # Write Data in output file
        #print "Current date & time " + time.strftime("%c")
        time.sleep(6)  # Add a delay of 6 seconds to avoid website overload
        
    else:  # This is for cases where the shape correspond to a line or a polygon
      lons_lats_list = shape.points
      lons_lats_array = np.array(lons_lats_list)
      lons = lons_lats_array[:,0]
      lats = lons_lats_array[:,1]
      if which_inputfile == 0 : asset_name = 'Line Shape # '+str(records[ii] [8])  # records[ii] [8] corresponds to fields[ii] [8] = ['Branch', 'N', 11, 0], which is the branch number, given as an integer
      for ilat in lats:
         for ilon in lons:
            print(ilon,ilat,asset_name)
            #f.write( str(ii)+'    '+str(ilat)+'    '+str(ilon)+'    '+asset_name+'\n')  # TEST: Write Data
            
            # INTERROGATE URL        
            asce_705_mph, asce_710_RCiii_mph = getASCE7winds(which_url,ilon,ilat)
            
            # OUTPUT VALUES INTO A FILE
            f.write(str(ilat)+'    '+str(ilon)+'    '+asce_705_mph+'    '+asce_710_RCiii_mph+'    '+asset_name+'\n')  # Write Data in output file
            #print "Current date & time " + time.strftime("%c")
            time.sleep(6)  # Add a delay of 6 seconds to avoid website overload
            
f.close()

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