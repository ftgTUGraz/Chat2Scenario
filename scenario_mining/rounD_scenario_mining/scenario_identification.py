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
from scenario_mining.rounD_scenario_mining.playground import Playground
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
import re
from map_data.RounD_map_data.RounD_data import (
    lanes_polygons, lanes_polygons1, lanes_polygons2_23
)

class OpenDriveMapSelector_RounD:
    def __init__(self,file_path,tracks_original):
        self.file_path = file_path
        self.tracks_original = tracks_original
        self.tracks_meta_df = self.select_opendrive_map()
    def select_opendrive_map(self):
        """
        Selects and processes the OpenDRIVE map file based on its numeric index, updating tracks with lane information and activity types.

        Returns:
        ----------
        DataFrame: A pandas DataFrame that includes updated track information with road and lane details along with activity types.
        """
        match = re.search(r'\d+', self.file_path.name)
        #match = re.search(r'\d+', './01_tracks.csv')
        
        if match:
            index = int(match.group(0))
            if 0 <= index <= 23:
                playground = Playground(index)
                tracks_meta_df = playground.update_track_file(self.file_path)
                print(tracks_meta_df)
                polygons_list = [polygon for polygons in playground.lane_polygons.values() for polygon in polygons]
                return polygons_list, tracks_meta_df
            else:
                print("No valid index found, or out of range. Unexecuted operation")
            r'''
            if  index == 0:
                tracks_meta_df = playground0.Playground0().update_track_file(self.file_path)
                print(tracks_meta_df)
                return lanes_polygons,tracks_meta_df
            elif  index == 1:
                tracks_meta_df = playground1.Playground1().update_track_file(self.file_path)
                print(tracks_meta_df)
                return lanes_polygons1,tracks_meta_df
            elif 2 <= index <= 23:
                tracks_meta_df = playground2_23.Playground2_23().update_track_file(self.file_path)
                print(tracks_meta_df)
                return lanes_polygons2_23,tracks_meta_df
            '''
        else:
            print("No valid index found in file name. No operation was performed.")

    @staticmethod
    def get_turn_types_from_response(response):
        """
        Extract turn types from a given response dictionary.

        Parameters:
        -----------
        response (dict): A dictionary containing turn types for vehicles.

        Returns:
        ego_roundabout_activity (str): Turn type of the ego vehicle.
        target_roundabout_activity (str): Turn type of the target vehicle.
        """
        ego_roundabout_activity = response['Ego Vehicle']['roundabout_activity']
        target_roundabout_activity = response['Target Vehicle']['roundabout_activity']
        return ego_roundabout_activity, target_roundabout_activity

    @staticmethod
    def identify_junction_scenarios(tracks_df, key_label):
        """
        Identifies junction scenarios based on provided DataFrame of track data including road, lane, and turn type information.

        Parameters:
        ----------
        tracks_df (DataFrame): DataFrame containing track data with columns for 'laneId' and 'roundabout_activity'.
        key_label (dict): Dictionary containing turn type information for both ego and target vehicles.

        Returns:
        ----------
        list: A list of identified scenarios including scenario details such as track IDs and frame ranges.
        """
        ego_turn, target_turn = OpenDriveMapSelector_RounD.get_turn_types_from_response(key_label)
        scenario_lists = []

        life_cycles = tracks_df.groupby('trackId').agg(start_frame=('frame', 'min'), end_frame=('frame', 'max')).reset_index()
        tracks_df['road_id'] = tracks_df['laneId'].apply(lambda x: int(str(x).split('.')[0]))
        ego_tracks = tracks_df[tracks_df['roundabout_activity'] == ego_turn].merge(life_cycles, on='trackId')
        target_tracks = tracks_df[tracks_df['roundabout_activity'] == target_turn].merge(life_cycles, on='trackId')
        processed_scenarios = set()

        for _, ego_row in ego_tracks.iterrows():
            ego_id = ego_row['trackId']
            ego_life = [ego_row['start_frame'], ego_row['end_frame']]
            ego_road_id = ego_row['road_id']

            for _, target_row in target_tracks.iterrows():
                target_id = target_row['trackId']
                if target_id == ego_id:
                    continue

                if (ego_id, target_id) in processed_scenarios:
                    continue

                target_life = [target_row['start_frame'], target_row['end_frame']]
                target_road_id = target_row['road_id']

                inter = intersection_judge(ego_life, target_life)
                if inter:
                    last_frame = inter[1]
                    ego_last_road_id = tracks_df[(tracks_df['trackId'] == ego_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]
                    target_last_road_id = tracks_df[(tracks_df['trackId'] == target_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]

                    if ego_last_road_id == target_last_road_id:
                        new_scenario = [ego_id, [target_id], inter[0], inter[1]]
                        if new_scenario not in scenario_lists:
                            scenario_lists.append(new_scenario)
                            processed_scenarios.add((ego_id, target_id))

        return scenario_lists
    

    @staticmethod
    def original_identify_junction_scenarios_optimized(tracks_df, key_label):
        """
        Optimized function to identify junction scenarios based on road, lane, and turn type data, avoiding redundant calculations.

        Parameters:
        ----------
        tracks_df (DataFrame): DataFrame containing track data including laneId and activity_type information.
        key_label (dict): Dictionary with turn type details for ego and target vehicles.

        Returns:
        ----------
        list: A list of scenarios with detailed information, optimized to avoid redundant processing.
        """
        ego_turn, target_turn = OpenDriveMapSelector_RounD.get_turn_types_from_response(key_label)
        tracks_df['road_id'] = tracks_df['laneId'].apply(lambda x: int(str(x).split('.')[0]) if pd.notnull(x) else None)
        tracks_df['frame'] = pd.to_numeric(tracks_df['frame'], errors='coerce')
        # Modify to capture all road_id and activity_type as lists
        life_cycles = tracks_df.groupby('trackId').agg(
            start_frame=('frame', 'min'),
            end_frame=('frame', 'max'),
            road_ids=('road_id', list),          # Capture all road_ids as a list
            activity_types=('activity_type', list)  # Capture all activity_types as a list
        ).reset_index()

        scenarios = {}

        if ego_turn == 'enter' and target_turn == 'inside':
            ego_last_enter_frame = None  
            target_tracks_at_frame = None 

            for ego_id in tracks_df['trackId'].unique():
                ego_tracks = tracks_df[tracks_df['trackId'] == ego_id]
                ego_enter_tracks = ego_tracks[ego_tracks['activity_type'] == 'enter']
                if ego_enter_tracks.empty:
                    continue  # Ego vehicle doesn't have 'enter' activity
                # Get the last frame where 'activity_type' == 'enter' for ego vehicle
                ego_last_enter_frame = ego_enter_tracks['frame'].max()

                # Get ego vehicle's maximum frame
                ego_max_frame = ego_tracks['frame'].max()

                # At that frame, check all target vehicles
                for target_id in tracks_df['trackId'].unique():
                    if target_id == ego_id:
                        continue
                    target_tracks_at_frame = tracks_df[
                        (tracks_df['trackId'] == target_id) & (tracks_df['frame'] == ego_last_enter_frame)
                    ]
                    target_tracks = tracks_df[
                        (tracks_df['trackId'] == target_id)
                    ]
                    target_tracks_for_inter = target_tracks

                    target_min_frame = target_tracks_for_inter['frame'].min()
                    target_max_frame = target_tracks_for_inter['frame'].max()   

                    target_tracks_at_frame = target_tracks[
                        target_tracks['frame'] == ego_last_enter_frame
                    ]          

                    if not target_tracks_at_frame.empty:
                        target_activity_type = target_tracks_at_frame['activity_type'].iloc[0]
                        if target_activity_type == 'inside':
                            # Compute intersection
                            inter = intersection_judge(
                                [ego_last_enter_frame, ego_max_frame],
                                [target_min_frame, target_max_frame]
                            )
                            if inter:
                                # Found a scenario
                                if ego_id not in scenarios:
                                    scenarios[ego_id] = {
                                        'targets': [target_id],
                                        'start_frame': inter[0],
                                        'end_frame': inter[1]
                                    }
                                else:
                                    if target_id not in scenarios[ego_id]['targets']:
                                        scenarios[ego_id]['targets'].append(target_id)
                                        # Update start_frame and end_frame
                                        scenarios[ego_id]['start_frame'] = min(scenarios[ego_id]['start_frame'], inter[0])
                                        scenarios[ego_id]['end_frame'] = max(scenarios[ego_id]['end_frame'], inter[1])
            scenarios_list = [
                [int(key), list(map(int, value['targets'])), value['start_frame'], value['end_frame']]
                for key, value in scenarios.items()
            ]
            return scenarios_list
       
        elif ego_turn == 'exit' and target_turn in ['inside', 'exit', 'inside_or_exit']:
            for ego_id in tracks_df['trackId'].unique():
                ego_tracks = tracks_df[tracks_df['trackId'] == ego_id]
                ego_exit_tracks = ego_tracks[ego_tracks['activity_type'] == 'exit']
                if ego_exit_tracks.empty:
                    continue  # Ego vehicle doesn't have 'exit' activity
                # Get the first frame where 'activity_type' == 'exit' for ego vehicle
                ego_first_exit_frame = ego_exit_tracks['frame'].min()
                ego_tracks_from_exit = ego_tracks[ego_tracks['frame'] >= ego_first_exit_frame]

                # At that frame, check all target vehicles
                for target_id in tracks_df['trackId'].unique():
                    if target_id == ego_id:
                        continue
                    target_tracks = tracks_df[tracks_df['trackId'] == target_id]
                    target_tracks_at_frame = target_tracks[
                        target_tracks['frame'] == ego_first_exit_frame
                    ]
                    if not target_tracks_at_frame.empty:
                        target_activity_type = target_tracks_at_frame['activity_type'].iloc[0]
                        if (target_turn == 'inside' and target_activity_type == 'inside') or \
                        (target_turn == 'exit' and target_activity_type == 'exit') or \
                        (target_turn == 'inside_or_exit' and target_activity_type in ['inside', 'exit']):
                            # Found a scenario
                            target_tracks_from_frame = target_tracks[target_tracks['frame'] >= ego_first_exit_frame]
                            inter = intersection_judge(
                                [ego_tracks['frame'].min(), ego_tracks['frame'].max()],
                                [target_tracks['frame'].min(), target_tracks['frame'].max()]
                            )
                            if inter:
                                if ego_id not in scenarios:
                                    scenarios[ego_id] = {
                                        'targets': [target_id],
                                        'start_frame': inter[0],
                                        'end_frame': inter[1]
                                    }
                                else:
                                    if target_id not in scenarios[ego_id]['targets']:
                                        scenarios[ego_id]['targets'].append(target_id)
                                        scenarios[ego_id]['start_frame'] = min(
                                            scenarios[ego_id]['start_frame'], inter[0]
                                        )
                                        scenarios[ego_id]['end_frame'] = max(
                                            scenarios[ego_id]['end_frame'], inter[1]
                                        )
            scenarios = [
                [int(key), list(map(int, value['targets'])), value['start_frame'], value['end_frame']]
                for key, value in scenarios.items()
            ]
            return scenarios        
        '''
        else:
            for _, ego_row in life_cycles.iterrows():
                ego_id = ego_row['trackId']
                ego_life = [ego_row['start_frame'], ego_row['end_frame']]
                ego_road_ids = ego_row['road_ids']
                ego_activity_types = ego_row['activity_types']

                if ego_turn in ego_activity_types:
                    for idx, activity in enumerate(ego_activity_types):
                        if activity == ego_turn:
                            ego_start_frame = tracks_df[
                                (tracks_df['trackId'] == ego_id) & 
                                (tracks_df['road_id'] == ego_road_ids[idx])
                            ]['frame'].min()
                            break
                    ego_tracks_df = tracks_df[
                        (tracks_df['trackId'] == ego_id) & 
                        (tracks_df['frame'] >= ego_start_frame)
                    ]

                    for _, target_row in life_cycles.iterrows():
                        target_id = target_row['trackId']
                        if target_id == ego_id:
                            continue

                        target_life = [target_row['start_frame'], target_row['end_frame']]
                        target_road_ids = target_row['road_ids']
                        target_activity_types = target_row['activity_types']

                        if target_turn in target_activity_types:
                            for idx, activity in enumerate(target_activity_types):
                                if activity == target_turn:
                                    target_start_frame = tracks_df[
                                        (tracks_df['trackId'] == target_id) & 
                                        (tracks_df['road_id'] == target_road_ids[idx])
                                    ]['frame'].min()
                                    break
                            target_tracks_df = tracks_df[
                                (tracks_df['trackId'] == target_id) & 
                                (tracks_df['frame'] >= target_start_frame)
                            ]

                            # Calculate intersection
                            inter = intersection_judge(
                                [ego_tracks_df['frame'].min(), ego_tracks_df['frame'].max()],
                                [target_tracks_df['frame'].min(), target_tracks_df['frame'].max()]
                            )

                            if inter:
                                last_frame = inter[1]
                                ego_last_road_id = ego_tracks_df[
                                    ego_tracks_df['frame'] == last_frame
                                ]['road_id'].iloc[0]
                                target_last_road_id = target_tracks_df[
                                    target_tracks_df['frame'] == last_frame
                                ]['road_id'].iloc[0]

                                if ego_last_road_id == target_last_road_id:
                                    if ego_id not in scenarios:
                                        scenarios[ego_id] = {
                                            'targets': [target_id],
                                            'start_frame': inter[0],
                                            'end_frame': inter[1]
                                        }
                                    else:
                                        if target_id not in scenarios[ego_id]['targets']:
                                            scenarios[ego_id]['targets'].append(target_id)
                                            scenarios[ego_id]['start_frame'] = min(
                                                scenarios[ego_id]['start_frame'], inter[0]
                                            )
                                            scenarios[ego_id]['end_frame'] = max(
                                                scenarios[ego_id]['end_frame'], inter[1]
                                            )

            scenarios = [
                [key, value['targets'], value['start_frame'], value['end_frame']] 
                for key, value in scenarios.items()
            ]
            return scenarios
        '''

    '''
    @staticmethod
    def identify_junction_scenarios_optimized(tracks_df, key_label):
        """
        Optimized function to identify junction scenarios based on road, lane, and turn type data.

        Parameters:
        ----------
        tracks_df (DataFrame): DataFrame containing track data including laneId and activity_type information.
        key_label (dict): Dictionary with turn type details for ego and target vehicles.

        Returns:
        ----------
        list: A list of scenarios with detailed information.
        """
        # Extract ego and target turn types from key_label
        ego_turn, target_turn = OpenDriveMapSelector_RounD.get_turn_types_from_response(key_label)

        # Filter tracks_df to keep only vehicles that contain the 'inside' activity type
        vehicles_with_inside = tracks_df[tracks_df['activity_type'] == 'inside']['trackId'].unique()
        tracks_df = tracks_df[tracks_df['trackId'].isin(vehicles_with_inside)]
        
        # Ensure 'frame' is numeric
        tracks_df['frame'] = pd.to_numeric(tracks_df['frame'], errors='coerce')
        
        # Precompute life cycles for each vehicle
        life_cycles = tracks_df.groupby('trackId').agg(
            start_frame=('frame', 'min'),
            end_frame=('frame', 'max')
        ).reset_index()
        life_cycles_dict = life_cycles.set_index('trackId').to_dict('index')

        scenarios_dict = {}

        if ego_turn == 'enter' and target_turn == 'inside':
            # Find the last 'enter' activity frame for each ego vehicle
            ego_enter_df = tracks_df[tracks_df['activity_type'] == 'enter']
            ego_enter_last_frame_df = ego_enter_df.groupby('trackId')['frame'].max().reset_index()
            ego_enter_last_frame_df.rename(columns={'trackId': 'ego_id', 'frame': 'ego_last_enter_frame'}, inplace=True)
            
            # Get all vehicles in 'inside' activity
            inside_df = tracks_df[tracks_df['activity_type'] == 'inside']
            
            # For each ego vehicle, find target vehicles at the ego's last 'enter' frame
            merged_df = ego_enter_last_frame_df.merge(
                inside_df,
                left_on='ego_last_enter_frame',
                right_on='frame',
                how='inner'
            )
            
            # Exclude cases where ego_id == target_id
            merged_df = merged_df[merged_df['ego_id'] != merged_df['trackId']]
            
            for idx, row in merged_df.iterrows():
                ego_id = row['ego_id']
                target_id = row['trackId']
                ego_last_enter_frame = row['ego_last_enter_frame']
                
                # Get life cycles
                ego_end_frame = life_cycles_dict[ego_id]['end_frame']
                target_start_frame = life_cycles_dict[target_id]['start_frame']
                target_end_frame = life_cycles_dict[target_id]['end_frame']
                
                # Compute overlapping intervals
                inter_start = max(ego_last_enter_frame, target_start_frame)
                inter_end = min(ego_end_frame, target_end_frame)
                
                if inter_start <= inter_end:
                    if ego_id not in scenarios_dict:
                        scenarios_dict[ego_id] = {
                            'targets': [target_id],
                            'start_frame': inter_start,
                            'end_frame': inter_end
                        }
                    else:
                        if target_id not in scenarios_dict[ego_id]['targets']:
                            scenarios_dict[ego_id]['targets'].append(target_id)
                            scenarios_dict[ego_id]['start_frame'] = min(
                                scenarios_dict[ego_id]['start_frame'], inter_start
                            )
                            scenarios_dict[ego_id]['end_frame'] = max(
                                scenarios_dict[ego_id]['end_frame'], inter_end
                            )
            
            # Convert scenarios_dict to list format
            scenarios_list = [
                [int(ego_id), list(map(int, value['targets'])), int(value['start_frame']), int(value['end_frame'])]
                for ego_id, value in scenarios_dict.items()
            ]
            return scenarios_list

        elif ego_turn == 'exit' and target_turn in ['inside', 'exit', 'inside_or_exit']:
            # Find the first 'exit' activity frame for each ego vehicle
            ego_exit_df = tracks_df[tracks_df['activity_type'] == 'exit']
            ego_exit_first_frame_df = ego_exit_df.groupby('trackId')['frame'].min().reset_index()
            ego_exit_first_frame_df.rename(columns={'trackId': 'ego_id', 'frame': 'ego_first_exit_frame'}, inplace=True)
            
            # Depending on target_turn, get appropriate target vehicles
            if target_turn == 'inside':
                target_df = tracks_df[tracks_df['activity_type'] == 'inside']
            elif target_turn == 'exit':
                target_df = tracks_df[tracks_df['activity_type'] == 'exit']
            elif target_turn == 'inside_or_exit':
                target_df = tracks_df[tracks_df['activity_type'].isin(['inside', 'exit'])]
            
            # For each ego vehicle, find target vehicles at the ego's first 'exit' frame
            merged_df = ego_exit_first_frame_df.merge(
                target_df,
                left_on='ego_first_exit_frame',
                right_on='frame',
                how='inner'
            )
            
            # Exclude cases where ego_id == target_id
            merged_df = merged_df[merged_df['ego_id'] != merged_df['trackId']]

            # Add laneId information to ego_exit_first_frame_df and merged_df to filter based on laneId
            ego_lane_df = ego_exit_df[['trackId', 'frame', 'laneId']].rename(columns={'trackId': 'ego_id', 'frame': 'ego_first_exit_frame', 'laneId': 'ego_laneId'})
            merged_df = merged_df.merge(
                ego_lane_df,
                on=['ego_id', 'ego_first_exit_frame'],
                how='left'
            )
            
            # Filter to ensure ego and target are in the same lane at ego's first exit frame, but only if target is 'exit'
            merged_df = merged_df[
                (merged_df['activity_type'] == 'inside') |  # No laneId requirement if target is 'inside'
                ((merged_df['activity_type'] == 'exit') & (merged_df['laneId'] == merged_df['ego_laneId']))  # laneId must match if target is 'exit'
            ]

            for idx, row in merged_df.iterrows():
                ego_id = row['ego_id']
                target_id = row['trackId']
                ego_first_exit_frame = row['ego_first_exit_frame']
                
                # Get life cycles
                #ego_start_frame = life_cycles_dict[ego_id]['start_frame']
                ego_end_frame = life_cycles_dict[ego_id]['end_frame']
                target_start_frame = life_cycles_dict[target_id]['start_frame']
                target_end_frame = life_cycles_dict[target_id]['end_frame']
                
                # Compute overlapping intervals
                inter_start = max(ego_first_exit_frame, target_start_frame)
                inter_end = min(ego_end_frame, target_end_frame)
                
                if inter_start <= inter_end:
                    if ego_id not in scenarios_dict:
                        scenarios_dict[ego_id] = {
                            'targets': [target_id],
                            'start_frame': inter_start,
                            'end_frame': inter_end
                        }
                    else:
                        if target_id not in scenarios_dict[ego_id]['targets']:
                            scenarios_dict[ego_id]['targets'].append(target_id)
                            scenarios_dict[ego_id]['start_frame'] = min(
                                scenarios_dict[ego_id]['start_frame'], inter_start
                            )
                            scenarios_dict[ego_id]['end_frame'] = max(
                                scenarios_dict[ego_id]['end_frame'], inter_end
                            )
            
            # Convert scenarios_dict to list format
            scenarios_list = [
                [int(ego_id), list(map(int, value['targets'])), int(value['start_frame']), int(value['end_frame'])]
                for ego_id, value in scenarios_dict.items()
            ]
            return scenarios_list

        else:
            # Handle other cases as needed
            return []
    '''


    @staticmethod
    def identify_junction_scenarios_optimized(tracks_df, key_label):
        """
        Optimized function to identify junction scenarios based on road, lane, and turn type data.
        This method is designed to be reusable and extensible for different types of scenarios.

        Parameters:
        ----------
        tracks_df (DataFrame): DataFrame containing track data including 'frame', 'trackId', 'activity_type', etc.
        key_label (dict): Dictionary with turn type details for ego and target vehicles.

        Returns:
        ----------
        list: A list of scenarios with detailed information.
        """
        # Extract ego and target turn types from key_label
        ego_turn, target_turn = OpenDriveMapSelector_RounD.get_turn_types_from_response(key_label)

        # Define a mapping from (ego_turn, target_turn) to specific configuration
        scenario_config = {
            ('enter', 'inside'): {
                'ego_activity': 'enter',
                'target_activity': 'inside',
                'frame_selector': 'last',  # Use last frame of ego's 'enter' activity
                'additional_filters': [],  # No additional filters
            },
            ('exit', 'inside_or_exit'): {
                'ego_activity': 'exit',
                'target_activity': ['inside', 'exit'],
                'frame_selector': 'first',  # Use first frame of ego's 'exit' activity
                'additional_filters': [OpenDriveMapSelector_RounD.conditional_same_lane_filter],  # Conditional filter
            },
            ('exit', 'inside'): {
                'ego_activity': 'exit',
                'target_activity': 'inside',
                'frame_selector': 'first',
                'additional_filters': [],
            },
            ('exit', 'exit'): {
                'ego_activity': 'exit',
                'target_activity': 'exit',
                'frame_selector': 'first',
                'additional_filters': [
                    OpenDriveMapSelector_RounD.same_lane_filter  # Ensure ego and target are in the same lane
                ],
            },
            # Additional scenarios can be added here
        }

        scenario_key = (ego_turn, target_turn)
        if scenario_key not in scenario_config:
            # Handle unsupported scenarios
            print(f"Scenario ({ego_turn}, {target_turn}) not supported.")
            return []

        config = scenario_config[scenario_key]

        # Proceed with the generic scenario identification logic
        return OpenDriveMapSelector_RounD.generic_scenario_identifier(tracks_df, config)

    @staticmethod
    def generic_scenario_identifier(tracks_df, config):
        """
        Generalized method to identify scenarios based on provided configuration.

        Parameters:
        ----------
        tracks_df (DataFrame): DataFrame containing track data including 'frame', 'trackId', 'activity_type', etc.
        config (dict): Configuration dictionary specifying ego and target activities, filters, etc.

        Returns:
        ----------
        list: A list of scenarios with detailed information.
        """
        ego_activity = config['ego_activity']
        target_activity = config['target_activity']
        additional_filters = config.get('additional_filters', [])
        frame_selector = config.get('frame_selector', 'first')  # 'first' or 'last'

        # Filter tracks_df to keep only vehicles that contain the 'inside' activity
        vehicles_with_inside = tracks_df[tracks_df['activity_type'] == 'inside']['trackId'].unique()
        tracks_df = tracks_df[tracks_df['trackId'].isin(vehicles_with_inside)]

        # Ensure 'frame' is numeric
        tracks_df['frame'] = pd.to_numeric(tracks_df['frame'], errors='coerce')

        # Filter ego vehicles based on activity
        ego_df = tracks_df[tracks_df['activity_type'] == ego_activity]

        if frame_selector == 'first':
            ego_activity_frame_df = ego_df.groupby('trackId')['frame'].min().reset_index()
        elif frame_selector == 'last':
            ego_activity_frame_df = ego_df.groupby('trackId')['frame'].max().reset_index()
        else:
            raise ValueError("Invalid frame_selector value. Use 'first' or 'last'.")

        ego_activity_frame_df.rename(columns={'trackId': 'ego_id', 'frame': 'ego_activity_frame'}, inplace=True)

        # Filter target vehicles based on activity
        if isinstance(target_activity, list):
            target_df = tracks_df[tracks_df['activity_type'].isin(target_activity)]
        else:
            target_df = tracks_df[tracks_df['activity_type'] == target_activity]

        ego_lane_df = tracks_df[['trackId', 'frame', 'laneId']]
        ego_lane_df = ego_lane_df.rename(columns={'trackId': 'ego_id', 'frame': 'ego_activity_frame', 'laneId': 'laneId_ego'})
        ego_activity_frame_df = ego_activity_frame_df.merge(ego_lane_df, on=['ego_id', 'ego_activity_frame'], how='left')

        merged_df = ego_activity_frame_df.merge(
            target_df,
            left_on='ego_activity_frame',
            right_on='frame',
            how='inner',
            suffixes=('', '_target') 
        )

        # Exclude cases where ego_id == target_id
        merged_df = merged_df[merged_df['ego_id'] != merged_df['trackId']]

        # Apply additional filters if any
        for filter_func in additional_filters:
            merged_df = filter_func(merged_df)

        # Initialize scenarios dictionary
        scenarios_dict = {}

        # Precompute life cycles for each vehicle
        life_cycles = tracks_df.groupby('trackId').agg(
            start_frame=('frame', 'min'),
            end_frame=('frame', 'max')
        ).reset_index()
        life_cycles_dict = life_cycles.set_index('trackId').to_dict('index')

        # Iterate over merged DataFrame to compute scenarios
        for idx, row in merged_df.iterrows():
            ego_id = row['ego_id']
            target_id = row['trackId']
            ego_activity_frame = row['ego_activity_frame']

            # Get life cycles
            ego_end_frame = life_cycles_dict[ego_id]['end_frame']
            target_start_frame = life_cycles_dict[target_id]['start_frame']
            target_end_frame = life_cycles_dict[target_id]['end_frame']

            # Compute overlapping intervals
            inter_start = max(ego_activity_frame, target_start_frame)
            inter_end = min(ego_end_frame, target_end_frame)

            if inter_start <= inter_end:
                if ego_id not in scenarios_dict:
                    scenarios_dict[ego_id] = {
                        'targets': [target_id],
                        'start_frame': inter_start,
                        'end_frame': inter_end
                    }
                else:
                    if target_id not in scenarios_dict[ego_id]['targets']:
                        scenarios_dict[ego_id]['targets'].append(target_id)
                        scenarios_dict[ego_id]['start_frame'] = min(
                            scenarios_dict[ego_id]['start_frame'], inter_start
                        )
                        scenarios_dict[ego_id]['end_frame'] = max(
                            scenarios_dict[ego_id]['end_frame'], inter_end
                        )

        # Convert scenarios_dict to list format
        scenarios_list = [
            [int(ego_id), list(map(int, value['targets'])), int(value['start_frame']), int(value['end_frame'])]
            for ego_id, value in scenarios_dict.items()
        ]
        return scenarios_list

    @staticmethod
    def same_lane_filter(merged_df):
        filtered_df = merged_df[merged_df['laneId_ego'] == merged_df['laneId']]
        return filtered_df
    
    @staticmethod
    def conditional_same_lane_filter(merged_df):
        target_exit_mask = merged_df['activity_type'] == 'exit'

        if target_exit_mask.any():
            exit_rows = merged_df[target_exit_mask]
            non_exit_rows = merged_df[~target_exit_mask]

            exit_rows_filtered = OpenDriveMapSelector_RounD.same_lane_filter(exit_rows)
            merged_df = pd.concat([exit_rows_filtered, non_exit_rows], ignore_index=True)

        return merged_df