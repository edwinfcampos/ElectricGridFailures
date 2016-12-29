# version Hereld 2015-08-19

#   the basic Curve
#   is used to represent each of the four curves typical in a fragility plot
#   and is also used for interpolation calculations
#   # POSSIBLE BUG: might not work for decreasing and/or non-monotonic functions
                                        # AfromB -- helper function for interpolating curves.
def AfromB(Avec,Bvec,Bval):             # given B(A) return value of A that maps to Bval
#    # POSSIBLE BUG: might not work for decreasing and/or non-monotonic functions
    if ( len(Avec) != len(Bvec) ):
        print ('B(A) must be represented by equal length vectors: proceeding anyway\n')
    if ( Bval <= Bvec[0] ):
        return Avec[0]
    if ( Bval > Bvec[-1] ):
        return Avec[-1]
    for pnum in range(1,len(Bvec)):
        if ( Bval <= Bvec[pnum] ):      # is Bval between Bvec[pnum-1] and Bvec[pnum]?
            frac = ( Bval - Bvec[pnum-1] ) / ( Bvec[pnum] - Bvec[pnum-1] )
            Aval = Avec[pnum-1] + frac*(Avec[pnum]-Avec[pnum-1])
            break
    return Aval

class Curve:
    def __init__(self):
        self.name = ''
        self.cnum = -1
        self.nPoints = 0
        self.x = []
        self.y = []
    def XfromY(self,yval):      # return value of x that maps to yval
        return AfromB(self.x,self.y,yval)
    def YfromX(self,xval):      # return value of y that maps to xval
        return AfromB(self.y,self.x,xval)

#   Fragility classes
#       Fragility           the root class -- don't instantiate, it's basically abstract
#       FragilityCurve      *   represents any of several basic fragility types the are based on curves
#       WindFragilityCurve  *   *   specific instance that knows about wind, mph, Zo, and Load Loss
#       FragilityThreshold  *   simple fragility type only understands a threshold -- not implemented
#       FragilityList       contains potentially mixed list of any kind of Fragility
class Fragility(object):
    def __init__(self):
        self.name = 'unique'
        self.description = 'Tom Python'
        self.disasterlayer = 'Mad Cow Disease'
        self.versions = {}
        self.version = 'Penultimate 6.0beta'
        self.date = 'Manana'
        self.vulnerabilityClass = 'Invincible'
        self.disasterType = 'enter disaster type' # name will match one of: 'Wind', 'Flood', 'Earthquake', 'Darth Vadar', 'Voldermort'
        self.disasterObj = None                        # will become pointer to DisasterLayer with matching name

    def probability(self,criteria):
        return 0

class FragilityCurve(Fragility):
    def __init__(self):
        # super(FragilityCurve,self).__init__()
        self.xRange = []
        self.yRange = []
        self.xUnit = 'Hectares'
        self.yUnit = 'Fortnights'
        self.curves = []
        self.tempcurve = Curve()    # used for interpolation calculations
        self.versions = {'Hereld_2015-07-27'}

    def configure(self, lines, start, end):
        curveNumber = -1
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
            if (keyword == 'description'):
                self.description = value
            if (keyword == 'fragility class'):
                self.vulnerabilityClass = value
            if (keyword == 'x range'):              # [ lo high ]
                tokens = value.split(' ')
                self.xRange = [ float(tokens[0]), float(tokens[1]) ]
                stoken = value.split("'")           # capture quoted string
                self.xUnit = stoken[1]
            if (keyword == 'y range'):              # 
                tokens = value.split(' ')
                self.yRange = [ float(tokens[0]), float(tokens[1]) ]
                stoken = value.split("'")           # capture quoted string
                self.yUnit = stoken[1]
            if (keyword == 'curve name'):           # 
                self.curves[curveNumber].name = value
            if (keyword == 'curve number'):         # 
                # ignore this number
                self.curves.append(Curve())         # create new Curve instance and add it to list
                curveNumber += 1
                self.curves[curveNumber].cnum = value
            if (keyword == 'number of points'):     # 
                self.curves[curveNumber].nPoints = value
            if (keyword == 'x'):                    # x1 x2 x3 ...
                self.curves[curveNumber].x = [float(s) for s in value.split(' ')]
            if (keyword == 'y'):                    # y1 y2 y3 ...
                self.curves[curveNumber].y = [float(s) for s in value.split(' ')]

    def XfromYZ(self,zchrones,y,z):
        # generic interpolator to be used by subclasses that know their own units
        #
        # X is curves[].x                   len = nPoints
        # Y is curves[].y                   len = nPoints
        # Z[i] is isovalue for curves[i]    len = 4 typically
        #
        # zchrones provides list of isovalues corresponding to each curve
        # returns X value corresponding to (Y,Z)
        self.tempcurve.x = zchrones                 # Z values for curves 0,1,2,3
        self.tempcurve.y = [ self.curves[cnum].XfromY(y) for cnum in range(0,4) ]
                                                    # tempcurve represents Z(X)
        return self.tempcurve.YfromX(z)             # at what X do we reach Z?

