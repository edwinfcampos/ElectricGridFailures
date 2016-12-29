'''
#! /usr/bin/env python
#! /usr/bin/ python
'''

"""
Created on Thu May 28 14:12:14 2015
This computes the failure condition (yes/no) for an critical
infrastructure exposed to a natural hazard such as a
tropical storm or an earthquake.

Instead of fragility curves or damage functions (e.g., FEMA's Hazus model), 
this code uses Failure Curves,
which are approximated as sigmoid functions.
            
Usage:
failureFunction(parameters)
print(failureFunction(human=1))

Input parameters:
peakgroundaccel_g = 
windspeed_mph = 
floodlvl_m = Flood water level, in meters from the top of the 1st finished floor
human = real # from -1 to +1 (e.g. -0.5)

Outputs:
0 --> No, there was no failure, infrastructure is operating normally
1 --> Yes, there is failure, infrastructure stops operations.

Developed by Edwin Campos, ecampos@anl.gov
Last modification 2015 June 26
@author: Edwin Campos
"""
#! /usr/bin/env python

import numpy as np

def failureFunction(pga_g=None,wind_mph=None,human=None,floodlvl_m=None):
    if human != None: # Human Threat
        probability_human_failure = human
    else:
        probability_human_failure = float('nan')
    
    if pga_g != None:  # Earthquake Hazard (fragility curves)
        pga_threshold = 0.4 # g units         
        probability_earthquake_failure = 1.0 / (1.0 + np.exp(10.0 * (-pga_g+pga_threshold) ))
    else:
        probability_earthquake_failure = float('nan')
    
    if wind_mph != None:  # Tropical Cyclone Winds Hazard
        wind_threshold = 70.0   # meters per second 
        probability_wind_failure = 1.0 / (1.0 + np.exp(-wind_mph+wind_threshold))
    else:
        probability_wind_failure = float('nan')
    
    if floodlvl_m != None:  # Flood Hazard (damage functions)
        # Functionality Threshold Depth, from FEMA Hazus Flood manual, Table 7.9, p.360
        # corresponding to flood depth beyond which the facility is considered non-operational
        functionality_threshold = 1.2192  # in meters, where 1.2192 m = 4 ft
        probability_flood_failure = 1.0 / ( 1.0 + np.exp(5.0*(-floodlvl_m + functionality_threshold)) )
    else:
        probability_flood_failure = float('nan') 
    
    if (wind_mph == None) and (pga_g == None) and (human == None) and (floodlvl_m == None):
        probability_of_failure = 0.0
    else:
        probability_of_failure = np.nanmean([probability_human_failure,  
                                 np.nanmax([probability_earthquake_failure,
                                            probability_wind_failure,
                                            probability_flood_failure])])
        
    failure = bool( round(probability_of_failure) )  
    
    print(probability_human_failure,
          probability_earthquake_failure,
          probability_wind_failure,
          probability_flood_failure,
          probability_of_failure)
          
    # 0 :  No, if prob. of failure <= 50%
    # 1 : Yes, if prob. of failure > 50%
    return failure

failureFunction() 