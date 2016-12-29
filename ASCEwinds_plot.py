#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 16:09:44 2015

This code plots maximum windspeed loads as a function of lat, lon
from construction codes ASCE 7-10 and ASCE 7-05. 

So what are you to do if you find yourself faced with a special wind region? 
Well, as ASCE 7-10 suggests, consulting with a climate expert is probably your best bet. 
A meteorologist or wind engineer will know how to interpret the local climate data recorded 
at weather stations near your site to help you determine your design wind speed. 
And if nearby topography plays a role in the wind’s directionality, turbulence level, or other behavior, 
a well-designed wind tunnel study can take the guesswork out of interpreting these special wind regions.

@author: edwincampos
Last modification on 2015 Aug 3
"""

# USER DEFINED VARIABLES
bbox = [-83.053506469947564, 30.772143173368807, -62.371875762556336, 46.803464126967938]  # [LonMin, LatMin,LonMax,LatMax]
#bbox = [-83.053506469947564, 30.772143173368807, -81.2375584078, 31.477924599]  # [LonMin, LatMin,LonMax,LatMax]
input_file = 'ASCEwinds_get_20150803.dat'  #'getASCEwinds.dat'  #'./ASCEwinds_get.dat' # WITH extension and path
output_filename = 'ASCEwinds'   # Without extension nor path

# DEPENDENCIES
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
#import scipy.interpolate
from matplotlib.mlab import griddata

# PREDEFINED VARIABLES
lat_asce = []  # Latitude(degrees, positive north) 
lon_asce=  []  # Longitude(degrees, positive east)
asce_705_mph = []  # ASCE 7-05 Wind speeds (50-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)
asce_710_RCiii_mph = [] # ASCE 7-10 Wind speeds (Risk Category III-IV: >1700-years mean recurrence interval for 3-seconds peak gust, in miles-per-hour)
tickinterval = 3. # Define the spacing between tickmarks (in degrees of latitude and longitude)
markersize=2  # Define size of plot symbols (e.g.,crosses)
  
# READ INPUT FILE
f = open(input_file, 'r')
line_count = 0
for line in f:
    line_count += 1
    if line_count > 5:
        #print line
        lat_buff,lon_buff,asce_705_buff,asce_710_RCiii_buff = line.split(',')
        #print lat_buff
        #print lon_buff
        #print asce_705_buff
        #print asce_710_RCiii_buff
        if asce_705_buff == 'Special%20Wind%20Region': continue # Execution continues with the next iteration of the loop
        if np.isfinite(float(asce_705_buff)):  #Filter out NaN values and Special Wind Regions
            lat_asce.append(float(lat_buff))
            lon_asce.append(float(lon_buff))
            asce_705_mph.append(float(asce_705_buff))
            asce_710_RCiii_mph.append(float(asce_710_RCiii_buff))

f.close()

# CREATE A BASEMAP
# lat_ts: latitude of true scale. lon_0,lat_0 is central point.
# llcrnrlat: latitude of lower left hand corner of the desired map domain (degrees).
# llcrnrlon: longitude of lower left hand corner of the desired map domain (degrees).
# urcrnrlon: longitude of upper right hand corner of the desired map domain (degrees).
# urcrnrlat: latitude of upper right hand corner of the desired map domain (degrees).
# resolution: resolution of boundary database to use. Can be c (crude), l (low), i (intermediate), h (high), f (full) or None.
# area_thresh: coastline or lake with an area smaller than area_thresh in km^2 will not be plotted. Default 10000,1000,100,10,1 for resolution c, l, i, h, f.


# Setup a stereographic basemap. 
# Setup a Mercator basemap. 
map = Basemap(projection='merc',\
            lon_0=-105.,lat_0=20.,lat_ts=0.,\
            llcrnrlat=bbox[1],urcrnrlat=bbox[3],\
            llcrnrlon=bbox[0],urcrnrlon=bbox[2],\
            rsphere=6371200.,resolution='l',area_thresh=1000)

fig = plt.figure()

map.drawmapboundary(fill_color='aqua')
map.fillcontinents(color='#ddaa66',lake_color='aqua')
map.drawcoastlines()

# draw parallels and meridians.
# label on left and bottom of map.
parallels = np.arange(0.,80,tickinterval)
# Control whether parallels are labelled where they intersect the left, right, top or bottom of the plot. For example labels=[1,0,0,1] will cause parallels to be labelled where they intersect the left and and bottom of the plot, but not the right and top.
map.drawparallels(parallels,labels=[1,0,0,0]) 

meridians = np.arange(10.,360.,tickinterval)
# Control whether meridians are labelled where they intersect the left, right, top or bottom of the plot. For example labels=[1,0,0,1] will cause meridians to be labelled where they intersect the left and and bottom of the plot, but not the right and top.
map.drawmeridians(meridians,labels=[0,0,0,1]) 


# CREATE ASCE MAP
# mymap = plt.tricontour(lon_asce,lat_asce, asce_705_mph, 10)
# Make an artificial, regular grid, to be used later during interpolation. 
numcols, numrows = 30, 30
lon1Dinterp = np.linspace(min(lon_asce), max(lon_asce), numcols)
lat1Dinterp = np.linspace(min(lat_asce), max(lat_asce), numrows)
lon2Dinterp, lat2Dinterp = np.meshgrid(lon1Dinterp, lat1Dinterp)
#print(lon2Dinterp)

#-- Interpolate at the points in xi, yi
# "griddata" expects "raw" numpy arrays, and it will output Z_2Dinterp.data and Z_2Dinterp.mask
Z_2Dinterp = griddata(lon_asce, lat_asce, asce_705_mph, lon2Dinterp, lat2Dinterp, interp='linear')  # Interpolate; there's also method='cubic' for 2-D data such as here
#print (Z_2Dinterp)
# PROJECT THE ASCE MAP ON THE BASEMAP
X_2D,Y_2D = map(lon2Dinterp*180./np.pi, lat2Dinterp*180./np.pi)
cs = map.contour(X_2D,Y_2D,Z_2Dinterp.data,15,linewidths=1.5)

'''
lon2D_asce, lat2D_asce = np.meshgrid(lon_asce,lat_asce)  # Set up a regular 2D grid for use in contour
asce2D_705_mph = griddata(lon_asce, lat_asce, asce_705_mph, lon2D_asce, lat2D_asce, interp='linear')  # Interpolate; there's also method='cubic' for 2-D data such as here
#asce2D_705_mph = scipy.interpolate.griddata((lon_asce, lat_asce), asce_705_mph, (lon2D_asce, lat2D_asce), method='linear')  # Interpolate; there's also method='cubic' for 2-D data such as here
# THE FOLLOWING LINE IS GIVING AN ERROR!
map.contour(lon2D_asce, lat2D_asce, asce2D_705_mph)  # Recall that contour uses 2D matrices for X and Y. If instead 1D vectors are used for X and Y ==> IndexError: too many indices for array
'''
#plt.title('contour lines over filled continent background')
plt.savefig(output_filename+'.png', dpi=200)
plt.show()
