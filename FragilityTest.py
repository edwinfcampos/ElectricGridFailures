__author__ = 'kibaekkim'

from Fragility import FragilityList

fragilities = FragilityList()
#print(fragilities.fragilityTypeMappings['WindCurves'])
fragilities.appendFragilityTypesFromFile('data/HurricaneFragilityDB.txt')

print('number of fragilities', len(fragilities.entries))

#fragilities.entries[0].MPHfromZoLossRatio(0.03,0.5)    # find threshold wind speed

