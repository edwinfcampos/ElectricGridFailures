#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 11:01:46 2015

This code defines the object oriented classes for the critical infrastructure assets
in the Integrated Infrastructure Forecaster system

For a tutorial on Object Oriented Programming, see for example: 
http://www.tutorialspoint.com/python/python_classes_objects.htm
or
http://www.jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/


@author: edwincampos
Last modification: 2015 Aug 18
"""

# DEPENDENCIES
import IIF_failure as IIFf
from Fragility import FragilityList, isDestroyed

#### CREATING THE BASE CLASS ##################################################

class Asset(object):
    """An Infrastructure asset
    Attributes:
        assetID: ...
        assetType: ...
        lat: ...
        long: ...
        belongsToNode: ...
        belongsToEdge: ...
        asset_type: ...
    """
    def isDestroyedbywind(self):
        """"Return a string representing the type of vehicle this is."""
        pass
    def isDestroyedbyflood(self):
        """"Return a string representing the type of vehicle this is."""
        pass
    def getLatLong(self):
        """"Return a string representing the type of vehicle this is."""
        pass

#### CREATING AN INFRASTRUCTURE SUBCLASS OBJECT ###############################
        
class EPasset(Asset):
    """Electric Power grid asset."""
    assetType = 'EP' 
    def isDestroyedbywind(self):
        """"Return a string representing the type of vehicle this is."""
        pass
    def isDestroyedbyflood(self):
        """"Return a string representing the type of vehicle this is."""
        pass
    def getLatLong(self):
        """"Return a string representing the type of vehicle this is."""
        pass

# CREATING THE ASSET SUBCLASS OBJECTS

class PowerPlant(EPasset):
    """Electric Power grid asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Power Plant will fails
        Using the FEMA Hazus Hurricane Technical Manual, Fig.N.3"""
        # Run Fragility.py to determine if the bus will fail, where self corresponds to the wind gust at the Power Plant, in miles per hour
        probability_wind_failure = bool( isDestroyed(WindFragility.entries[2],0.03,self,0.5) )     
        # isDestroyed(HazusFig.N.number,terrain_surface_roughness_m,windgust_mph,failurethreshold_ratio) ), wind causes failure threshold Ratio less than 0.5 for roughness Zo = 0.03 m
        return probability_wind_failure
    def getLatLong(self):
        """Return the price for which we would pay to purchase the vehicle."""
        if self.sold_on is None:
            return [0.0,0.0]  # Not yet sold
        return [self.lat, self.lon]
        
class Substation(EPasset):
    """Electric Power Substation asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Power Plant will fails
        Using the FEMA Hazus Hurricane Technical Manual, Fig.N.1"""
        # Run Fragility.py to determine if the bus will fail, where self corresponds to the wind gust at the substation, in miles per hour
        probability_wind_failure = bool( isDestroyed(WindFragility.entries[0],0.03,self,0.5) )     
        # isDestroyed(HazusFig.N.number,terrain_surface_roughness_m,windgust_mph,failurethreshold_ratio) ), wind causes failure threshold Ratio less than 0.5 for roughness Zo = 0.03 m
        return probability_wind_failure
    def getLatLong(self):
        """Return the price for which we would pay to purchase the vehicle."""
        if self.sold_on is None:
            return [0.0,0.0]  # Not yet sold
        return [self.lat, self.lon]

class TransmissionLine(EPasset):
    """Electric Power Transmission Line asset."""
    def isDestroyedbywind(self): # Tropical Cyclone Winds Hazard
        """Return True or False criteria to determine if the Transmission Line will fails"""
        if wind_mph != None:  
            #Typically in a hurricane environment, the value of the maximum 3 second gust over a 1 minute period 
            # is on the order of 1.3 times (or 30% higher than) than the 1 min sustained wind. 
            # Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html
            gust_mph = 1.3 * wind_mph    # Recall that 1 mph wind = 1.3 mph gust  
            """Using the Building Construction Code ASCE 7-05"""
            # Run function gust_threshold_ASCE7 (still to be build) to determine wind load in building code, where self corresponds to the wind gust at the site, in miles per hour
            #gust_threshold = gust_threshold_ASCE7(05,self.lat,self.lon)   # gust_threshold_ASCE7(code_year,site_latitude_degrees,site_longitude_degrees,current_windgust_mph) )
            gust_threshold = 95.0   #gust_threshold_ASCE7 # miles per hour ; for example, gust_threshold = 150.0
            probability_wind_failure = 1.0 / (1.0 + np.exp(-gust_mph+gust_threshold))
        else:
            probability_wind_failure = float('nan')
        return probability_wind_failure

