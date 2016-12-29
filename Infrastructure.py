# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:08:50 2015
           Tue Aug 25 generify variable names as appropriate

@author: Edwin Campos and Mark Hereld
"""
import shapefile
import numpy as np
import random
from Asset import Asset, AssetList

class InfrastructureElement(object):

    def __init__(self):
        self.name = ''            # name
        self.location = [0.0,0.0] # latitude, longitude
        self.assets = []          # list of assets located at this element
        self.removed = False      # Is this element removed?

    def findAssets(self, assets):

        for a in assets.entries.values():
            dist = np.linalg.norm(np.array(self.location) - np.array(a.geometry))
            # TODO: This is arbitrary choice.
            maxdist = 0.1;
            if (dist < maxdist):
                self.assets.append(a)

class InfrastructureLayer(object):
#GENERIFY#     def load():
#GENERIFY#         print('nothing')
#GENERIFY#     def save():
#GENERIFY#         print('zilch')
#GENERIFY# 
#GENERIFY# class ElectricPowerGrid(InfrastructureLayer):

    def __init__(self):
        self.sf = ''
        self.filename = ''
        self.elements = []

        # These would not need to be member variables. - Kim, 08272015
        # self.shapes = ''
        # self.fields = ''
        # self.records = ''

    def load(self,shapefilename):

        # Read shape files for Electric Power Buses

        self.filename = shapefilename
        self.sf = shapefile.Reader(shapefilename)
        self.shapes = self.sf.shapes()  # Geometry: shp file with geometries # Every geometry/shape must have a corresponding record
        self.fields = self.sf.fields    # Atributes: shx file with headers  # fields[ #ofrecords[:,i]+1, 4]
        self.records= self.sf.records() # Records: dbf file with contents # records[ #ofshapes, #offields[:,i] -1]
        #print(fields)
        #[('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['Bus', 'C', 60, 0], ['Type', 'N', 11, 0], ['GenOutput', 'F', 19, 11], ['Load', 'F', 19, 11], ['VarLoad', 'F', 19, 11], ['GenRating', 'F', 19, 11], ['MinGen', 'F', 19, 11], ['Voltage', 'F', 19, 11], ['Angle', 'F', 19, 11], ['Latitude', 'F', 19, 11], ['Longitude', 'F', 19, 11], ['Name', 'C', 60, 0], ['Island', 'N', 11, 0], ['FinalGen', 'F', 19, 11], ['FinalLoad', 'F', 19, 11], ['Stable', 'C', 60, 0], ['Feasible', 'C', 60, 0]]

        #IF 'Outaged' does not exist then ...
        # Create a new field & record in the bus shapefiles: 'Outaged' = 'False'
        self.fields.append(['Outaged', 'C', 60, 0])

        # No need to be a member
        self.list2Bappended = [['False']] * (len(self.shapes))  # Important, use [[]] to make a column array
        self.records = np.hstack((self.records,self.list2Bappended))  #Append/concatenate the new column array into the records list, as the last column

        for i in xrange(self.sf.numRecords):
            element = InfrastructureElement()
            element.location[0] = self.sf.shape(i).points[0][1]
            element.location[1] = self.sf.shape(i).points[0][0]
            self.elements.append(element)

    def save(self,shapefilename):

        # Mark removed elements
        for i in xrange(len(self.elements)):
            if (self.elements[i].removed == True):
                self.disableElementByIndex(i)

        # Update/Re-write the Buses shapefiles with the new failure criteria
        '''Recall that the set of 3 files is called a layer.
        .shp – geographical information (latitudes and longitudes)
        .dbf – dbase III table containing attribute information for the shapes in the .shp file
        .shx – shape index file, contains the offset of the records in the .shp file (for random access reading) '''
        # For details visit https://pypi.python.org/pypi/pyshp
        w = shapefile.Writer(shapeType=shapefile.POINT)  # Recall that sf.shapeType = 1 ==> Point
        w.fields = list(self.sf.fields)    # Atributes: shx file  #Do not use sf.fields, because it does not have the new 'Outaged' atribute
        w._shapes = list(self.sf.shapes()) # Geometry: shp file
        w.records = list(self.records)  # Records: dbf file
        #w.point(sf.shapes()) #shapes)    # Geometry: shp file
        #w.field(sf.fields)    # Atributes: shx file
        #w.record(records)  #Records: dbf file
        #print 'Writing output shapefiles at... '+datadir+'/'+myshp+'_analyzed.*'
        w.save(shapefilename+'_analyzed')

    # Wrapper for load
    def open(self,shapefilename):               # provide this alias for backward compatibility
        self.load(shapefilename)

    # Wrapper for save?
    def saveNetwork(self,shapefilename):        # provide this alias for backward compatibility
        self.save(shapefilename)

    def disableElementByIndex(self,index):
        self.records[index][-1] = 'True'           # Recall that records[ii][-1] = 'False' # bus 'Outaged'index):

    # TODO: only for testing...
    def randomlyTrashThisNetwork(self):
        for ii in xrange(len(self.shapes)):
            failure = (random.random()>0.5)     # Need to find the random()
            
            if failure:
                #self.records[ii][-1] = 'True'   # Recall that records[ii][-1] = 'False' # bus 'Outaged'
                self.disableElementByIndex(ii)

class InfrastructureList:

    def __init__(self):
        self.description = ''
        self.entries = dict()

    def appendFragilityTypesFromFile(self, filename):

        self.entries[filename] = InfrastructureLayer()
        self.entries[filename].open(filename)

# from IIF_infra... import ElectricPowerGrid
# EP = ElectricPowerGrid()
# EP.load('shapefile')
# EP.randomlyTrashThisNetwork()
# EP.save('newfangledshapefile')

