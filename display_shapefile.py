# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:43:00 2015
This code generates a .png file with visualization of shape files
Improvements: 
- Read Maximum sustained winds and its position (center?)
- which_case == 7 does not work if want_zoom = 0
@author: Edwin Campos, edwinfcampos@aol.com
Last modification on 2015 Sep 3
"""
# DEPENDENCIES
import shapefile  #http://gis.humboldt.edu/OLM/GSP_318/09_3_ShapefilePY.html or https://code.google.com/p/pyshp/wiki/PyShpDocs
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# osgeo is required for the cases where the shapefiles are in a projection coordinates, and need to be in geographic coordinates --> 
# 1. Instal GDAL as explained in https://trac.osgeo.org/gdal/wiki/BuildingOnMac
# or, type in the command console: 
# $ brew install gdal
# $ mkdir -p /Users/edwincampos/.local/lib/python2.7/site-packages
# $ echo 'import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")' >> /Users/edwincampos/.local/lib/python2.7/site-packages/homebrew.pth
# 2. Write a code to convert shapefiles into geographic coord, as in http://gis.stackexchange.com/questions/77529/how-to-find-and-apply-reprojection-parameters 
from osgeo import osr  
import mpl_toolkits.basemap.pyproj as pyproj


# Variable inputs (to be modified by user). 
which_case = 7  # 7 is giving some problems, since >>> shapes[0].shapeType =  3  
want_zoom = 1  # 1 for zooming in particular area; 0 for full hurricane-dataset area
want_sidetext = 0  # 1 for appearing additional text at the side of the plot
outputplotname = 'display_shapefile'

# Constants (modified carefully, only to create new cases)
if which_case == 0:  
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneWilma'
    myshp_filename = 'lines'  
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = 'Synthetic Electric Grid Lines\n Florida, USA'
    bbox = [-83.0,25.0,-80.0,28.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 1.0
elif which_case == 1: 
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneWilma'
    myshp_filename = 'buses' #'buses_old' #'lines'
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = 'Synthetic Electric Grid Buses\n Florida, USA'
    bbox = [-83.0,25.0,-80.0,28.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
elif which_case == 2:
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromRobinson_NGPP/fl_ngpp'
    myshp_filename = 'ngpp_draft_FL'
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = 'Natural Gas Processing Plant\n Florida, USA'
    bbox = [-88.0,25.0,-80.0,31.5]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 1.0    
elif which_case == 3:
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/Hurrevac4Windows/Hurrevac_outputs'
    myshp_filename = 'WILMA_windhr0' #'WILMA_windhr0' #'WILMA_windswath' #'WILMA_error' #'WILMA_FcstPlot_l'  # 'WILMA_FcstPlot_p' is not working
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = '39, 58 & 74 mph Winds for Hurricane Wilma \n 2005 Oct 24, 8 am CDT'
    bbox = [-77.5,37.5,-75.0,39.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 0.5
elif which_case == 4:   # In this case >>> shapes[0].shapeType = 5 --> Polygon
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/Hurrevac4Windows/Hurrevac_outputs'
    myshp_filename = 'KATRINA_windhr0' #'KATRINA_windhr0' #'KATRINA_windswath' #'KATRINA_error' #'KATRINA_FcstPlot_l'  # 'KATRINA_FcstPlot_p' is not working
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = '39, 58 & 74 mph Winds for Hurricane Katrina \n 2005 Aug 29, 4 am CDT (Adv.#26)'
    bbox = [-77.5,37.5,-75.0,39.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 0.5
elif which_case == 5:
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromCraig_HurricaneSandy/ExampleData'
    myshp_filename = 'buses'
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = 'Synthetic Electric Grid \n Orginal without Failures'
    bbox = [-77.5,37.5,-75.0,39.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 0.5
elif which_case == 6:
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromRobinson_NGPP/ngpp_east'
    myshp_filename = 'ngpp_east'
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = 'Natural Gas Processing Plants in FL, AL, MS, LA, & TX*\n None in the Atlantic Coast States'
    bbox = [-105.0,25.0,-70.0,45.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 5.0
elif which_case == 7:   # Surge Elevation Contours for Hurricane Ivan 2004  # Does not work if want_zoom = 0
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/fromFEMA_HurricaneIvan/sec'
    myshp_filename = 'surge_rev'
    shapefiles_ingeo = 0 # These shapefiles are in a projection coordinates, and need to be in geographic coordinates --> 
    # Instal GDAL at http://www.kyngchaos.com/software/frameworks#gdal_complete
    # Instal GDAL Python wrapper available at https://pypi.python.org/pypi/GDAL/
    # Write a code to convert shapefiles into geographic coord, as in http://gis.stackexchange.com/questions/77529/how-to-find-and-apply-reprojection-parameters    
    plottitle = 'Surge Elevation Contours derived from coastal high water marks following Hurricane Ivan in 2004'
    bbox = [-88.3,30.0,-86.0,31.01]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 0.5
else:
    datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/codes'
    myshp_filename = 'newfangledshapefile_analyzed'
    shapefiles_ingeo = 1 # These shapefiles are in geographic coordinates 
    plottitle = 'Synthetic Electric Grid \n Final with Random Failures'
    bbox = [-77.5,37.5,-75.0,39.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    tickinterval = 0.5
    
shapefilename = datadir+'/'+myshp_filename

'''
# If shapefile is in map projection coordinates, then convert shapefile to geographic coordinates
if which_case == 7:
    shpproj shapefilename shapefilename_geo   # Reproject shapefile, find more details at http://shapelib.maptools.org/shapelib-tools.html#shpproj
    shapefilename = shapefilename_geo         # Use the new reprojected shapefiles in the rest of the code
'''
    
## Read shape files for Electric Power Lines
##myshp_eplines = ep_namehint[1] # = ['buses', 'lines'] 

# Read shape files
sf = shapefile.Reader(shapefilename)  # open the shapefile
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
'''
for name in dir(shapes[0]):
    if not name.startswith('__'):
        name
        
for shape in shapes:
    [[longitud,latitud]] = shape.points
        print(longitud,latitud)
'''

# Find bounding box coordinates of all shapes in the shapefile (to be used later in basemap plot)
if (want_zoom == 0) and (shapes[0].shapeType != 1):  # Zoom using the bbox information only for NON-Point Geometries
    # Recall that 'bbox = shapes[0].bbox' retrieves the bounding box of the first shape
    bbox = [180,90,-180,-90]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude]
    #These will corresponds to the 1st row, which is needed only for setup and will be deleted later
    bbox_all = bbox  #[180,90,-180,-90] 
    firstXYs = shapes[0].points[0]
    for shape in shapes:
        bbox[0] = shape.bbox[0] #min(bbox[0], shape.bbox[0])
        bbox[1] = shape.bbox[1] #min(bbox[1], shape.bbox[1])
        bbox[2] = shape.bbox[2] #max(bbox[2], shape.bbox[2])
        bbox[3] = shape.bbox[3] #max(bbox[3], shape.bbox[3])
        bbox_all = np.vstack((bbox_all,shape.bbox))  # Stack arrays in sequence vertically (row wise).
        firstXYs = np.vstack((firstXYs,shape.points[0]))  # This finds the origin point in the shape

    # Get rid of the first row, which contains non-useful data
    #del bbox_all[0,:]
    bbox_all = bbox_all[1:,:]
    firstXYs = firstXYs[1:,:]

    # add some padding
    bbox = [min(bbox_all[:,0]), min(bbox_all[:,1]), max(bbox_all[:,2]), max(bbox_all[:,3])]
    bbox[0] -= 1.1  # left-hand longitude
    bbox[1] -= 0.2   # botton latitude
    bbox[2] += 0.5   # right-hand longitude
    bbox[3] += 0.2   # top latitude
    
    # Define the spacing between tickmarks (in degrees of latitude and longitude)
    tickinterval = 3.
    # Define size of plot symbols (e.g.,crosses)
    markersize=2
else:
    #bbox = [-77.5,37.5,-75.0,39.0]  # [left-hand longitude, botton latitude, right-hand longitude, top latitude] # This was already determined by which_case
    # tickinterval = 0.5
    outputplotname = outputplotname+'_zoom'
    markersize=  10

# Setup a stereographic basemap. 
# Setup a Mercator basemap. 
map = Basemap(projection='merc',\
            #lon_0=-105.,lat_0=20.,lat_ts=0.,\
            llcrnrlat=bbox[1],urcrnrlat=bbox[3],\
            llcrnrlon=bbox[0],urcrnrlon=bbox[2],\
            #rsphere=6371200.,area_thresh=1000,\
            resolution='i')  # Resolution of boundary database can be c (crude, default), l (low), i (intermediate), h (high), f (full) or None.

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
map.drawcountries()
map.drawstates()


ax = plt.axes()
ax.set_title(plottitle)


# if the shapefiles are in a projection coordinates, then convert into geographic coordinates 
# Determine the proj4 info from the *.prj shapefile ("http://gis.stackexchange.com/questions/7608/shapefile-prj-to-postgis-srid-lookup-table/7615#7615")
if shapefiles_ingeo == 1:
    # Read and pLot shapefiles for Electric Grid Buses
    map.readshapefile(shapefilename, 'things2draw')  # This plots only a minuscule point
else:
    prj_file = open(shapefilename+'.prj','r')
    prj_txt = prj_file.read()
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_txt])  # prj_txt contains the information in the *.prj file
    proj4_shape_string = srs.ExportToProj4()  # This info can also be obtained at http://spatialreference.org  --> '+proj=utm +zone=16 +ellps=GRS80 +units=m +no_defs' 
    # Determine the proj4 info from the map
    proj4_map_string = map.proj4string
    # Setup the transform (as in "http://gis.stackexchange.com/questions/77529/how-to-find-and-apply-reprojection-parameters")
    shpProj = pyproj.Proj(proj4_shape_string)
    mapProj = pyproj.Proj(map.proj4string)    
    for shape in shapes:   
        ##xline,yline = shape  # This will work all the time, as it comes directly from the .shp file
        xline = [i[0] for i in shape[:]]
        yline = [i[1] for i in shape[:]]
        shpX = xline
        shpY = yline
        # Transform the shapefile from its projection into lat/lon
        lonlat = np.array(shpProj(shpX,shpY,inverse=True)).T
        # Convert the lat lon to the Basemap projection
        baseXY = np.array(mapProj(lonlat[:,0],lonlat[:,1])).T
        
        # Plot  . recall that for case #7, records[shape#][surgeheightinfeet]
        ax.plot(xline, yline, color='black') # This will draw lines


#ax = plt.axes()
#ax.set_title(plottitle)

# Draw crosses for Point Geometries
if shapes[0].shapeType == 1:
  for info, shape in zip(map.things2draw_info, map.things2draw):
    ''' READING COORDINATES FROM THE .dbf FILE, which won't work if there are not lat, lon values in the .shx file, or if the .dbf file is not corresponding to the .shp file (google geometry and record balancing) 
    if 'Latitude' in info: 
        lat_bus = float(info['Latitude'])
    elif 'latitude' in info:
        lat_bus = float(info['latitude'])
    elif 'LATITUDE' in info:
        lat_bus = float(info['LATITUDE'])
    else:
        continue  # The current iteration of the FOR loop terminates, and execution continues with next iteration
    if 'Longitude' in info: 
        lon_bus = float(info['Longitude'])
    elif 'longitude' in info:
        lon_bus = float(info['longitude'])
    elif 'LONGITUDE' in info:
        lon_bus = float(info['LONGITUDE'])
    else:
        continue 
    #map.plot(lon_bus,lat_bus)   # this should draw lines & polygons
    xbus,ybus = map(lon_bus,lat_bus)
    '''    
    xbus,ybus = shape  # This will work all the time, as it comes directly from the .shp file
        
    #print info['Bus'], info['Name'], info['Stable']
    # Recall that records_epbuses[ii][-1] = ' False' # bus 'Feasible'
    #print records_epbuses_fa[int(info['Bus']) -1 ][-1] ,', If True ==> bus Outaged'
    if (which_case != 1) and (
        (['Outaged', 'C', 60, 0] in fields) or (
        ['outage', 'C', 5, 0] in fields) ) and (
        records[ int(info['Bus']) -1 ][-1] == 'True'): # Recall that records_epbuses_fa[ii][-1] = 'True' ==> bus 'Outaged'
    #if info['Stable'] == 'False': #This corresponds to the non-analyzed shape file
        whichcolor= 'red' #'blue'  
    else: 
        whichcolor = 'blue' #'black'    
    ax.plot(xbus, ybus, marker='+', color=whichcolor, markersize=markersize, markeredgewidth=1.5) # This will draw points/crosses
else: 
  for info, shape in zip(map.things2draw_info, map.things2draw):
    ##xline,yline = shape  # This will work all the time, as it comes directly from the .shp file
    xline = [i[0] for i in shape[:]]
    yline = [i[1] for i in shape[:]]
    if (which_case != 1) and (
        (['Outaged', 'C', 60, 0] in fields) or (['outage', 'C', 5, 0] in fields) ) and (
        records[ int(info['Bus']) -1 ][-1] == 'True'): # Recall that records_epbuses_fa[ii][-1] = 'True' ==> bus 'Outaged'
        whichcolor= 'red' #'blue'  
    else: 
        whichcolor = 'blue' #'black'
    ax.plot(xline, yline, color=whichcolor) # This will draw lines
    
    
if want_sidetext:   
  ax.text(1.13, 0.25, '+\nBus\nFailure',
        verticalalignment='bottom', horizontalalignment='center',
        transform=ax.transAxes,
        color='blue', fontsize=12)
  ax.text(1.13, 0.55, '+\nBus\nOK',
        verticalalignment='bottom', horizontalalignment='center',
        transform=ax.transAxes,
        color='black', fontsize=12)
        
plt.savefig(outputplotname+'.png', dpi=200)
plt.show()