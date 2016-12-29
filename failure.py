# -*- coding: utf-8 -*-
"""
This computes the failure condition (yes/no) for an critical
infrastructure exposed to a natural hazard such as a
tropical storm or an earthquake.

Usage:
failure(parameters)
Input parameters:
peakgroundaccel_g = 
windspeed_mph = 
floodlevel_m =
Outputs:
0 --> No, there was no failure, infrastructure is operating normally
1 --> Yes, there is failure, infrastructure stops operations.

Developed by Edwin Campos, ecampos@anl.gov
Last modification 2015 June 16
"""

#! /usr/bin/env python

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

#***Fragility Curve for Earthquakes***
# X axis: Peak ground accelerations, in g
pga_values = np.arange(0.,1.5,.1) 
# X-axis value corresponding to 50% probability of failure
pga_threshold = 0.4 # g units
# Y axis: Failure probability, %
sigmoid_failure_earthquake = 1.0 / (1.0 + np.exp(15.0 * (-pga_values+pga_threshold) )) 

#***Fragility Curve for Hurricane winds***
# X axis: Peak Wind Speed, in miles per hour, over a 1-minute period, measured at 10m agl
wind_values = np.arange(0.,180.,1.) 
# Gusts, in miles per hour, corresponding to the 3-5 second wind peak
# Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html 
gust_mph = 1.3 * wind_values 
# X-axis value corresponding to 50% probability of failure
gust_threshold = 150.0   # miles per hour 
wind_threshold = gust_threshold / 1.3 # Approx. 115.4 miles per hour
# Y axis: Failure probability, %
#sigmoid_failure_wind = 1.0 / (1.0 + np.exp(-wind_values+wind_threshold))
sigmoid_failure_wind = 1.0 / (1.0 + np.exp(-gust_mph+gust_threshold))
        
#***Damage Function for Flood***
# X axis Water Flooding Depth 
floodlvl_ft = np.arange(0.,10,0.5)  #Flood water level, in feet from the top of the 1st finished floor
floodlvl_values = floodlvl_ft / 3.2808 #Flood water level, in meters from the top of the 1st finished floor
# X-axis value corresponding to flood depth beyond which the facility is considered non-operational
# Functionality Threshold Depth, from FEMA Hazus Flood manual, Table 7.9, p.360
functionality_threshold = 1.2192  # in meters, where 1.2192 m = 4 ft
sigmoid_failure_flood = 1.0 / ( 1.0 + np.exp(5.0*(-floodlvl_values + functionality_threshold)) )  
#The continuation line character is a backslash, \

# Flood Damage Function Values from Table 7.9 in FEMA Hazus Floods manual, p. 360
floodlvl_Table_ft = np.arange(0.,11,1.0) #[0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.] 
floodlvl_Table_m = floodlvl_Table_ft / 3.2808  # Table gives values in ft, and here we use meters
PercentDamage_substation = [0,0.02,0.04,0.06,0.07,0.08,0.09,0.10,0.12,0.14,0.15] # Substation of any voltage
PercentDamage_SmallPwPlant = [0.,0.025,0.05,0.075,0.10,0.125,0.15,0.175,0.20,0.25,0.30] #'Small Power Plant'                          

# set tick width
mpl.rcParams['xtick.major.size'] = 4
mpl.rcParams['xtick.major.width'] = 1.0
mpl.rcParams['xtick.minor.size'] = 2
mpl.rcParams['xtick.minor.width'] = 1

#Main plots
plt.plot(pga_values,sigmoid_failure_earthquake, linewidth=3.0)
plt.ylim(-0.005,1.01)
plt.minorticks_on() #Plot minor ticks on both axis

# Earthquake Fragility Curve
plt.title('Earthquake Fragility Curve as a Sigmoid Function')
plt.minorticks_on() #Plot minor ticks on both axis

plt.xlabel('Peak Ground Acceleration (g)')
plt.ylabel('Failure Probability')
plt.plot([min(pga_values),pga_threshold],[0.5,0.5], 
         linestyle='--',color='red', label='50%')
plt.plot([pga_threshold,pga_threshold],[0.0,0.5], 
         linestyle='--',color='red')
plt.savefig('failure_earthquake.png', dpi=200)
plt.show()

# Hurricane Fragility Curve
plt.plot(wind_values,sigmoid_failure_wind, linewidth=3.0)
plt.ylim(-0.005,1.01)
plt.title('Hurricane Fragility Curve as a Sigmoid Function')
plt.xlabel('Wind Speed (miles/hour)')
plt.ylabel('Failure Probability')
plt.plot([min(wind_values),wind_threshold],[0.5,0.5], 
         linestyle='--',color='red', label='50%')
plt.plot([wind_threshold,wind_threshold],[0.0,0.5], 
         linestyle='--',color='red')
plt.savefig('failure_hurricane.png', dpi=200)
plt.show()

# Flood Damage Function
plt.plot(floodlvl_values,sigmoid_failure_flood, linewidth=3.0)
plt.ylim(-0.005,1.01)
plt.title('Flood Damage Function as a Sigmoid Function')
plt.xlabel('Water Depth (m)')
plt.ylabel('Failure Probability')
plt.plot([min(floodlvl_values),functionality_threshold],[0.5,0.5], 
         linestyle='--',color='red', label='50%')
plt.plot([functionality_threshold,functionality_threshold],[0.0,0.5], 
         linestyle='--',color='red')
'''
plt.plot(floodlvl_Table_m , PercentDamage_SmallPwPlant,
         linestyle='--',color='blue', label='Small Power Plant')
plt.plot(floodlvl_Table_m , PercentDamage_substation,
         linestyle='--',color='green', label='Substation')      
plt.savefig('failure_flood.png', dpi=200)
'''
plt.show()


def failureFunction(pga_g=None,wind_mph=None,human=None):
    if (human != None) and (human != 0): # Human Threat
        print('human was not passed or is set equal to ', human)         
        probability_of_failure = 1.0
    else:
        if pga_g != None:  # Earthquake Hazard
            print('pga_g was passed, and it is equal to ', pga_g)
            pga_threshold = 0.4 # g units         
            probability_of_failure = 1.0 / (1.0 + np.exp(10.0 * (-pga_g+pga_threshold) ))
        else:
            print ('pga_g was NOT passed')
     
        if wind_mph == None:  # Tropical Cyclone Hazard
            print ('wind_mph was NOT passed')
        else:
            print('wind_mph was passed, and it is equal to ', wind_mph)
            #Fragility Curve as a sigmoid function
            wind_threshold = 70.0    
            probability_of_failure = 1.0 / (1.0 + np.exp(-wind_mph+wind_threshold))
          
        if (wind_mph == None) and (pga_g == None) and ((human == None) or (human == 0)):
            probability_of_failure = 0.0
    
    failure = bool( round(probability_of_failure) )  
    # 0 :  No, if prob. of failure <= 50%
    # 1 : Yes, if prob. of failure > 50%
    return failure

failureFunction()   
        
    