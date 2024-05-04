"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at 
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from numpy.polynomial.polynomial import Polynomial
from scipy.signal import find_peaks
import time
import streamlit as st

def classify_vehicle_maneuver(velocities, accel_rate_threshold):
    """
    Classify vehicle maneuvers based on velocity differences.

    Parameters:
    -----------
    Inputs:
    velocities (list): A list of velocities for different frames.
    accel_rate_threshold (float): threshold to judge vehicles' state (acceleration, deceleration, or keep velocity)

    Returns:
    list: A list of maneuvers classified as 'Acceleration', 'Deceleration', or 'Keep Velocity'.
    ----------
    """
    
    maneuvers = []  # List to hold the maneuver classifications

    # Iterate through the array of velocities
    for i in range(1, len(velocities)):
        # Calculate the difference in velocity from the previous frame to the current frame
        velocity_difference = velocities[i] - velocities[i - 1]

        # Classify the maneuver based on the velocity difference
        if velocity_difference > accel_rate_threshold:
            maneuvers.append('Acceleration')
        elif velocity_difference < -1*accel_rate_threshold:
            maneuvers.append('Deceleration')
        else:
            maneuvers.append('Keep Velocity')
    
    return maneuvers


def merge_consecutive_maneuvers(maneuvers):
    """
    Merge consecutive maneuvers that are the same.

    Parameters:
    ----------
    Inputs:
        maneuvers (list): A list of maneuvers classified as 'Acceleration', 'Deceleration', or 'Keep Velocity'.

    Returns:
        list: A list of maneuvers with consecutive duplicates merged.
    ----------
    """
    
    # List to hold the merged maneuvers
    merged_maneuvers = []

    # Iterate through the maneuvers list
    for maneuver in maneuvers:
        # If the merged list is empty or the current maneuver is different from the last, add the maneuver
        if not merged_maneuvers or maneuver != merged_maneuvers[-1]:
            merged_maneuvers.append(maneuver)
    
    return merged_maneuvers


def longitudinal_activity_calc(vehicle_data):
    """
    Calculate vehicle longitudinal activity [keep velocity; acceleration; deceleration]

    Parameters:
    ----------
    Inputs:
        vehicle_data (df): a dataframe contains the drive information of one vehicle

    Returns:
        longActRes_merge (df): a dataframe contains [frame, id, LongitudinalActivity, laneId, x, y]
    ---------

    Examples:
    ----------
    Consider the following returned dataframe `longActRes_merge`:

        frame  | id | LongitudinalActivity | laneId | x | y 

           1   |  2 | Acceleration         |    2   | 162.75 | 9.39

    This indicates that from the 1st frame until the end, the vehicle accelerates;
    ----------
    """
    # Threshold of acceleration rate for [acceleration maneuver]
    # Reference: Bokare, P. S., & Maurya, A. K. (2017). Acceleration-deceleration behaviour of 
    # various vehicle types. Transportation research procedia, 25, 4733-4749.
    accel_rate_threshold = 0.5

    def categorize_maneuver(row):
        if row['xAcceleration'] > accel_rate_threshold:
            return 'acceleration'
        elif row['xAcceleration'] < -accel_rate_threshold:
            return 'deceleration'
        else:
            return 'keep velocity'

    # Apply the function to the DataFrame
    vehicle_data_copy = vehicle_data.copy()
    vehicle_data_copy['LongitudinalActivity'] = vehicle_data_copy.apply(categorize_maneuver, axis=1)
    vehicle_data_merge = vehicle_data_copy[vehicle_data_copy['LongitudinalActivity'] != vehicle_data_copy['LongitudinalActivity'].shift()]
    longActRes_merge = vehicle_data_merge[['frame', 'id', 'LongitudinalActivity', 'laneId', 'x', 'y']]
    end_row = {'frame': vehicle_data_copy['frame'].values[-1],
               'id': vehicle_data_copy['id'].values[-1],
               'LongitudinalActivity': 'finished',
               'laneId': vehicle_data_copy['laneId'].values[-1],
               'x': vehicle_data_copy['x'].values[-1],
               'y': vehicle_data_copy['y'].values[-1]}
    longActRes_merge = longActRes_merge.append(end_row, ignore_index=True)

    return longActRes_merge


