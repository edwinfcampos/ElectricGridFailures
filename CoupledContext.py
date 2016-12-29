# version Hereld 2015-08-20

from DisasterLayer import DisasterList, Hurricane, Flood
from Infrastructure import InfrastructureLayer, InfrastructureList
from Fragility import FragilityList
from Asset import AssetList

#   Context Classes
#       Asset           the root class -- don't instantiate, it's basically abstract
#       AssetList       contains potentially mixed list of any kind of Asset
class CoupledContext(object):
    def __init__(self):
        self.name = 'Gigantor'
        self.description = 'Top level object that describes and runs scenarios'
        self.versions = {'Hereld_2015-07-27'}   # list of compatible versions
        self.version = 'Penultimate 6.0beta'    # this version
        self.date = 'Manana'        # date this asset description created in db
        self.disasters       = DisasterList()       # 
        self.infrastructures = InfrastructureList() #
        self.assets          = AssetList()          # 
        self.fragilities     = FragilityList()      # 

        self.disasterLayerMappings = {
            'Wind':Hurricane,
            'Flood':Flood}
        self.infrastructureLayerMappings = {
            'ElectricPowerGrid':InfrastructureLayer,
            'NaturalGasSystem':InfrastructureLayer}

    # 1. Open up the grand configuration file
    # 2. Load up all of the data for disaster layers, infrastructure layers, assets, and fragilities
    # 3. Link the data objects
    def load(self,configurationfilename):
        self.configureFromTextFile(configurationfilename)
        self.linkInfrastructures2Assets() # link each infrastructure to assets
        self.linkAssets2Fragilities()     # tell each Asset where to find its Fragility data
        self.linkFragilities2Disasters()  # tell each Fragility where to find its Disaster data

    # Execute the entire coupled problem to remove all destroyed assest from system
    def generateFirstOrderConsequences(self, criteria):
        # tuck criteria into it's safe place
        # implement the code on the first page of the Architecture diagram, looping over infrastructures and assets
        # save the appropriate data for use downstream by the iterative simulation code
        for infra in self.infrastructures.entries.values(): # for each infrastructure
            for elem in infra.elements:                     # for each infrastructure element
                for a in elem.assets:                       # for each of the assets
                    if (a.isDestroyed(criteria)):           # see if it is destroyed
                        print "Asset (%s) is destroyed." % a.name
                        elem.removed = True                 # mark as destroyed
                        break
            infra.save(infra.filename)                      # save resulting destroyed infrastructure

    def configureFromTextLines(self, lines, start, end):
        for lineNumber in range(start,end):
            keyvalue = lines[lineNumber].split('=')
            keyword = keyvalue[0].strip().lower()
            if (len(keyvalue) > 1):
                value = keyvalue[1].strip()
            else:
                value = ''

            # select lines that describe next entry
            if (keyword == 'version'):              # config format conforming version
                self.version = value
            if (keyword == 'date'):                 # creation date for this config
                self.date = value
            if (keyword == 'name'):                 # identifying name (user determined)
                self.name = value
            if (keyword == 'description'):          # scenario/experiment description
                self.description = value
            # for d in ['Earthquake', 'Wind', 'Flood', 'Drought', 'StockingRun', 'ZombieWar']:
            #     if (keyword == d.lower()):           # 
            #         self.disasters[d] = XXXXXX() # factory thingy?
            #         self.disasters[d].configureFromTextFile(value)
            for d in self.disasterLayerMappings:
                if (keyword == d.lower()):
                    self.disasters.appendDisasterTypesFromFile(value.strip('\''), d)
            if (keyword in (infra.lower() for infra in self.infrastructureLayerMappings)):
                self.infrastructures.appendFragilityTypesFromFile(value.strip('\''))

            # Append assets
            if (keyword == 'assets'):
                self.assets.appendAssetTypesFromFile(value.strip('\''))

            # Append fragilities
            if (keyword == 'fragilities'):
                self.fragilities.appendFragilityTypesFromFile(value.strip('\''))

##EXAMPLE##            if (keyword == 'asset class'):
##EXAMPLE##                self.assetClassName = value
##EXAMPLE##            if (keyword == 'latlong'):
##EXAMPLE##                self.geometry = [float(s) for s in value.split(' ')]
##EXAMPLE##            if (keyword == 'fragility classes'):
##EXAMPLE##                disasterfragilitypairs = [s for s in value.split(',')]
##EXAMPLE##                for pair in disasterfragilitypairs:
##EXAMPLE##                    df = pair.split(':')
##EXAMPLE##                    #print('df    = *%s*' % df)
##EXAMPLE##                    #print('    d = *%s*' % df[0])
##EXAMPLE##                    #print('    f = *%s*' % df[1])
##EXAMPLE##                    self.fragilities[df[0].strip()] = df[1].strip()

    def configureFromTextFile(self,configfilename):
        configFile = open(configfilename,'r')
        linesoftext = configFile.readlines()
        
        # newestEntry = len(self.entries)
        startLine = -1
        lineNumber = 0
        while (lineNumber < len(linesoftext)):
            keyvalue = linesoftext[lineNumber].split('=')
            keyword = keyvalue[0].strip().lower()

            #DEBUG# print('read line: keyword = * %s *' % keyword)
            # select lines that describe next entry
            if (keyword == 'version'):              # begins entry configuration section
                startLine = lineNumber
            elif (keyword == 'end'):                # ends entry configuration section
                if (startLine < 0):
                    print('Version keyword not found -- invalid config file format')
                    break
                endLine = lineNumber
                self.configureFromTextLines(linesoftext,startLine,endLine)
                break

            # while loop housekeeping
            lineNumber += 1
        configFile.close()

    # Link each infrastructure to assets
    #   After this, InfrastructureElement has a set of assets based on geo-location.
    def linkInfrastructures2Assets(self):
        for infra in self.infrastructures.entries.values(): # for each infrastructure
            for elem in infra.elements:                     # for each infrastructure element
                elem.findAssets(self.assets)                # find assets of this element

    # Link each asset to fragilities
    def linkAssets2Fragilities(self):
        for a in self.assets.entries.values():           # for each asset
            # TODO: Could this be enough?
            a.fragilities = self.fragilities
            # for f in a.fragilities.entries.values():     # for each fragility of the asset
            #     f.obj = self.fragilities.entries[f.name] # expects fragilitylist to be a dictionary

    # Link each fragility to a disaster (N-to-one)
    def linkFragilities2Disasters(self):
        for f in self.fragilities.entries.values():
            f.disasterObj = self.disasters[f.disasterType]   # assuming disasters is a dictionary

    def display(self, map = None):
        self.disasters.display(map)
        self.assets.display(map)

## Baubles = AssetList()
## Baubles.appendAssetTypesFromFile('EP_Assets_20150819.txt')        #
## 
## # EXAMPLES
## 
## Wind.entries[0].MPHfromZoLossRatio(0.03,0.5)    # find threshold wind speed
## 
## isDestroyed(Wind.entries[0],0.03,119,0.5)     # wind causes Loss Ratio less than 0.5 for Zo = 0.03 m
## isDestroyed(Wind.entries[0],0.03,120,0.5)     # wind causes greater Loss Ratio

