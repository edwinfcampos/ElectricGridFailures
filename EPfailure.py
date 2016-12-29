#!/usr/bin/env python
"""
Created on Thu May 28 14:12:14 2015
This computes the failure condition (yes/no) for an Electric Power
infrastructure exposed to a natural hazard such as a
tropical storm (flood and wind) or an earthquake, as well as a human threat.

Instead of fragility curves or damage functions (e.g., FEMA's Hazus model), 
this code uses Failure Curves, which are approximated as sigmoid functions.
            
Usage:
EPfailureFunction(parameters)
Examples:
kk = EPfailureFunction(pga_g=3.9,wind_mph=66.,floodlvl_m=4.2,human=0.4999)
EPfailureFunction(human=-0.5,wind_mph=80.,floodlvl_m=1.0,infrastructure='large_pwrplnt')

Input parameters:
- Natural Hazards & Human Threat:
pga_g : Peak ground acceleration (in g units) from an earthquake 
wind_mph : 1-minute Peak wind speed (in miles per hour)
floodlvl_m = Flood water level, in meters from the top of the 1st finished floor
human = Human threat probability (a real # from -1 to +1; e.g., -0.5)

- Electric Power Infrastructures: Geolocation may be obtained at http://www.epa.gov/enviro/html/fii/ez.html
lv_substation : Low Voltage Substation
mv_substation : Medium Voltage Substation
hv_substation : High Voltage Substation
ec_discircuit : Distribution Circuits Elevated Crossing
bc_discircuit : Distribution Circuits Buried Crossing
nc_discircuit : Distribution Circuits Non-Crossing
transmi_tower : Transmission towers
small_pwrplnt : Small Generating Power Plant
medim_pwrplnt : Medium Generating Power Plant
large_pwrplnt : Large Generating Power Plant

Look in Hazus-MH 2.1 CDMS Data Dictionary for p.92 (https://www.fema.gov/media-library/assets/documents/24609?id=5120)
(For Hurricanes & winds, infrastructure types depend on building # of stories, see Table D.45 in p. 122)
Transmission Substations
ESSL Low Voltage (115 KV) Substation [different combinations for with or without anchored components]
ESSM Medium Voltage (230 KV) Substation [different combinations for with or without anchored
ESSH High Voltage (500 KV) Substation [different combinations for with or without anchored components]
Distribution Circuits
EDC Distribution Circuits (either Seismically Designed Components or Standard Components)
Generation Plants
EPPL Large Power Plants ( > 500 MW ) [different combinations for with or without anchored components]
EPPM Medium Power Plants ( 100 - 500 MW ) [different combinations for with or without anchored
EPPS Small Power Plants ( < 100 MW ) [different combinations for with or without anchored components]


Outputs:
0 --> No, there was no failure, infrastructure is operating normally
1 --> Yes, there is failure, infrastructure stops operations.

Developed by Edwin Campos, ecampos@anl.gov
Last modification 2015 June 26
@author: Edwin Campos
"""
import numpy as np

def EPfailureFunction(pga_g=None,wind_mph=None,human=None,floodlvl_m=None):
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
        #Typically in a hurricane environment, the value of the maximum 3 second gust over a 1 minute period 
        # is on the order of 1.3 times (or 30% higher than) than the 1 min sustained wind. 
        # Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html
        gust_mph = 1.3 * wind_mph    # Recall that 1 mph wind = 1.3 mph gust  
        gust_threshold = 95.0   # miles per hour ; for example, gust_threshold = 150.0
        probability_wind_failure = 1.0 / (1.0 + np.exp(-gust_mph+gust_threshold))
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
    '''
    print(probability_human_failure,
          probability_earthquake_failure,
          probability_wind_failure,
          probability_flood_failure,
          probability_of_failure)
    '''      
    # 0 :  No, if prob. of failure <= 50%
    # 1 : Yes, if prob. of failure > 50%
    return failure

EPfailureFunction() 