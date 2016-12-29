# version Hereld 2015-08-20
#   modified by Kim, 2015-08-27

from CoupledContext import CoupledContext
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

# One could do...
# tester = CoupledContext()
# tester.configureFromTextFile('ScenarioOne.txt')
# tester.linkAssets2Fragilities()
# tester.linkFragilities2Disasters()

# Alternatively...
tester = CoupledContext()
tester.load('ScenarioOne.txt')
tester.generateFirstOrderConsequences(0.1)

# VISUALIZATION
MINLON = -90
MAXLON = -73
MINLAT = 25
MAXLAT = 35
m = Basemap(llcrnrlon=MINLON, llcrnrlat=MINLAT, urcrnrlon=MAXLON, urcrnrlat=MAXLAT,
            projection='merc', resolution ='l', area_thresh=1000.)

m.drawcoastlines(linewidth=0.5)
m.drawstates()
# m.drawmapboundary(fill_color='aqua')
# m.fillcontinents(color='green')
m.shadedrelief()
m.drawparallels(np.arange(MINLAT,MAXLAT,5),labels=[1,1,0,0])
m.drawmeridians(np.arange(MINLON,MAXLON,5),labels=[0,0,0,1])

tester.display(m)

plt.title('Fictitious Hurricane Scenario')
plt.show()
## plt.savefig('scenario.eps', format='eps')
