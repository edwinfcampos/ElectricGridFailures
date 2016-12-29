# Disaster objects
#   created on August 19, 2015 by Kibaek Kim
#   modified on August 21, 2015 by Kibaek Kim
#   modified on August 25, 2015 by Kibaek Kim
#   last modified on August 27, 2015 by Kibaek Kim

import shapefile
from mpl_toolkits.basemap import Basemap # This should be included before pyplot.
from matplotlib.mlab import inside_poly, griddata
from matplotlib.tri import Triangulation, LinearTriInterpolator
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
import numpy as np

# This class is an abstract class to store data for disasters and to provide damage information at given locations.
class DisasterLayer(object):

    def __init__(self):
        self.name = '' # disaster name
        self.data = '' # data content
        self.unit = '' # unit of intensity value

    def open(self, filename, name):
        # set disaster name
        self.name = name
        # Read data file
        self.data = shapefile.Reader(filename)

    def configureFromTextFile(self, filename):
        # TODO: no name here...
        self.open(filename, filename)

    def getIntensity(self, lat, long):
        pass

    def display(self, map = None):
        pass

# Hurricane child class
#   +open() reads shape files that contain geographic information and wind speed.
#   +getIntensity() returns gust in MPH at given latitude and longitude.
# TODO: We might be able to do a better job if we can decode GRIB1...
class Hurricane(DisasterLayer):

    def open(self, filename, name):
        super(Hurricane, self).open(filename, name)
        self.unit = 'gust_mph'

    def getIntensity(self, lat, long):

        # TODO: Test
        long += 5.0
        lat += 10.0

        wind_kt = 0.0 # wind speed in knots
        for i in xrange(self.data.numRecords):
            if len(inside_poly([[long, lat]], self.data.shape(i).points)) > 0:
                # Find the wind corresponding to the bus latutude and longitude
                wind_kt =  max(wind_kt, float(self.data.record(i)[1]))

        # Converting from knott to mph (1 kt = 1.15077945 miles per hour)
        wind_mph = wind_kt * 1.15077945
        # Converting from mph wind to mph gust (1 mph wind = 1.3 mph gust)
        gust_mph = wind_mph * 1.3;

        return gust_mph

    def display(self, map = None):

        if (map == None):
            plt.figure()

        for i in xrange(self.data.numRecords):
            x, y = Polygon(self.data.shape(i).points).exterior.xy
            x = [xi - 5.0 for xi in x]
            y = [yi - 10.0 for yi in y]
            if (map == None):
                plt.plot(x, y)
            else:
                x, y = map(x, y)
                map.plot(x, y)

        if (map == None):
            plt.title('Disaster: ' + self.name)
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.savefig(self.name + '.eps', format='eps')

# Flood child class
#   +open() reads shape files that contain geographic information and probability of surge > x.
#   +getIntensity() returns the probability of surge > x at given latitude and longitude.
# TODO: This does not return "intensity"...
class Flood(DisasterLayer):

    def open(self, filename, name):
        super(Flood, self).open(filename, name)

        self.lon = [self.data.shape(i).points[0][0] for i in xrange(self.data.numRecords)]
        self.lat = [self.data.shape(i).points[0][1] for i in xrange(self.data.numRecords)]
        self.val = [self.data.record(i)[1] for i in xrange(self.data.numRecords)]

        t = Triangulation(self.lon, self.lat)
        self.interpolator = LinearTriInterpolator(t, self.val)

        self.unit = 'probability'

    def getIntensity(self, lat, long):

        surge = 0.0
        maskedIntensity = self.interpolator(long, lat)
        if maskedIntensity.mask == False:
            surge = maskedIntensity.data

        return surge

    def display(self, map = None):

        minx = min(self.lon)
        maxx = max(self.lon)
        miny = min(self.lat)
        maxy = max(self.lat)

        xi = np.linspace(minx,maxx,100)
        yi = np.linspace(miny,maxy,100)
        zi = griddata(self.lon, self.lat, self.val, xi, yi, interp='linear')

        if (map == None):
            plt.figure()
            plt.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
            plt.contourf(xi, yi, zi, 15, cmap=plt.cm.rainbow, vmax=abs(zi).max(), vmin=abs(zi).min())
            plt.colorbar()
            plt.title('Disaster: ' + self.name)
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.savefig(self.name + '.eps', format='eps')
        else:
            map.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
            map.contourf(xi, yi, zi, 15, cmap=plt.cm.rainbow, vmax=abs(zi).max(), vmin=abs(zi).min())
            map.colorbar()

# List of disaster classes
#   +appendDisasterTypesFromFile()
# TODO: We have similar classes...
class DisasterList:

    def __init__(self):
        self.description = ''
        # TODO: We use Disaster Type as a key, assuming that we have only one event per disaster.
        self.entries = dict()
        self.disasterTypeMappings = {
            'Flood':Flood,
            'Wind':Hurricane
            }

    def __setitem__(self, key, value):
        self.entries[key] = value

    def __getitem__(self, key):
        return self.entries[key]

    def appendDisasterTypesFromFile(self, filename, dtype):

        dfile = open(filename + '.txt', 'r')
        linesoftext = dfile.readlines()

        newestEntry = len(self.entries)
        lineNumber = 0
        createNewEntry = 0
        while (lineNumber < len(linesoftext)):

            # parse line
            keyvalue = linesoftext[lineNumber].split('=')
            keyword = keyvalue[0].strip().lower()

            # select lines that describe next entry
            if (keyword == 'version'):                 # begins entry configuration section
                pass
            elif (keyword == 'type'):                  # ends entry configuration section
                dtype = keyvalue[1].strip().strip("'") # key for disaster dict
            elif (keyword == 'end'):                   # ends entry configuration section
                createNewEntry = 1

            if (createNewEntry == 1):
                # initialize new disaster entry
                self.entries[dtype] = self.disasterTypeMappings[dtype]()
                # fill the object with the data
                self.entries[dtype].open(filename, dtype)
                # createNewEntry housekeeping
                createNewEntry = 0
                newestEntry += 1

            # while loop housekeeping
            lineNumber += 1
        dfile.close()

    def display(self, map = None):
        for d in self.entries.values():
            d.display(map)