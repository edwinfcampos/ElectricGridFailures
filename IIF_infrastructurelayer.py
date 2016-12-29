# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:08:50 2015

@authors: Edwin Campos and Mark Hereld
Last modification on 2015 Aug 19 by Edwin Campos
"""
import shapefile
import numpy as np
import random

class InfrastructureLayer(object):
    def open():
        print('nothing')
    def saveNetwork():
        print('network')

class ElectricPowerGrid(InfrastructureLayer):
    def open(self,shapefilename):

        # Read shape files for Electric Power Buses
        
        self.sf_epbu = shapefile.Reader(shapefilename)
        self.shapes_epbuses = self.sf_epbu.shapes()  # Geometry: shp file with geometries # Every geometry/shape must have a corresponding record
        self.fields_epbuses = self.sf_epbu.fields    # Atributes: shx file with headers  # fields[ #ofrecords[:,i]+1, 4]
        self.records_epbuses= self.sf_epbu.records() # Records: dbf file with contents # records[ #ofshapes, #offields[:,i] -1]
        #print(fields_epbuses)
        #[('DeletionFlag', 'C', 1, 0), ['Class', 'C', 60, 0], ['Bus', 'C', 60, 0], ['Type', 'N', 11, 0], ['GenOutput', 'F', 19, 11], ['Load', 'F', 19, 11], ['VarLoad', 'F', 19, 11], ['GenRating', 'F', 19, 11], ['MinGen', 'F', 19, 11], ['Voltage', 'F', 19, 11], ['Angle', 'F', 19, 11], ['Latitude', 'F', 19, 11], ['Longitude', 'F', 19, 11], ['Name', 'C', 60, 0], ['Island', 'N', 11, 0], ['FinalGen', 'F', 19, 11], ['FinalLoad', 'F', 19, 11], ['Stable', 'C', 60, 0], ['Feasible', 'C', 60, 0]]

        
        # Create a new field & record in the bus shapefiles: 'Outaged' = 'False'
        if (['Outaged', 'C', 60, 0]  not in self.fields_epbuses):  #IF 'Outaged' does not exist then ...
            self.fields_epbuses.append(['Outaged', 'C', 60, 0])
            self.list2Bappended = [['False']] * (len(self.shapes_epbuses))  # Important, use [[]] to make a column array
            self.records_epbuses = np.hstack((self.records_epbuses,self.list2Bappended))  #Append/concatenate the new column array into the records list, as the last column

    def saveNetwork(self,shapefilename):
       
        # Update/Re-write the Buses shapefiles with the new failure criteria
        '''Recall that the set of 3 files is called a layer.
        .shp – geographical information (latitudes and longitudes)
        .dbf – dbase III table containing attribute information for the shapes in the .shp file
        .shx – shape index file, contains the offset of the records in the .shp file (for random access reading) '''
        # For details visit https://pypi.python.org/pypi/pyshp
        w = shapefile.Writer(shapeType=shapefile.POINT)  # Recall that sf_epbu.shapeType = 1 ==> Point
        w.fields = list(self.fields_epbuses)    # Atributes: shx file  #Do not use sf_epbu.fields, because it does not have the new 'Outaged' atribute
        w._shapes = list(self.sf_epbu.shapes()) # Geometry: shp file
        w.records = list(self.records_epbuses)  # Records: dbf file
        #w.point(sf_epbu.shapes()) #shapes_epbuses)    # Geometry: shp file
        #w.field(sf_epbu.fields)    # Atributes: shx file
        #w.record(records_epbuses)  #Records: dbf file
        #print 'Writing output shapefiles at... '+datadir+'/'+myshp_epbuses+'_analyzed.*'
        w.save(shapefilename+'_analyzed')

    def randomlyTrashThisNetwork(self):
        for ii in xrange(len(self.shapes_epbuses)):
            failure = (random.random()>0.5)  # Need to find the random()
            
            if failure:
                self.records_epbuses[ii][-1] = 'True' # Recall that records_epbuses[ii][-1] = 'False' # bus 'Outaged'
        



# from IIF_infra... import ElectricPowerGrid
# EP = ElectricPowerGrid()
# EP.open('shapefile')
# EP.randomlyTrashThisNetwork()
# EP.saveNetwork('newfangledshapefile')

