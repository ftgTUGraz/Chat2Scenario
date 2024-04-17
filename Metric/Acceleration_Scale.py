"""
Author: Yongqi Zhao
Date Created: 2023-11-28
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
Reference: https://criticality-metrics.readthedocs.io/en/latest/
"""

import math
import pandas as pd

def DST(egoVehData, tgtVehData):
    """
    Deceleration to safety time (DST)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        metric_df (df): a dataframe including frame and DST ['frame', 'dst']
    ----------
    """
    # define a function to calculate desired metric
    def calculate_DST(v1, v2, x1, x2, ts):
        return float((v1 - v2)**2 / (2*(x1 - x2) - v2*ts))
    
    frameList = []
    dstList = []
    # tranversal both dataframes synchronously
    for (index1, egoRow), (index2, tgtRow) in zip(egoVehData.iterrows(), tgtVehData[0].iterrows()):
        currFrame = egoRow['frame']
        frameList.append(currFrame)
        v1 = egoRow['xVelocity']
        x1 = egoRow['x']
        v2 = tgtRow['xVelocity']
        x2 = tgtRow['x']
        ts = 0
        dst = calculate_DST(v1, v2, x1, x2, ts)
        dstList.append(dst)
    
    metric_df = pd.DataFrame({
        'frame': frameList,
        'dst': dstList
    })

    return metric_df


