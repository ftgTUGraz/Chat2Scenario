"""
Author: Yongqi Zhao
Date Created: 2023-11-28
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
Reference: https://criticality-metrics.readthedocs.io/en/latest/
"""
import pandas as pd

def LongJ(egoVehData, frame_rate):
    """
    Longitudinal jerk (LongJ)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        frame_rate (int): frame rate of the data

    Returns:
        metric_df (df): a dataframe including frame and xJerk ['frame', 'xJerk']     
    ----------
    """
    egoVehDataCopy = egoVehData.copy()

    # time step
    tStep = 1/frame_rate
    # calculate the difference in acceleration
    egoVehDataCopy['xJerk'] = egoVehDataCopy['xAcceleration'].diff()/tStep  

    metric_df = pd.DataFrame({
        'frame': egoVehDataCopy['frame'],
        'xJerk': egoVehDataCopy['xJerk']
    })

    return metric_df


def LatJ(egoVehData, frame_rate):
    """
    Lateral jerk (LatJ)

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe created by pd.read_csv()

    Returns:
        metric_df (df): a dataframe including frames and LatJ ['frame', 'xJerk']   
    ----------
    """
    egoVehDataCopy = egoVehData.copy()

    # time step
    tStep = 1/frame_rate

    # calculate the difference in acceleration
    egoVehDataCopy['yJerk'] = egoVehDataCopy['yAcceleration'].diff()/tStep  # assuming time step is 1

    metric_df = pd.DataFrame({
        'frame': egoVehDataCopy['frame'],
        'yJerk': egoVehDataCopy['yJerk']
    })

    return metric_df