def lane_yPos_calc(tracks):
    """
    Calculate the y coordinate of the given lane based on the position of following lane cars

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe containing vehicle trajectory, which can be load by pd.read_csv()

    Returns:
        refYPosLaneMean (dict): a dictionary contains the meaning YPos of corresponding lane
    ----------
    """
    unique_ids = tracks['id'].unique()
    unique_laneIds = tracks['laneId'].unique().tolist()
    refYPosLane = {key: [] for key in unique_laneIds}
    refYPosLaneMean = {key: None for key in unique_laneIds}

    for unique_id in unique_ids:
        vehicle_id = unique_id
        vehicle_data = tracks[tracks['id'] == vehicle_id]

        # If current vehicle follows lane, calculate meaning YPos
        pass_laneIds = vehicle_data['laneId'].unique()
        if len(pass_laneIds) == 1:
            curr_mean_y = np.mean(vehicle_data['y'])
            refYPosLane[pass_laneIds[0]].append(curr_mean_y)
    
    # Calculate meaning YPos for each lane
    for key in refYPosLane:
        refYPosLaneMean[key] = np.mean(refYPosLane[key]) if refYPosLane[key] else None

    return refYPosLaneMean


def lateral_activtity_frame_calc(copied_veh_data, refYPosLaneMean, laneChangeFrame):
    """
    Calculate the begin frame and end frame of the lateral activity

    Parameters:
    ----------
    Inputs:
        copied_veh_data (df): a dataframe containing vehicle information (intermediate variable of function "lateral_activtity_calc")
        refYPosLaneMean (dict): a dictionary contains the meaning YPos of corresponding lane [id:YPos] (output of function "lane_yPos_calc")
        laneChangeFrame (int): frame number where the lane change happened
        
    Returns:
        closest_frame_before_n (int): begin frame of the lane change
        closest_frame_after_n (int): end frame of the lane change
    ----------
    """
    # 1. laneIds that ego went through; 2. reference YPos of following lane activity in the lane; 3. frame number where the lane change happens
    laneIds_through = copied_veh_data['laneId'].unique()
    refYPosLane1 = refYPosLaneMean[laneIds_through[0]]
    refYPosLane2 = refYPosLaneMean[laneIds_through[1]]
    n = laneChangeFrame

    # Initialize variables to store the closest frame numbers
    closest_frame_before_n = None
    closest_frame_after_n = None

    # Iterate over the DataFrame in reverse order for frames before 'n'
    for index, row in copied_veh_data[copied_veh_data['frame'] < n][::-1].iterrows():
        if closest_frame_before_n is None or abs(row['y'] - refYPosLane1) < abs(copied_veh_data[copied_veh_data['frame'] == closest_frame_before_n].iloc[0]['y'] - refYPosLane1):
            closest_frame_before_n = row['frame']

    # Iterate over the DataFrame in regular order for frames after 'n'
    for index, row in copied_veh_data[copied_veh_data['frame'] > n].iterrows():
        if closest_frame_after_n is None or abs(row['y'] - refYPosLane2) < abs(copied_veh_data[copied_veh_data['frame'] == closest_frame_after_n].iloc[0]['y'] - refYPosLane2):
            closest_frame_after_n = row['frame']

    # Assign the begin or end frame of scenario in case lane change happens at begining and end e.g., id=169; 07_tracks
    if closest_frame_before_n is not None and closest_frame_after_n is not None:
        return closest_frame_before_n, closest_frame_after_n
    elif closest_frame_before_n is None and closest_frame_after_n is not None:
        closest_frame_before_n = copied_veh_data['frame'].values[0]
        return closest_frame_before_n, closest_frame_after_n
    elif closest_frame_before_n is not None and closest_frame_after_n is None:
        closest_frame_after_n = copied_veh_data['frame'].values[-1]
        return closest_frame_before_n, closest_frame_after_n
    elif closest_frame_before_n is None and closest_frame_after_n is None:
        closest_frame_before_n = copied_veh_data['frame'].values[0]
        closest_frame_after_n = copied_veh_data['frame'].values[-1]
        return closest_frame_before_n, closest_frame_after_n


