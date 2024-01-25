"""
Author: Yongqi Zhao
Date Created: 2023-11-28
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
Reference: https://criticality-metrics.readthedocs.io/en/latest/
"""
import math

def CS():
    """
    Conflict Severity (CS)

    Parameters:
    ----------
    Inputs:

    Returns:
        
    ----------
    weights for ego and target vehicles are not available
    """
    pass


def delta_v(tracks, delta_v_threshold, framerate):
    """
    Delta-v

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe created by pd.read_csv()
        delta_v_threshold (list): boundary of ET
        framerate (Hz): frame rate of the dataset

    Returns:
        ego_ids (list): a list contains ego id that can meet the requirements
    ----------
    Only consider a single vehicle
    """
    ego_ids = []

    # filter rows where "frame" is 1 or a multiple of 30
    tracks_sample = tracks[tracks['frame'] % framerate == 0].copy()

    # collision search
    collision = tracks_sample[(tracks_sample['precedingId'] != 0) & (tracks_sample['ttc'] == 0)]

    # calculate delta_v
    if not collision.empty:
        print("coming soon, as long as determin the way to find collision scenarios")

    