class DistributionLine(EPasset):
    """Electric Power Distribution Line asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Power Plant will fails
        Using the Building Construction Code ASCE 7-05"""
        # Run function isDestroyed_ASCE7 (still to be build) to determine if the bus will fail, where self corresponds to the wind gust at the site, in miles per hour
        probability_wind_failure = isDestroyed_ASCE7(05,self.lat,self.lon,self.gust_mph)   # isDestroyed_ASCE7(code_year,site_latitude_degrees,site_longitude_degrees,current_windgust_mph) )
        return probability_wind_failure

#### CREATING AN INFRASTRUCTURE SUBCLASS OBJECT ###############################

class NGasset(Asset):
    """Natural Gas asset."""
    assetClass = 'NG'
    def assetType(self):
        """"Return a string representing the type of asset this is."""
        return 'NG'

# CREATING THE ASSET SUBCLASS OBJECTS

class ProcessingPlant(NGasset):
    """Natural Gas Processing Plant asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Power Plant will fails
        Using the Building Construction Code ASCE 7-05"""
        # Run function isDestroyed_ASCE7 (still to be build) to determine if the bus will fail, where self corresponds to the wind gust at the site, in miles per hour
        probability_wind_failure = isDestroyed_ASCE7(05,self.lat,self.lon,self.gust_mph)    
        # isDestroyed_ASCE7(code_year,site_latitude_degrees,site_longitude_degrees,current_windgust_mph) )
        return probability_wind_failure

class CompressorStation(NGasset):
    """Natural Gas Compressor Station asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Power Plant will fails
        Using the Building Construction Code ASCE 7-05"""
        # Run function isDestroyed_ASCE7 (still to be build) to determine if the bus will fail, where self corresponds to the wind gust at the site, in miles per hour
        probability_wind_failure = isDestroyed_ASCE7(05,self.lat,self.lon,self.gust_mph)   
        # isDestroyed_ASCE7(code_year,site_latitude_degrees,site_longitude_degrees,current_windgust_mph) )
        return probability_wind_failure

class ControlValve(NGasset):
    """Natural Gas Control Valve asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Control Valves will fails
        Using Stephen Folga personnal communication on 2015 Aug 12 (email to Edwin Campos)"""
        # Run function isDestroyed_ASCE7 (still to be build) to determine if the bus will fail, where self corresponds to the wind gust at the site, in miles per hour
        probability_wind_failure = bool(0)     
        # Control Valves are not affected by wind hazards
        return probability_wind_failure

class PipeLine(NGasset):
    """Natural Gass Pipeline asset."""
    def isDestroyedbywind(self):
        """Return True or False criteria to determine if the Control Valves will fails
        Using Stephen Folga personnal communication on 2015 Aug 12 (email to Edwin Campos)"""
        # Run function isDestroyed_ASCE7 (still to be build) to determine if the bus will fail, where self corresponds to the wind gust at the site, in miles per hour
        probability_wind_failure = bool(0)     
        # Control Valves are not affected by wind hazards
        return probability_wind_failure


'''        
#Por aca voy
class Network:
   'Common base class for all infrastructures'
   nodeList = 0
   
   edgeList = 0

   def __init__(self, name, salary):
      self.name = name
      self.salary = salary
      Employee.empCount += 1
   
   def open(self):
     print "Total Employee %d" % Employee.empCount

   def loadNetwork(self):
      print "Name : ", self.name,  ", Salary: ", self.salary

# CREATING INSTANCE OBJECTS
"This would create first object of Employee class"
emp1 = Employee("Zara", 2000)
"This would create second object of Employee class"

# ACCESSING ATTRIBUTES
emp2 = Employee("Manni", 5000)
emp1.displayEmployee()
emp2.displayEmployee()
print "Total Employee %d" % Employee.empCount
'''