def lateral_activtity_calc(vehicle_data, refYPosLaneMean):
    """
    Calculate vehicle lateral activity [follow lane; lane change to the left; lane change to the right]

    Parameters:
    ----------
    Inputs:
        vehicle_data (df): a dataframe contains the drive information of one vehicle
        refYPosLaneMean (dict): a dictionary contains the meaning YPos of corresponding lane

    Returns:
        latActRes (df): a dataframe contains [frame, id, LateralActivity, laneId, x, y]
    ----------

    Examples:
    ----------

        frame  |  LateralActivity  

        1      |  follow lane       

        40     |  lane change left

        100    |  follow lane

    This indicates that vehicle changes the lane to left on 40th frame; and follows the lane for the rest of the frames

    ----------
    """
    # Calculate lane id changes during the whole scenario
    copied_veh_data = vehicle_data.copy()
    copied_veh_data['laneChange'] = copied_veh_data['laneId'].diff()

    # Calculate drive direction
    veh_drive_direction = copied_veh_data['x'].iloc[-1] - copied_veh_data['x'].iloc[0]
    
    # Calculate lateral activities of vehicles
    def lane_change_calc(row):
        if (row['laneChange'] > 0 and veh_drive_direction > 0) or (row['laneChange'] < 0 and veh_drive_direction < 0):
            return 'lane change right'
        elif (row['laneChange'] < 0 and veh_drive_direction > 0) or (row['laneChange'] > 0 and veh_drive_direction < 0):
            return 'lane change left'
        else:
            return 'follow lane'
    copied_veh_data['LateralActivity'] = copied_veh_data.apply(lane_change_calc, axis=1)

    # Find frames with lane change
    lane_change_frames = copied_veh_data[(copied_veh_data['LateralActivity'] == 'lane change left') | (copied_veh_data['LateralActivity'] == 'lane change right')]
    # If there are no lane change maneuvers, take the first frame of the vehicle
    if lane_change_frames.empty:
        vehicle_info = copied_veh_data.iloc[0:1]
        latActRes = vehicle_info[['frame', 'id', 'LateralActivity', 'laneId', 'x', 'y']]
        end_row = {
            'frame': copied_veh_data['frame'].values[-1],
            'id': copied_veh_data['id'].values[-1],
            'LateralActivity': 'finished',
            'laneId': copied_veh_data['laneId'].values[-1],
            'x': copied_veh_data['x'].values[-1],
            'y': copied_veh_data['y'].values[-1]
        }
        latActRes = latActRes.append(end_row, ignore_index=True)
        return latActRes
    else:
        # Calculate the begin frame and end frame of the lane change activity
        laneChangeBegFrame, laneChangeEndFrame = lateral_activtity_frame_calc(copied_veh_data, refYPosLaneMean, lane_change_frames['frame'].values[0])
        laneChangeBegIndex = laneChangeBegFrame - copied_veh_data['frame'].values[0]
        laneChangeEndIndex = laneChangeEndFrame - copied_veh_data['frame'].values[0]
        latActRes = {
            'frame': [copied_veh_data['frame'].values[0], laneChangeBegFrame, laneChangeEndFrame, copied_veh_data['frame'].values[-1]],
            'id': [copied_veh_data['id'].values[0], copied_veh_data['id'].values[1], copied_veh_data['id'].values[2], copied_veh_data['id'].values[-1]],
            'LateralActivity': [copied_veh_data['LateralActivity'].values[0], lane_change_frames['LateralActivity'].values[0], copied_veh_data['LateralActivity'].values[laneChangeEndIndex], 'finished'],
            'laneId': [copied_veh_data['laneId'].values[0], copied_veh_data['laneId'].values[laneChangeBegIndex], copied_veh_data['laneId'].values[laneChangeEndIndex], copied_veh_data['laneId'].values[-1]],
            'x': [copied_veh_data['x'].values[0], copied_veh_data['x'].values[laneChangeBegIndex], copied_veh_data['x'].values[laneChangeEndIndex], copied_veh_data['x'].values[-1]],
            'y': [copied_veh_data['y'].values[0], copied_veh_data['y'].values[laneChangeBegIndex], copied_veh_data['y'].values[laneChangeEndIndex], copied_veh_data['y'].values[-1]]
        }
        latActRes = pd.DataFrame(latActRes)
        return latActRes


