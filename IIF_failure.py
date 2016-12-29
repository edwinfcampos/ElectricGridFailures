#!/usr/bin/env python
"""
Created on Thu May 28 14:12:14 2015
This computes the failure condition (yes/no) for an infrastructure asset exposed to a natural hazard 
such as a hurricane (flood and wind) or an earthquake, as well as a human threat.
            
Usage:
failureFunction(parameters)
Examples:
kk = failureFunction(pga_g=3.9,wind_mph=66.,floodlvl_m=4.2,human=0.4999)
failureFunction(human=-0.5,wind_mph=80.,floodlvl_m=1.0,asset='ngpp')
failure = IIFf.failureFunction(asset='ngpp', wind_mph=hazard_wind_mph, gust_threshold_mph=asce_705_mph )

Input parameters:
- Natural Hazards & Human Threat:
pga_g : Peak ground acceleration (in g units) from an earthquake 
wind_mph : 1-minute Peak wind speed (in miles per hour)
wind_threshold_mph : Value for the sustained wind (in miles per hour) to be used as the fail/nofail threshold 
floodlvl_m = Flood water level, in meters from the top of the 1st finished floor
human = Human threat probability (a real # from -1 to +1; e.g., -0.5)

- Electric Power Infrastructures: Geolocation may be obtained at http://www.epa.gov/enviro/html/fii/ez.html
asset:
'npgg' : Natural Gas Processing Plant
'npp' : Nuclear Power Plant
'epp': Electric Power Plant
'eps' : Electric Power Substation
'eptl' : Electric Power Transmission Lines

Other assets that may be included in the future are...
'ngcs' : Natural Gas Compressor Station
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

Last modification 2015 Sep 1
Author: Edwin Campos, ecampos@anl.gov, edwinfcampos@aol.com
"""
import numpy as np
from scipy import interpolate
import math

want_fuzzylogic = 0  # 1 --> failureFunction will use sigmoid function with threshold specified by function inputs. else --> failureFunction will use hazard > threshold

def failureFunction(asset='ngpp',wind_mph=None,gust_threshold_mph=None, floodlvl_m=None,human=None,pga_g=None):
    if wind_mph != None:  # Tropical Cyclone Winds Hazard
        #wind_mph = wind_mph *1.2  # Just for testing, add 20% to the wind
        #Typically in a hurricane environment, the value of the maximum 3 second gust over a 1 minute period 
        # is on the order of 1.3 times (or 30% higher than) than the 1 min sustained wind. 
        # Source: http://www.aoml.noaa.gov/hrd/tcfaq/D4.html
        gust_mph = 1.3 * wind_mph    # Recall that 1 mph wind = 1.3 mph gust  
        
        # As threshold for Electric Power Plants, use the lower of (local wind load in building code ASCE7-05 or 50% loss in Hazus Hurricane Fig. N.2 Fragility Curve) 
        # From Steve Folga's email to Edwin Campos on 2015 Aug 21 
        if asset == 'epp': 
            # From Fig. N.2 in Hazus Hurricane Technical Manual
            # Industrial Building Loss Function, Figure N.2, No Reduction in Metal Deck Capacity, Reinforced Masonry Walls, Missile Environment A
            fragility_curve_winds = [60.254547, 75.526592, 79.856128, 83.420452, 89.025146, 95.140327,   # Peak Gust Wind Speed in Open Terrain (mph), Zo = 0.03 m, digitized by Mark Hereld on 2015-07-27
                                     102.022465, 103.296689, 108.140341, 109.669321, 111.199316, 113.239135, 
                                     116.805777, 119.608319, 122.157629, 124.705668, 126.743806, 128.016060, 
                                     129.289602, 134.893402, 137.440477, 141.767996, 144.058656, 147.113580, 
                                     149.404425, 152.713734, 154.240786, 157.803469, 160.346892, 162.127828, 
                                     162.890355, 164.924839, 168.992669, 170.009487, 172.298091, 176.365879, 
                                     180.432806, 181.703853, 186.278227, 189.581873, 195.172266, 200.000000]
            fragility_curve_loss = [0.000006, 0.000000, 0.007256, 0.010729, 0.034575, 0.068587,   # Building Loss Ratio, Zo = 0.03 m, digitized by Mark Hereld on 2015-07-27
                                    0.126311, 0.136496, 0.187386, 0.200959, 0.221302, 0.248424, 
                                    0.278956, 0.306084, 0.343359, 0.373861, 0.397582, 0.400985, 
                                    0.414540, 0.482293, 0.516160, 0.556808, 0.577131, 0.614372, 
                                    0.641453, 0.688833, 0.709138, 0.756508, 0.776813, 0.800493, 
                                    0.800497, 0.817413, 0.837716, 0.841101, 0.864774, 0.898591, 
                                    0.922260, 0.935782, 0.949307, 0.962828, 0.983106, 0.989865]
            interpolated_wind = interpolate.interp1d(fragility_curve_loss,fragility_curve_winds)  # Linear interpolation function for the fragility curve
            fragility_curve_threshold = 0.5   # Value of lost ratio to be used as the threshold between fail and nofail conditions
            Hazus_threshold_mph = interpolated_wind(fragility_curve_threshold)   # Evaluate the interpolated fragility curve at the loss threshold point            
            gust_threshold_mph = min(gust_threshold_mph,Hazus_threshold_mph)   # miles per hour ; for example, gust_threshold_mph = 150.0

        if  math.isnan(gust_mph) or math.isnan(gust_threshold_mph):  # This 'else' includes cases where gust_mph and/or gust_threshold_mph are Not-a-Number
            probability_wind_failure = float('nan') 
        elif want_fuzzylogic == 1:
            probability_wind_failure = 1.0 / (1.0 + np.exp(-gust_mph+gust_threshold_mph))
        else:
            if gust_mph > gust_threshold_mph : 
                probability_wind_failure = 1.0
            else:   
                probability_wind_failure = 0.0
        
    else:
        probability_wind_failure = float('nan')
    
    if floodlvl_m != None:  # Flood Hazard (damage functions)
        # Functionality Threshold Depth, from FEMA Hazus Flood manual, Table 7.9, p.360
        # corresponding to flood depth beyond which the facility is considered non-operational
        functionality_threshold = 1.2192  # in meters, where 1.2192 m = 4 ft
        probability_flood_failure = 1.0 / ( 1.0 + np.exp(5.0*(-floodlvl_m + functionality_threshold)) )
    else:
        probability_flood_failure = float('nan') 
    
    if human != None: # Human Threat
        probability_human_failure = human
    else:
        probability_human_failure = float('nan')
    
    if pga_g != None:  # Earthquake Hazard (fragility curves)
        pga_threshold = 0.4 # g units         
        probability_earthquake_failure = 1.0 / (1.0 + np.exp(10.0 * (-pga_g+pga_threshold) ))
    else:
        probability_earthquake_failure = float('nan')
    
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

failureFunction() 

'''
******************************************************************************
                         ***LICENSE NOTICE***
******************************************************************************
Copyright (c) 2015: Open Source Software Distribution MIT License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
******************************************************************************
'''