def RLoA(egoVehData, tgtVehData):
    """
    Required longitudinal acceleration (RLoA)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        metric_df (df): a dataframe including frame and RLoA ['frame', 'RLoA']
    ----------
    """

    # define the function to calculate euclidean distance
    def euclidean_distance(x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    # define the function to calculate RLoA
    def calculate_RLoA(a2_long, v1_long, v2_long, x1, y1, x2, y2):
        """
        Parameters
        ----------
        Inputs:
            a2_long: longitudinal acceleration of target vehicle 
            v1_long: longitudinal velocity of ego vehicle 
            v2_long: longitudinal velocity of target vehicle
            x1: coordinate of ego vehicle in x-axis 
            y1: coordinate of ego vehicle in y-axis  
            x2: coordinate of target vehicle in x-axis  
            y2: coordinate of target vehicle in y-axis 

        Returns:
            RLoA: Required longitudinal acceleration 
        ----------
        """
        opt1 = a2_long + ((v1_long - v2_long)**2)/(2*euclidean_distance(x1, y1, x2, y2))
        opt2 = 0
        return min(opt1, opt2)
    
    frameList = []
    RLoAList = []
    # tranversal both dataframes synchronously
    for (index1, egoRow), (index2, tgtRow) in zip(egoVehData.iterrows(), tgtVehData[0].iterrows()):
        currFrame = egoRow['frame']
        frameList.append(currFrame)
        x1 = egoRow['x']
        y1 = egoRow['y']
        v1_long = egoRow['xVelocity']
        x2 = tgtRow['x']
        y2 = tgtRow['y']
        v2_long = tgtRow['xVelocity']
        a2_long = tgtRow['xAcceleration']
        rloa = calculate_RLoA(a2_long, v1_long, v2_long, x1, y1, x2, y2)
        RLoAList.append(rloa)

    metric_df = pd.DataFrame({
        'frame': frameList,
        'RLoA': RLoAList
    })

    return metric_df


def RLaA(egoVehData, tgtVehData):
    """
    Required lateral acceleration (RLaA)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        metric_df (df): a dataframe including frame and RLaA ['frame', 'RLaA']
    ----------
    """
    # # left right driving direction threshold --> only valid for highD
    # lane_threshold = (max(tracks['laneId']) - min(tracks['laneId']))/2

    # define the function to calculate RLaA
    def calculate_RLaA(a2_lat_left, v2_lat, v1_lat, TTC, w1, w2, y2, y1, a2_lat_right):
        # required lateral acceleration in the left direction
        a1_lat_left = a2_lat_left + (2*(v2_lat - v1_lat))/TTC + (2/(TTC**2))*((-(w1 + w2)/2) + y2 - y1)

        # required lateral acceleration in the right direction
        a1_lat_right = a2_lat_right + (2*(v2_lat - v1_lat))/TTC + (2/(TTC**2))*(((w1 + w2)/2) + y2 - y1)

        a_lat_req = min(a1_lat_left, a1_lat_right)

        return a_lat_req
    

    drivePos = False
    if egoVehData['x'].values[-1] - egoVehData['x'].values[0] > 0:
        drivePos = True

    frameList = []
    RLaAList = []
    # tranversal both dataframes synchronously
    for (index1, egoRow), (index2, tgtRow) in zip(egoVehData.iterrows(), tgtVehData[0].iterrows()):
        currFrame = egoRow['frame']
        frameList.append(currFrame)
        v2_lat = tgtRow['yVelocity']
        v1_lat = egoRow['yVelocity']
        TTC = egoRow['ttc']
        w1 = egoRow['width']
        w2 = tgtRow['width']
        y2 = tgtRow['y']
        y1 = egoRow['y']
        a2_lat_left = None
        a2_lat_right = None
        if drivePos:
            a2_lat_left = -tgtRow['yAcceleration']
            a2_lat_right = tgtRow['yAcceleration']
        else:
            a2_lat_left = tgtRow['yAcceleration']
            a2_lat_right = -tgtRow['yAcceleration']

        rlaa = calculate_RLaA(a2_lat_left, v2_lat, v1_lat, TTC, w1, w2, y2, y1, a2_lat_right)
        RLaAList.append(rlaa)

    metric_df = pd.DataFrame({
        'frame': frameList,
        'RLoA': RLaAList
    })

    return metric_df
    

def RA(egoVehData, tgtVehData):
    """
    Required acceleration (RA)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        metric_df (df): a dataframe including frame and RA ['frame', 'RA']
    ----------
    """

    # define the function to calculate "required lateral acceleration"
    def calculate_RLaA(a2_lat_left, v2_lat, v1_lat, TTC, w1, w2, y2, y1, a2_lat_right):
        # required lateral acceleration in the left direction
        a1_lat_left = a2_lat_left + (2*(v2_lat - v1_lat))/TTC + (2/(TTC**2))*((-(w1 + w2)/2) + y2 - y1)

        # required lateral acceleration in the right direction
        a1_lat_right = a2_lat_right + (2*(v2_lat - v1_lat))/TTC + (2/(TTC**2))*(((w1 + w2)/2) + y2 - y1)

        a_lat_req = min(a1_lat_left, a1_lat_right)

        return a_lat_req
    
    # define the function to calculate euclidean distance
    def euclidean_distance(x1, y1, x2, y2):
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)

    # define the function to calculate RLoA
    def calculate_RLoA(a2_long, v1_long, v2_long, x1, y1, x2, y2):
        opt1 = a2_long + ((v1_long - v2_long)**2)/(2*euclidean_distance(x1, y1, x2, y2))
        opt2 = 0
        return min(opt1, opt2)
    
    drivePos = False
    if egoVehData['x'].values[-1] - egoVehData['x'].values[0] > 0:
        drivePos = True
    frameList = []
    RAList = []
    # tranversal both dataframes synchronously
    for (index1, egoRow), (index2, tgtRow) in zip(egoVehData.iterrows(), tgtVehData.iterrows()):
        currFrame = egoRow['frame']
        frameList.append(currFrame)

        a2_lat_left = None
        a2_lat_right = None
        if drivePos:
            a2_lat_left = -tgtRow['yAcceleration']
            a2_lat_right = tgtRow['yAcceleration']
        else:
            a2_lat_left = tgtRow['yAcceleration']
            a2_lat_right = -tgtRow['yAcceleration']
        
        v2_lat = tgtRow['yVelocity']
        v1_lat = tgtRow['yVelocity']
        TTC = egoRow['ttc']
        w1 = egoRow['width']
        w2 = tgtRow['width']
        y2 = tgtRow['y'].values[0]
        y1 = egoRow['y']

        # calculate RLaA
        RLaA_Value = calculate_RLaA(a2_lat_left, v2_lat, v1_lat, TTC, w1, w2, y2, y1, a2_lat_right)

        ## get all parameters for required longitudinal acceleration
        a2_long = tgtRow['xAcceleration']
        v1_long = egoRow['xVelocity']
        v2_long = tgtRow['xVelocity']
        x1 = egoRow['x']
        y1 = egoRow['y']
        x2 = tgtRow['x']
        y2 = tgtRow['y']
        RLoA_Value = calculate_RLoA(a2_long, v1_long, v2_long, x1, y1, x2, y2)

        ## calculate required acceleration
        RA_Value = math.sqrt(RLaA_Value**2 + RLoA_Value**2)
        RAList.append(RA_Value)

    metric_df = pd.DataFrame({
        'frame': frameList,
        'RLoA': RAList
    })

    return metric_df