def main_fcn_veh_activity(tracks, progress_bar):
    """
    Main functions to get all desired vehicle activity [keep velocity; acceleration; deceleration]

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe containing vehicle trajectory, which can be load by pd.read_csv()

    Returns:
        longActDict (dict): a dictionary containing longitudinal activites id: df['frame', 'id', 'LongitudinalActivity', 'x', 'y']
        latActDict (dict): a dictionary containing lateral activites id: df['frame', 'id', 'LateralActivity', 'x', 'y']
        interactIdDict (dict): a dictionary containing fictive ego vehicles and correspondong target vehicles id: df[id1, id2, id3,...]
    ---------
    """
    # Initialize dictionaries to store results
    longActDict = dict()
    latActDict = dict()
    interactIdDict = dict()

    # Extract desired activities; calculate YPos reference if "lane change" is desired
    refYPosLaneMean = lane_yPos_calc(tracks)

    start_time = time.time()
    unique_ids = tracks['id'].unique()
    index = 0
    for unique_id in unique_ids:
        # Update progress bar
        progress = int((index + 1) / len(unique_ids) * 100)
        progress_bar.progress(progress)

        # Current vehicle
        vehicle_id = unique_id
        vehicle_data = tracks[tracks['id'] == vehicle_id]

        # Longitudinal activity calculation
        longActRes = longitudinal_activity_calc(vehicle_data)

        # Lateral activity calculation
        latActRes = lateral_activtity_calc(vehicle_data, refYPosLaneMean)
        
        # If meet both lateral and longitudinal activities
        longActDict[vehicle_id] = longActRes
        latActDict[vehicle_id] = latActRes

        interaction_columns = [
            "precedingId", "followingId", "leftPrecedingId", "leftAlongsideId", 
            "leftFollowingId", "rightPrecedingId", "rightAlongsideId", "rightFollowingId"
        ]
        interaction_vehicles = []
        for column in interaction_columns:
            interaction_ids = vehicle_data[column].unique()
            for i in interaction_ids:
                if i != 0 and i not in interaction_vehicles:
                    interaction_vehicles.append(i)
        interactIdDict[vehicle_id] = interaction_vehicles

        # Update index
        index += 1

    # Complete the progress
    progress_bar.progress(100)
    end_time = time.time()
    print(f'It takes {end_time-start_time} seconds!')
    return longActDict, latActDict, interactIdDict

def get_vehicle_activity_at_junctions(tracks, progress_bar, junctions_data):
    """
    Get vehicle activity at junctions.

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe containing vehicle trajectory, which can be loaded by pd.read_csv()
        progress_bar (object): progress bar object to display progress
        junctions_data (list): a list containing junctions data, each item in the list represents a junction

    Returns:
    ----------
    Returns:
        junctions_activity_dict (dict): a dictionary containing vehicle junctions activity id: df['frame', 'id', 'JunctionsActivity', 'x', 'y']
    """
    # Initialize dictionary to store results
    junctions_activity_dict = dict()

    # Extract desired activities
    start_time = time.time()
    unique_ids = tracks['id'].unique()
    index = 0
    for unique_id in unique_ids:
        # Update progress bar
        progress = int((index + 1) / len(unique_ids) * 100)
        progress_bar.progress(progress)

        # Current vehicle
        vehicle_id = unique_id
        vehicle_data = tracks[tracks['id'] == vehicle_id]

        # Initialize junction activity
        junction_activity = None

        # Check if vehicle passes through any junction
        for junction_data in junctions_data:
            junction_id = junction_data['id']
            junction_polygon = junction_data['polygon']
            # Check if any point of the vehicle trajectory is within the junction polygon
            for _, frame_data in vehicle_data.iterrows():
                x = frame_data['x']
                y = frame_data['y']
                point_within_polygon = junction_polygon.contains(Point(x, y))
                if point_within_polygon:
                    junction_activity = junction_id
                    break
            if junction_activity:
                break

        # If vehicle passes through a junction, set junction activity
        if junction_activity:
            vehicle_data['JunctionsActivity'] = junction_activity
            junctions_activity_dict[vehicle_id] = vehicle_data[['frame', 'id', 'JunctionsActivity', 'x', 'y']]
        # If vehicle doesn't pass through any junction, set activity as None
        else:
            junctions_activity_dict[vehicle_id] = vehicle_data[['frame', 'id', 'JunctionsActivity', 'x', 'y']]

        # Update index
        index += 1

    # Complete the progress
    progress_bar.progress(100)
    end_time = time.time()
    print(f'It takes {end_time-start_time} seconds!')
    return junctions_activity_dict
