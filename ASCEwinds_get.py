#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:38:27 2015

This code retrieves maximum windspeed loads as a function of lat, lon
from construction codes ASCE 7-10 and ASCE 7-05.

References: http://windspeed.atcouncil.org

Dependencies: urllib2 and urllib 

Issues: None

Last modification: 2015/July/30
@author: edwincampos
"""
# USER DEFINED VARIABLES
# It takes 2h17min with the bbox and resol_lat_lon settings below
bbox = [-83.053506469947564, 30.772143173368807, -62.371875762556336, 46.803464126967938]  # [LonMin, LatMin,LonMax,LatMax]
resol_lat_lon = [0.5,0.5]  # Desired Resolution in degrees of [latitude, longitude] 
url = 'http://windspeed.atcouncil.org/domains/atcwindspeed/process/'
outputfile = './ASCEwinds_get.dat'       
# DEPENDENCIES
import numpy as np
import time
import urllib2
import urllib

# DEFINE LATITUDES AND LONGITUDES
n_points_lat = (bbox[3] - bbox[1]) / resol_lat_lon[0]
n_points_lon = (bbox[2] - bbox[0]) / resol_lat_lon[1]
lats = np.linspace(bbox[1], bbox[3], n_points_lat)
lons = np.linspace(bbox[0], bbox[2], n_points_lon)

# RETRIEVE THE ASCE 7 WINDS
requests = {}  # Define list with website access parameters
requests['dec'] ='1'   # This allows display of Lat and Lon values in html file
requests['zoom'] = '4' # This determines the size of the Google map

f = open(outputfile, 'w')  #Open output file for writing
# Write Header lines in output file
f.write( "Data downloaded from 'http://windspeed.atcouncil.org' on "+ time.strftime("%c %Z")+'\n' )  
f.write( 'Latitude(degrees, positive north),\n' )
f.write( 'Longitude(degrees, positive east),\n' )
f.write( 'ASCE 7-05 Wind speeds (50-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour),\n' )
f.write( 'ASCE 7-10 Wind speeds (Risk Category III-IV: >1700-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)\n' )
          
for ilat in lats:
    for ilon in lons:
        # Input values: Desired lat, Lon
        #requests = {}
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
        
        # OUTPUT VALUES INTO A FILE
        f.write( str(ilat)+','+str(ilon)+','+asce_705_mph+','+asce_710_RCiii_mph+'\n')  # Write Data
        #print "Current date & time " + time.strftime("%c")
        time.sleep(6)  # Add a delay of 6 seconds to avoid website overload

f.close()