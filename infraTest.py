# DEPENDENCIES
## from Infrastructure import ElectricPowerGrid
from Infrastructure import InfrastructureLayer

# RANDOM MODIFICATION OF INFRASTRUCTURE ASSETS IN SHAPEFILES
#datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/HurricaneSandy_fromCraig/ExampleData'
datadir = 'data/EPGridData'
outputplotname = 'FailureAnalyses'
ep_namehint = ['buses', 'lines']
myshp_epbuses = ep_namehint[0] # = ['buses', 'lines'] 
shapefilename = datadir+'/'+myshp_epbuses
EP = ElectricPowerGrid()
EP.open(shapefilename)
EP.randomlyTrashThisNetwork()
EP.saveNetwork('newfangledshapefile')

