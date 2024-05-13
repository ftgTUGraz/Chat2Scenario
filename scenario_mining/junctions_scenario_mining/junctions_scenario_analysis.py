import streamlit as st
import pandas as pd
from GUI.Web_Sidebar import *
from utils.helper_original_scenario import generate_xosc
import time
from GUI.Web_MainContent import *
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from utils.prompt_engineering import *
from NLP.Scenario_Description_Understand import *
from scenario_mining.activity_identification import *
from scenario_mining.scenario_identification import *
import scenario_mining.junctions_scenario_mining.bendplatz_01 as bendplatz
import scenario_mining.junctions_scenario_mining.frankenburg_02 as frankenburg
import scenario_mining.junctions_scenario_mining.heckstrasse_03 as heckstrasse
import scenario_mining.junctions_scenario_mining.aseag_04 as aseag
import xml.etree.ElementTree as ET
import math
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # Or 'Qt5Agg', 'GTK3Agg', 'WXAgg', etc., depending on your system configuration
import matplotlib.pyplot as plt


def select_opendrive_map(file_path):
    """
    Selects and processes the OpenDRIVE map file based on its numeric index, updating tracks with lane information and activity types.

    Parameters:
    ----------
    file_path (str): The file path that contains the numeric index which dictates the processing logic.

    Returns:
    ----------
    DataFrame: A pandas DataFrame that includes updated track information with road and lane details along with activity types.
    """
    # Extracting numbers from the file name
    match = re.search(r'\d+', file_path)
    if match:
        index = int(match.group(0))
        # Choosing the corresponding map file and processing logic based on different number ranges
        if 0 <= index <= 6:
            # Adding road and lane information
            tracks_meta_df = aseag.update_tracks_with_lane_info(file_path)
            # Adding activity types (e.g., right, left, straight)
            tracks_meta_df = aseag.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df
        
        elif 7 <= index <= 17:

            tracks_meta_df = bendplatz.update_tracks_with_lane_info(file_path)
            tracks_meta_df = bendplatz.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df

        elif 18 <= index <= 29:

            tracks_meta_df = frankenburg.update_tracks_with_lane_info(file_path)
            tracks_meta_df = frankenburg.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df

        elif 30 <= index <= 32:

            tracks_meta_df = heckstrasse.update_tracks_with_lane_info(file_path)
            tracks_meta_df = heckstrasse.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df
    else:
        # Default processing logic if no valid index found or out of range
        print("No valid index found, or out of range. No operation performed.")


def get_turn_types_from_response(response):
    """
    Extract turn types from a given response dictionary.

    Parameters:
    -----------
    Inputs:
        response (dict): A dictionary containing turn types for vehicles.

    Returns:
        ego_turn_type (str): Turn type of the ego vehicle.
        target_turn_type (str): Turn type of the target vehicle.
    ----------
    """
    # Extract turn type for the ego vehicle
    ego_turn_type = response['Ego Vehicle']['turn_type']

    # Extract turn type for the target vehicle
    target_turn_type = response['Target Vehicle']['turn_type']

    return ego_turn_type, target_turn_type



