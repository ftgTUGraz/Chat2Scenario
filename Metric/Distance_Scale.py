"""
Author: Yongqi Zhao
Date Created: 2023-11-28
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
Reference: https://criticality-metrics.readthedocs.io/en/latest/
"""
from shapely.geometry import Point, Polygon, LineString
import math
import numpy as np
import pandas as pd

def AGS():
    """
    Accepted Gap Size (AGS)

    Parameters:
    ----------
    Inputs:

    Returns:
        
    ----------
    prediction model is needed --> Metric is only for online
    """
    pass


def DCE():
    """
    Distance of Closest Encounter (DCE)

    Parameters:
    ----------
    Inputs:

    Returns:
        
    ----------
    refer to TTCE (Time to Closest Encounter)
    """
    pass


def HW():
    """
    Headway (HW)

    Parameters:
    ----------
    Inputs:

    Returns:
        
    ----------
    refer to THW (Time Headway) --> already exist in highD
    """
    pass


def PSD(egoVehData, tgtVehData, CA):
    """
    Proportion of Stopping Distance (PSD)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        metric_df (df): a dataframe including frame and PSD ['frame', 'psd']      
    ----------
    refer to THW (Time Headway)
    """
    # define conflict area using polygon
    conflict_area = Polygon(CA)

    # MSD calculation
    def MSD(v1, a1_long_min):
        v1 = np.linalg.norm(v1)
        a1_long_min = abs(a1_long_min)
        return (v1**2)/(2*a1_long_min)
    
    frameList = []
    psdList = []
    # tranversal both dataframes synchronously
    for (index1, egoRow), (index2, tgtRow) in zip(egoVehData.iterrows(), tgtVehData.iterrows()):
        currFrame = egoRow['frame']
        frameList.append(currFrame)
        # skip if acceleration is zero
        if egoRow['xAcceleration'] == 0:
            psdList.append(np.nan)
            continue
        # current position 
        curr_x = egoRow['x']
        curr_y = egoRow['y']
        curr_pos = Point(curr_x, curr_y)
        # calculate distance 
        curr_dst = curr_pos.distance(conflict_area) 
        # calculate MSD
        curr_v1 = math.sqrt(egoRow['xVelocity']**2 + egoRow['yVelocity']**2)
        curr_a1_long = egoRow['xAcceleration']
        curr_msd = MSD(curr_v1, curr_a1_long)
        # calculate PSD
        curr_psd = curr_dst/curr_msd
        # insert the calculate value to dataframe
        psdList.append(curr_psd)
        
    metric_df = pd.DataFrame({
        'frame': frameList,
        'psd': psdList
    })

    return metric_df


