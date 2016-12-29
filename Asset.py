# version Hereld 2015-08-19

#   Asset classes
#       Asset           the root class -- don't instantiate, it's basically abstract
#       AssetList       contains potentially mixed list of any kind of Asset

import random
from Fragility import FragilityList
import matplotlib.pyplot as plt

class name2obj(object):
    def __init__(self):
        self.name = 'none'
        self.obj = None

class Asset(object):
    def __init__(self):
        self.name = 'Ozymandius'
        self.assetClassName = 'skyscraper'
        self.description = 'Tom Python'
        self.versions = {'Hereld_2015-07-27'}   # list of compatible versions
        self.version = 'Penultimate 6.0beta'    # this version
        self.date = 'Manana'        # date this asset description created in db
        self.geometry = [0,0]       # [latitude,longitude]
        self.destroyed = False
        #self.fragilities = dict()   # a list of fragility objects, each for a different disaster type
        self.fragilities = FragilityList()

    def configureFromTextLines(self,lines, start, end):
        for lineNumber in range(start,end):
            keyvalue = lines[lineNumber].split('=')
            keyword = keyvalue[0].strip().lower()
            if (len(keyvalue) > 1):
                value = keyvalue[1].strip()
            else:
                value = ''

            # select lines that describe next entry
            if (keyword == 'version'):
                self.version = value
            if (keyword == 'date'):
                self.date = value
            if (keyword == 'name'):
                self.name = value
            if (keyword == 'description'):
                self.description = value
            if (keyword == 'asset class'):
                self.assetClassName = value
            if (keyword == 'latitude'):
                self.geometry[0] = float(value)
            if (keyword == 'longitude'):
                self.geometry[1] = float(value)
            if (keyword == 'latlong'):
                self.geometry = [float(s) for s in value.split(' ')]
            if (keyword == 'fragility class'):
                disasterfragilitypairs = [s for s in value.split(',')]
                for pair in disasterfragilitypairs:
                    df = pair.split(':')
                    DisasterClassID = df[0].strip()
                    fragilityType = df[1].strip()
                    # self.fragilities[DisasterClassID] = name2obj()
                    # self.fragilities[DisasterClassID].name = df[1].strip()
                    # self.fragilities[DisasterClassID].obj = None
                    self.fragilities.entries[fragilityType] = self.fragilities.fragilityTypeMappings[fragilityType]()
                    self.fragilities.entries[fragilityType].DClassName = DisasterClassID

    # TODO: looks incomplete...
    def isDestroyed(self, criteria, mode = 'simpleThreshold'):

        for f in self.fragilities.entries.values(): # for each fragility
            # which hazard will destroy us?
            intensity = f.disasterObj.getIntensity(self.geometry[0], self.geometry[1])
            # print self.geometry, intensity, criteria
            #probabilityOfAnnihilation = f.probability(criteria)
            if (mode == 'simpleThreshold'):
                threshold = None

                # TODO: Need generalized
                if (f.disasterType == 'Wind'):
                    threshold = f.MPHfromZoLossRatio(0.03, criteria)
                elif (f.disasterType == 'Flood'):
                    threshold = 0.5
                print 'intensity %f threshold %f' % (intensity, threshold)

                if (intensity > threshold):
                    self.destroyed = True
                    break
            elif (mode == 'stochastic'):
                # TODO: Random number needs to be more carefully generated.
                if (intensity > random.random()):
                    self.destroyed = True
                    break
            elif (mode == 'everythingMustGo'):
                self.destroyed = True
                break

        return self.destroyed        # logical OR of all of the above

#EXAMPLE# def isDestroyed(WFCinstance,Zo,mph,threshLoss):
#EXAMPLE#     # thresh is building Loss Ratio
#EXAMPLE#     #     X is mph; Y is LoadLoss; Z is meters
#EXAMPLE# 
#EXAMPLE#     # calculate the windspeed beyond which Loss Ratio is greater than threshLoss
#EXAMPLE#     threshMPH = WFCinstance.MPHfromZoLossRatio(Zo,threshLoss)
#EXAMPLE#     if ( mph >= threshMPH ):
#EXAMPLE#         return 1                # you sunk my battleship
#EXAMPLE#     else:
#EXAMPLE#         return 0                # airball

class AssetList:
    def __init__(self):
        self.description = ''
        self.entries = dict()

    def appendAssetTypesFromFile(self, filename):            # should this be:    appendTypesFromFile()
        assetFile = open(filename,'r')
        linesoftext = assetFile.readlines()
        
        newestEntry = len(self.entries)
        startLine = -1
        endLine = -1
        lineNumber = 0
        createNewEntry = 0
        while (lineNumber < len(linesoftext)):
            keyvalue = linesoftext[lineNumber].split('=')
            keyword = keyvalue[0].strip().lower()
            if (len(keyvalue) > 1):
                value = keyvalue[1].strip()
            else:
                value = ''

            #DEBUG# print('read line: keyword = * %s *' % keyword)
            # select lines that describe next entry
            if (keyword == 'version'):              # begins entry configuration section
                startLine = lineNumber
            elif (keyword == 'name'):               # ends entry configuration section
                name = keyvalue[1].strip().strip("'")  # key for asset dict
            elif (keyword == 'end'):                # ends entry configuration section
                endLine = lineNumber
                createNewEntry = 1

            if (createNewEntry == 1):
                #DEBUG# print('createNewEntry\n')
                # initialize new asset entry
                # IMPORTANT -- replace with factory that uses "VERSION" (rename this)
                #   to decide which subclass of Asset to instantiate here
                ##2DICT## self.entries.append(Asset())
                self.entries[name] = Asset()
                # fill the object with the data
                ##2DICT## self.entries[newestEntry].configureFromTextLines(linesoftext,startLine,endLine)
                self.entries[name].configureFromTextLines(linesoftext,startLine,endLine)
                # createNewEntry housekeeping
                createNewEntry = 0
                startLine = -1
                endLine = -1
                newestEntry += 1

            # while loop housekeeping
            lineNumber += 1
        assetFile.close()

    def display(self, map = None):

        if (map == None):
            plt.figure()

        for a in self.entries.values():
            y, x = a.geometry
            MARKER = 'o'
            COLOR = 'b'
            if (a.destroyed == True):
                MARKER = 'x'
                COLOR = 'r'
            if (x == 0 and y == 0):
                pass
            if (map == None):
                plt.scatter(x, y, marker=MARKER, c=COLOR)
            else:
                x, y = map(x, y)
                map.scatter(x, y, marker=MARKER, c=COLOR)

        if (map == None):
            plt.title('Assets')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.savefig('Assets.eps', format='eps')


# usage
# instantiate a list and load it with data from one or many files ('Hurricane...', 'Earthquake...', etc.)

# Baubles = AssetList()
# Baubles.appendAssetTypesFromFile('data/EP_Assets_20150824.txt')        #
##
## # EXAMPLES
## 
## Wind.entries[0].MPHfromZoLossRatio(0.03,0.5)    # find threshold wind speed
## 
## isDestroyed(Wind.entries[0],0.03,119,0.5)     # wind causes Loss Ratio less than 0.5 for Zo = 0.03 m
## isDestroyed(Wind.entries[0],0.03,120,0.5)     # wind causes greater Loss Ratio

