# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:43:00 2015

@author: Edwin Campos and Mark Hereld
"""
# DEPENDENCIES
from IIF_infrastructurelayer import ElectricPowerGrid

# RANDOM MODIFICATION OF INFRASTRUCTURE ASSETS IN SHAPEFILES
datadir = '/Users/edwincampos/Documents/Argonne_Projects/2015_LDRD_Infrastructures/HurricaneSandy_fromCraig/ExampleData'
outputplotname = 'FailureAnalyses'
ep_namehint = ['buses', 'lines']
myshp_epbuses = ep_namehint[0] # = ['buses', 'lines'] 
shapefilename = datadir+'/'+myshp_epbuses
EP = ElectricPowerGrid()
EP.open(shapefilename)
EP.randomlyTrashThisNetwork()
EP.saveNetwork('newfangledshapefile')
