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
import re

class OpenDriveMapSelector:
    def __init__(self,file_path,tracks_original):
        self.file_path = file_path
        self.tracks_original = tracks_original
        self.tracks_meta_df = self.select_opendrive_map()
    def select_opendrive_map(self):
        """
        Selects and processes the OpenDRIVE map file based on its numeric index, updating tracks with lane information and activity types.

        Parameters:
        ----------
        file_path (str): The file path that contains the numeric index which dictates the processing logic.

        Returns:
        ----------
        DataFrame: A pandas DataFrame that includes updated track information with road and lane details along with activity types.
        """
        match = re.search(r'\d+', self.file_path.name)
        if match:
            index = int(match.group(0))
            if 0 <= index <= 6:
                tracks_meta_df = aseag.AseagProcessor().update_tracks_with_lane_info(self.tracks_original)
                tracks_meta_df = aseag.AseagProcessor().process_tracks(tracks_meta_df)
                print(tracks_meta_df)
                return tracks_meta_df
            elif 7 <= index <= 17:
                print('12\n\n',self.file_path,'\n\n')
                tracks_meta_df = bendplatz.BendplatzProcessor().update_tracks_with_lane_info(self.tracks_original)
                tracks_meta_df = bendplatz.BendplatzProcessor().process_tracks(tracks_meta_df)
                print(tracks_meta_df)
                return tracks_meta_df
            elif 18 <= index <= 29:
                tracks_meta_df = frankenburg.FrankenbergProcessor().update_tracks_with_lane_info(self.tracks_original)
                tracks_meta_df = frankenburg.FrankenbergProcessor().process_tracks(tracks_meta_df)
                print(tracks_meta_df)
                return tracks_meta_df
            elif 30 <= index <= 32:
                tracks_meta_df = heckstrasse.HeckstrasseProcessor().update_tracks_with_lane_info(self.tracks_original)
                tracks_meta_df = heckstrasse.HeckstrasseProcessor().process_tracks(tracks_meta_df)
                print(tracks_meta_df)
                return tracks_meta_df
        else:
            print("No valid index found, or out of range. No operation performed.")

    @staticmethod
    def get_turn_types_from_response(response):
        """
        Extract turn types from a given response dictionary.

        Parameters:
        -----------
        response (dict): A dictionary containing turn types for vehicles.

        Returns:
        ego_turn_type (str): Turn type of the ego vehicle.
        target_turn_type (str): Turn type of the target vehicle.
        """
        ego_turn_type = response['Ego Vehicle']['turn_type']
        target_turn_type = response['Target Vehicle']['turn_type']
        return ego_turn_type, target_turn_type

    @staticmethod
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
        ego_turn, target_turn = OpenDriveMapSelector.get_turn_types_from_response(key_label)
        scenario_lists = []

        life_cycles = tracks_df.groupby('trackId').agg(start_frame=('frame', 'min'), end_frame=('frame', 'max')).reset_index()
        tracks_df['road_id'] = tracks_df['road_lane'].apply(lambda x: int(str(x).split('.')[0]))
        ego_tracks = tracks_df[tracks_df['turn_type'] == ego_turn].merge(life_cycles, on='trackId')
        target_tracks = tracks_df[tracks_df['turn_type'] == target_turn].merge(life_cycles, on='trackId')
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
        ego_turn, target_turn = OpenDriveMapSelector.get_turn_types_from_response(key_label)
        tracks_df['road_id'] = tracks_df['road_lane'].apply(lambda x: int(str(x).split('.')[0]))
        life_cycles = tracks_df.groupby('trackId').agg(
            start_frame=('frame', 'min'),
            end_frame=('frame', 'max'),
            road_id=('road_id', 'first'),
            turn_type=('turn_type', 'first')
        ).reset_index()

        ego_tracks = life_cycles[life_cycles['turn_type'] == ego_turn]
        target_tracks = life_cycles[life_cycles['turn_type'] == target_turn]
        scenarios = {}
        processed_scenarios = set()

        for _, ego_row in ego_tracks.iterrows():
            ego_id = ego_row['trackId']
            ego_life = [ego_row['start_frame'], ego_row['end_frame']]
            ego_road_id = ego_row['road_id']

            for _, target_row in target_tracks.iterrows():
                target_id = target_row['trackId']
                if target_id == ego_id:
                    continue

                target_life = [target_row['start_frame'], target_row['end_frame']]
                target_road_id = target_row['road_id']
                inter = intersection_judge(ego_life, target_life)
                if inter:
                    ego_start_road_id = tracks_df[(tracks_df['trackId'] == ego_id) & (tracks_df['frame'] == ego_row['start_frame'])]['road_id'].iloc[0]
                    target_start_road_id = tracks_df[(tracks_df['trackId'] == target_id) & (tracks_df['frame'] == target_row['start_frame'])]['road_id'].iloc[0]
                    last_frame = inter[1]
                    ego_last_road_id = tracks_df[(tracks_df['trackId'] == ego_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]
                    target_last_road_id = tracks_df[(tracks_df['trackId'] == target_id) & (tracks_df['frame'] == last_frame)]['road_id'].iloc[0]

                    if ego_last_road_id == target_last_road_id and target_start_road_id != target_last_road_id and ego_start_road_id != ego_last_road_id:
                        if ego_id not in scenarios:
                            scenarios[ego_id] = {'targets': [target_id], 'start_frame': inter[0], 'end_frame': inter[1]}
                        else:
                            if target_id not in scenarios[ego_id]['targets']:
                                scenarios[ego_id]['targets'].append(target_id)
                                scenarios[ego_id]['start_frame'] = min(scenarios[ego_id]['start_frame'], inter[0])
                                scenarios[ego_id]['end_frame'] = max(scenarios[ego_id]['end_frame'], inter[1])

        scenarios = [[key, value['targets'], value['start_frame'], value['end_frame']] for key, value in scenarios.items()]
        return scenarios

# Example usage:
# selector = OpenDriveMapSelector()
# df = selector.select_opendrive_map("some_path_with_index")
# scenarios = selector.identify_junction_scenarios(df, key_label)