class WindFragilityCurve(FragilityCurve):

    def __init__(self):
        super(WindFragilityCurve, self).__init__()
        self.disasterType = 'Wind'

    def MPHfromZoLossRatio(self,Zo,LossRatio):
        # the Wind subclass of FragilityCurve knows that its curves correspond to Zo values
        # other subclasses might not be about wind
        return FragilityCurve.XfromYZ(self,[ 0.03, 0.35, 0.70, 1.00 ],LossRatio,Zo)

class FragilityThreshold(Fragility):
    def __init__(self):
        super(FragilityThreshold,self).__init__()
        self.threshold = 0
        self.units = ''

    def configure(self,lines, start, end):
        curveNumber = -1
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
            if (keyword == 'description'):
                self.description = value
            if (keyword == 'fragility class'):
                self.vulnerabilityClass = value
            if (keyword == 'threshold'):
                self.threshold = value

    def probabilityDestroyed(self):
        return 1.0

class FragilityList:
    def __init__(self):
        self.description = ''

        # TODO: What should be the key for this dictionary? Fragility Class?
        self.entries = dict()
        
        self.fragilityTypeMappings = {
            'Curves':FragilityCurve,
            'WindCurves':WindFragilityCurve,
            'Threshold':FragilityThreshold,
            }

    def appendFragilityTypesFromFile(self,filename):
        fragilityFile = open(filename,'r')
        linesoftext = fragilityFile.readlines()

        startLine = -1
        endLine = -1
        lineNumber = 0
        createNewEntry = 0
        ftype = ''  # Fragility Type
        fclass = '' # Fragility Class
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
            elif (keyword == 'fragility type'):     # ends entry configuration section
                ftype = value.strip('\'')
            elif (keyword == 'fragility class'):     # ends entry configuration section
                fclass = value.strip('\'')
            elif (keyword == 'end'):                # ends entry configuration section
                endLine = lineNumber
                createNewEntry = 1

            if (createNewEntry == 1):
                #DEBUG# print('createNewEntry\n')
                # initialize new fragility entry
                # IMPORTANT -- replace with factory that uses "VERSION" (rename this)
                #   to decide which subclass of Fragility to instantiate here
                self.entries[fclass] = self.fragilityTypeMappings[ftype]()
                ### self.entries.append(WindFragilityCurve())
                # fill the object with the data
                self.entries[fclass].configure(linesoftext,startLine,endLine)
                # createNewEntry housekeeping
                createNewEntry = 0
                startLine = -1
                endLine = -1

            # while loop housekeeping
            lineNumber += 1
        fragilityFile.close()


# usage
# instantiate a list and load it with data from one or many files ('Hurricane...', 'Earthquake...', etc.)

# Wind = FragilityList()
# Wind.appendFragilityTypesFromFile('data/HurricaneFragilityDB.txt')
## 
## # EXAMPLES
## 
## print Wind.entries[0].MPHfromZoLossRatio(0.03,0.5)    # find threshold wind speed
#
## isDestroyed(Wind.entries[0],0.03,119,0.5)     # wind causes Loss Ratio less than 0.5 for Zo = 0.03 m
## isDestroyed(Wind.entries[0],0.03,120,0.5)     # wind causes greater Loss Ratio

