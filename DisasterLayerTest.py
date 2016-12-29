# Just for testing the DisasterLayer object
#   created on August 19, 2015 by Kibaek Kim
#   last modified on August 20, 2015 by Kibaek Kim

import shapefile
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
import random

import DisasterLayer as dl

def testHurricane(filename):

    # load hurricane data
    hdl = dl.HurricaneDamage()
    hdl.open(filename, 'TestHurricane')

    # load bus locations
    buses = shapefile.Reader('data/buses')

    # plot hurricane damage contours
    plt.figure()
    for i in xrange(hdl.data.numRecords):
        x,y = Polygon(hdl.data.shape(i).points).exterior.xy
        plt.plot(x,y)

    # plot bus locations
    print 'Getting wind damage for each bus'
    for i in xrange(buses.numRecords):
        lat = float(buses.record(i)[10]) + random.uniform(-2, 2)
        long = float(buses.record(i)[11]) + random.uniform(-2, 2)
        intensity = hdl.getIntensity(lat, long)
        print 'bus ', i, ' lat ', lat, ' long ', long, ' intensity ', intensity
        plt.scatter(long, lat, c='red')

    print 'done'

def testFlood(filename):
    # load flood data
    fdl = dl.FloodDamage()
    fdl.open(filename, 'TestFlood')

    # load bus locations
    buses = shapefile.Reader('data/buses')

    plt.figure()
    # plot flood polygons
    # TODO: This looks strange. maybe because of the missing data?
    for i in xrange(fdl.data.numRecords):
        pts = fdl.data.shape(i).points
        x, y = Polygon(pts).exterior.xy
        plt.plot(x, y)

    # plot bus locations
    print 'Getting flood damage for each bus'
    for i in xrange(buses.numRecords):
        lat = float(buses.record(i)[10]) - 10 + random.uniform(-0.5, 0.5)
        long = float(buses.record(i)[11]) - 20
        intensity = fdl.getIntensity(lat, long)
        print 'bus ', i, ' lat ', lat, ' long ', long, ' intensity ', intensity
        plt.scatter(long, lat, c='red')

    print 'done'

# Test data files
hurricaneFile = 'data/al182012_2012102912_Flat2'
floodFile     = 'data/ProbSurge02c_06191400_0-SFC'

# Run test
testHurricane(hurricaneFile)
testFlood(floodFile)

plt.show()