def identify_junction_scenarios(tracks_df, key_label):
    """
    Identifies junction scenarios based on provided DataFrame of track data including road, lane, and turn type information.

    Parameters:
    ----------
    tracks_df (DataFrame): DataFrame containing track data with columns for 'road_lane' and 'turn_type'.
    key_label (dict): Dictionary containing turn type information for both ego and target vehicles.

    Returns:
    ----------
    list: A list of identified scenarios including scenario details such as track IDs and frame ranges.
    """
    ego_turn, target_turn = get_turn_types_from_response(key_label)
    scenario_lists = []

    # Calculating the life cycle range for each trackId
    life_cycles = tracks_df.groupby('trackId').agg(start_frame=('frame', 'min'), end_frame=('frame', 'max')).reset_index()

    # Extracting road ID
    tracks_df['road_id'] = tracks_df['road_lane'].apply(lambda x: int(str(x).split('.')[0]))

    # Filtering rows that match the ego turn type
    ego_tracks = tracks_df[tracks_df['turn_type'] == ego_turn].merge(life_cycles, on='trackId')
    target_tracks = tracks_df[tracks_df['turn_type'] == target_turn].merge(life_cycles, on='trackId')
    # Cache for processed scenarios to improve efficiency
    processed_scenarios = set()

    # Iterating through each ego track row
    for _, ego_row in ego_tracks.iterrows():
        ego_id = ego_row['trackId']
        ego_life = [ego_row['start_frame'], ego_row['end_frame']]
        ego_road_id = ego_row['road_id']

        # Iterating through each target track row
        for _, target_row in target_tracks.iterrows():
            target_id = target_row['trackId']
            if target_id == ego_id:
                continue  # Skip if ego and target vehicle are the same

            # Check if they are on the same road at the last frame of the intersection
            if (ego_id, target_id) in processed_scenarios:
                continue

            target_life = [target_row['start_frame'], target_row['end_frame']]
            target_road_id = target_row['road_id']

            # 使用intersection_judge判断生命周期交集
            inter = intersection_judge(ego_life, target_life)
            if inter:
                # 在交集的最后一帧检查是否在同一条道路上
                last_frame = inter[1]
                ego_last_road_id = tracks_df[(tracks_df['trackId'] == ego_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]
                target_last_road_id = tracks_df[(tracks_df['trackId'] == target_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]
                
                if ego_last_road_id == target_last_road_id:
                    new_scenario = [
                        ego_id, 
                        [target_id], 
                        inter[0], 
                        inter[1]
                    ]
                    # Ensure not to add the same scenario twice
                    if new_scenario not in scenario_lists:
                        scenario_lists.append(new_scenario)
                        processed_scenarios.add((ego_id, target_id))
                    
    return scenario_lists

def identify_junction_scenarios_optimized(tracks_df, key_label):
    """
    Optimized function to identify junction scenarios based on road, lane, and turn type data, avoiding redundant calculations.

    Parameters:
    ----------
    tracks_df (DataFrame): DataFrame containing track data including road_lane and turn_type information.
    key_label (dict): Dictionary with turn type details for ego and target vehicles.

    Returns:
    ----------
    list: A list of scenarios with detailed information, optimized to avoid redundant processing.
    """
    ego_turn, target_turn = get_turn_types_from_response(key_label)

    # Optimization: First extract life cycle, road_id, and turn_type for each trackId
    tracks_df['road_id'] = tracks_df['road_lane'].apply(lambda x: int(str(x).split('.')[0]))
    life_cycles = tracks_df.groupby('trackId').agg(
        start_frame=('frame', 'min'),
        end_frame=('frame', 'max'),
        road_id=('road_id', 'first'),  # Assuming road_id remains constant throughout the track
        turn_type=('turn_type', 'first')  # Adding handling for turn_type
    ).reset_index()

    # Filter out data that matches ego and target turn types
    ego_tracks = life_cycles[life_cycles['turn_type'] == ego_turn]
    target_tracks = life_cycles[life_cycles['turn_type'] == target_turn]

    scenarios = {}
    processed_scenarios = set()  # Cache for processed scenarios to improve efficiency

    # Iterating through each ego track
    for _, ego_row in ego_tracks.iterrows():
        ego_id = ego_row['trackId']
        ego_life = [ego_row['start_frame'], ego_row['end_frame']]
        ego_road_id = ego_row['road_id']

        # Iterating through each target track
        for _, target_row in target_tracks.iterrows():
            target_id = target_row['trackId']
            if target_id == ego_id:
                continue  # Skip if ego and target vehicle are the same

            target_life = [target_row['start_frame'], target_row['end_frame']]
            target_road_id = target_row['road_id']

            # Checking life cycle intersection
            inter = intersection_judge(ego_life, target_life)
            if inter:
                # Getting road IDs at the start and end frames of the intersection
                ego_start_road_id = tracks_df[(tracks_df['trackId'] == ego_id) & (tracks_df['frame'] == ego_row['start_frame'])]['road_id'].iloc[0]
                target_start_road_id = tracks_df[(tracks_df['trackId'] == target_id) & (tracks_df['frame'] == target_row['start_frame'])]['road_id'].iloc[0]

                last_frame = inter[1]
                ego_last_road_id = tracks_df[(tracks_df['trackId'] == ego_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]
                target_last_road_id = tracks_df[(tracks_df['trackId'] == target_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]
                
                if ego_last_road_id == target_last_road_id and target_start_road_id != target_last_road_id and ego_start_road_id != ego_last_road_id:
                    '''
                    new_scenario = [
                        ego_id, 
                        [target_id], 
                        inter[0], 
                        inter[1]
                    ]
                    
                    
                    # Make sure you don't add the same scene repeatedly
                    if new_scenario not in scenarios:
                        scenarios.append(new_scenario)
                        processed_scenarios.add((ego_id, target_id))
                    '''

                    if ego_id not in scenarios:
                        scenarios[ego_id] = {'targets': [target_id], 'start_frame': inter[0], 'end_frame': inter[1]}
                    else:
                        # If scenario already exists, only add new target_id if it's not already recorded
                        if target_id not in scenarios[ego_id]['targets']:
                            scenarios[ego_id]['targets'].append(target_id)
                            # Update start and end frames to include the longest interaction period
                            scenarios[ego_id]['start_frame'] = min(scenarios[ego_id]['start_frame'], inter[0])
                            scenarios[ego_id]['end_frame'] = max(scenarios[ego_id]['end_frame'], inter[1])

    # Convert dictionary to list format to match the original output structure
    scenarios = [[key, value['targets'], value['start_frame'], value['end_frame']] for key, value in scenarios.items()]
 
                    
    return scenarios