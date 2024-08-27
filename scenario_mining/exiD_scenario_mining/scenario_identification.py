import re
import csv
import scenario_mining.exiD_scenario_mining.playground1_18 as playground1_18
import scenario_mining.exiD_scenario_mining.playground19_38 as playground19_38
import scenario_mining.exiD_scenario_mining.playground39_52 as playground39_52
import scenario_mining.exiD_scenario_mining.playground53_60 as playground53_60
import scenario_mining.exiD_scenario_mining.playground61_72 as playground61_72
import scenario_mining.exiD_scenario_mining.playground73_77 as playground73_77
import scenario_mining.exiD_scenario_mining.playground78_92 as playground78_92
from NLP.Scenario_Description_Understand import *
import streamlit as st
import pandas as pd
from GUI.Web_Sidebar import *
from utils.helper_original_scenario import generate_xosc
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
matplotlib.use('Agg')  # Or 'Qt5Agg', 'GTK3Agg', 'WXAgg', etc., depending on your system configuration
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import shapely.wkt
import pickle
import json
from shapely.geometry import mapping
import json
from shapely.geometry import shape, Polygon
from data import (
    onramp_polygon_1_18, offramp_polygon_1_18, lanes_polygons_1_18, json_data_1_18, onramp_polygons_19_38, 
    offramp_polygons_19_38, json_data_19_38, lanes_polygons_19_38, onramp_polygons_39_52, offramp_polygons_39_52, 
    json_data_39_52, lanes_polygons_39_52, lanes_polygons_53_60, offramp_polygons_53_60, json_data_53_60, 
    onramp_polygons_53_60, json_data_61_72, onramp_polygons_61_72, offramp_polygons_61_72, lanes_polygons_61_72, 
    json_data_73_77, lanes_polygons_73_77, onramp_polygons_73_77, lanes_polygons_78_92, onramp_polygons_78_92, json_data_78_92
)

class ScenarioIdentification:

    @staticmethod
    def get_utm_origin(recordings_meta_file):
        """
        Extracts xUtmOrigin and yUtmOrigin values from the XX_recordingsMeta.csv file.

        Parameters:
        recordings_meta_file (str): Path to the XX_recordingsMeta.csv file

        Returns:
        tuple: (xUtmOrigin, yUtmOrigin)
        """
        with open(recordings_meta_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                x_utm_origin = float(row['xUtmOrigin'])
                y_utm_origin = float(row['yUtmOrigin'])
                return x_utm_origin, y_utm_origin
        raise ValueError("xUtmOrigin and yUtmOrigin not found in recordings meta file")

    @staticmethod
    def select_playground(file_path):
        """
        Select the corresponding playground module based on the number in the file name and perform the corresponding operations.

        Parameters:
        ----------
        file_path (str): File path containing the numeric index to determine the processing logic.

        Returns:
        ----------
        None
        """
        # Initialize the plot
        fig, ax = plt.subplots()
        # Extract the number from the file name
        match = re.search(r'\d+', file_path.name)
        if match:
            index = int(match.group(0))
            # Select the corresponding playground module based on different number ranges
            if 0 <= index <= 18:
                if 0 <= index <= 9:
                    input_file_1_18 = f'0{index}_tracks.csv'
                    output_file_1_18 = f'0{index}_updated_tracks.csv'
                else:
                    input_file_1_18 = f'{index}_tracks.csv'
                    output_file_1_18 = f'{index}_updated_tracks.csv'

                track_processor = playground1_18.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_1_18, onramp_polygon_1_18, offramp_polygon_1_18, lanes_polygons_1_18)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygon_1_18, offramp_polygon_1_18, lanes_polygons_1_18)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_1_18, updated_tracks_df

            elif 19 <= index <= 38:
                input_file_19_38 = f'{index}_tracks.csv'
                output_file_19_38 = f'{index}_updated_tracks.csv'
                track_processor = playground19_38.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_19_38, onramp_polygons_19_38, offramp_polygons_19_38, lanes_polygons_19_38)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygons_19_38, offramp_polygons_19_38, lanes_polygons_19_38)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_19_38, updated_tracks_df

            elif 39 <= index <= 52:
                input_file_39_52 = f'{index}_tracks.csv'
                output_file_39_52 = f'{index}_updated_tracks.csv'
                track_processor = playground39_52.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_39_52, onramp_polygons_39_52, offramp_polygons_39_52, lanes_polygons_39_52)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygons_39_52, offramp_polygons_39_52, lanes_polygons_39_52)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_39_52, updated_tracks_df

            elif 53 <= index <= 60:
                input_file_53_60 = f'{index}_tracks.csv'
                output_file_53_60 = f'{index}_updated_tracks.csv'
                track_processor = playground53_60.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_53_60, onramp_polygons_53_60, offramp_polygons_53_60, lanes_polygons_53_60)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygons_53_60, offramp_polygons_53_60, lanes_polygons_53_60)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_53_60, updated_tracks_df

            elif 61 <= index <= 72:
                input_file_61_72 = f'{index}_tracks.csv'
                output_file_61_72 = f'{index}_updated_tracks.csv'
                track_processor = playground61_72.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_61_72, onramp_polygons_61_72, offramp_polygons_61_72, lanes_polygons_61_72)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygons_61_72, offramp_polygons_61_72, lanes_polygons_61_72)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_61_72, updated_tracks_df

            elif 73 <= index <= 77:
                input_file_73_77 = f'{index}_tracks.csv'
                output_file_73_77 = f'{index}_updated_tracks.csv'
                track_processor = playground73_77.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_73_77, onramp_polygons_73_77, {}, lanes_polygons_73_77)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygons_73_77, {}, lanes_polygons_73_77)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_73_77, updated_tracks_df

            elif 78 <= index <= 92:
                input_file_78_92 = f'{index}_tracks.csv'
                output_file_78_92 = f'{index}_updated_tracks.csv'
                track_processor = playground78_92.TrackDataProcessor()
                #updated_tracks_df = track_processor.extract_turn_type_and_lane(input_file_78_92, onramp_polygons_78_92, {}, lanes_polygons_78_92)
                updated_tracks_df = track_processor.extract_turn_type_and_lane(file_path, onramp_polygons_78_92, {}, lanes_polygons_78_92)
                ax.set_xlabel("X Coordinate")
                ax.set_ylabel("Y Coordinate")
                ax.set_title("Visualization of Polygons from JSON Data")
                ax.legend()
                ax.grid(True)
                ax.axis('equal')
                return json_data_78_92, updated_tracks_df

    @staticmethod
    def get_activity_from_LLM_response_ExitD(LLM_response):
        """
        Refine the activity from LLM response.

        Parameters:
        -----------
        Inputs:
            LLM_response (dict): a dictionary containing LLM response

        Returns:
            req_ego_latAct (str): required lateral activity of ego vehicle
            req_ego_lonAct (str): required longitudinal activity of ego vehicle 
            req_ego_rampAct (str, optional): required ramp activity of ego vehicle (only for exitD)
            req_tgt_startPos (str): required start position of target vehicle 
            req_tgt_endPos (str): required end position of target vehicle 
            req_tgt_latAct (str): required lateral activity of target vehicle 
            req_tgt_longAct (str): required longitudinal activity of target vehicle
            req_tgt_rampAct (str, optional): required ramp activity of target vehicle (only for exitD)
        ----------
        """

        # Ego 
        req_ego_latAct = LLM_response['Ego Vehicle']['Ego lateral activity'][0]
        req_ego_lonAct = LLM_response['Ego Vehicle']['Ego longitudinal activity'][0]
        req_ego_rampAct = LLM_response['Ego Vehicle']['Ego ramp activity'][0]

        # Target
        tgt_startPos = LLM_response['Target Vehicle #1']['Target start position']
        start_item = list(tgt_startPos.items())[0]
        req_tgt_startPos = start_item[1][0]
        
        tgt_endPos = LLM_response['Target Vehicle #1']['Target end position']
        end_item = list(tgt_endPos.items())[0]
        req_tgt_endPos = end_item[1][0]

        req_tgt_latAct = LLM_response['Target Vehicle #1']['Target behavior']['target lateral activity'][0]
        req_tgt_longAct = LLM_response['Target Vehicle #1']['Target behavior']['target longitudinal activity'][0]
        req_tgt_rampAct = LLM_response['Target Vehicle #1']['Target behavior']['target ramp activity'][0]

        return req_ego_latAct, req_ego_lonAct, req_ego_rampAct, req_tgt_startPos, req_tgt_endPos, req_tgt_latAct, req_tgt_longAct, req_tgt_rampAct

    @staticmethod
    def get_activity_from_LLM_response_ExitD_Ramp(LLM_response):
        """
        Refine the activity from LLM response.

        Parameters:
        -----------
        Inputs:
            LLM_response (dict): a dictionary containing LLM response

        Returns:
            req_ego_latAct (str): required lateral activity of ego vehicle
            req_ego_lonAct (str): required longitudinal activity of ego vehicle 
            req_ego_rampAct (str, optional): required ramp activity of ego vehicle (only for exitD)
            req_tgt_startPos (str): required start position of target vehicle 
            req_tgt_endPos (str): required end position of target vehicle 
            req_tgt_latAct (str): required lateral activity of target vehicle 
            req_tgt_longAct (str): required longitudinal activity of target vehicle
            req_tgt_rampAct (str, optional): required ramp activity of target vehicle (only for exitD)
        ----------
        """

        # Ego 
        req_ego_rampAct = LLM_response['Ego Vehicle']['Ego ramp activity'][0]
        req_tgt_rampAct = LLM_response['Target Vehicle #1']['Target ramp activity'][0]

        return req_ego_rampAct, req_tgt_rampAct

    @staticmethod
    def mainFunctionScenarioIdentification_ExitD(tracks_36, key_label, latActDict, longActDict, interactIdDict, progress_bar, file_path):
        """
        Main function to search the desired scenarios

        Parameters:
        -----------
        Inputs:
            track_36 (df): track read by pd.read_csv()
            key_label (dict): LLM response
            latActDict (dict): [key: egoID; value: df['frame', 'id', 'LateralActivity', 'lateral', 'x', 'y']]
            longActDict (dict): [key: egoID; value: df['frame', 'id', 'LongitudinalActivity', 'lateral', 'x', 'y']]
            interactIdDict (dict): [key: id; value: ID of interacting targets] 
            progress_bar (st.progress(0)): initialize the progress bar

        Returns:
            scenarioLists (list): a list contains multiple sublist in the format of [egoID, [tgtID], begFrame, endFrame]
        ----------
        """
        if 'Ego lateral activity' in key_label['Ego Vehicle']:
            req_ego_latAct, req_ego_lonAct, req_tgt_startPos, req_tgt_endPos, \
            req_tgt_latAct, req_tgt_longAct , req_tgt_startPos_type, req_tgt_endPos_type = get_activity_from_LLM_response(key_label)
            scenarioLists = []
            for key in latActDict:
                scenarioList = []

                # Current ego vehicle and interacting targets
                curr_ego = key  # current ego id
                curr_ego_latActs = latActDict[curr_ego]  # current ego lateral activities
                curr_ego_lonActs = longActDict[curr_ego]  # current ego longitudinal activities
                curr_interact_tgts = interactIdDict[curr_ego]  # targets interacting with current ego

                # Judge the ego vehicle lateral activity
                if req_ego_latAct not in curr_ego_latActs['LateralActivity'].values:
                    continue
                egoLatActFram = find_start_end_frame_of_latAct(curr_ego_latActs, req_ego_latAct)
                egoLatAct_endFrame = egoLatActFram[1]
                
                tgt_list = []
                for curr_interact_tgt in curr_interact_tgts:
                    if curr_interact_tgt == -1 or curr_interact_tgt not in latActDict or curr_interact_tgt not in longActDict:
                        continue

                    # Judge the target vehicle lateral activity
                    curr_interact_tgt_latAct = latActDict[curr_interact_tgt]
                    if req_tgt_latAct not in curr_interact_tgt_latAct['LateralActivity'].values:
                        continue
                    tgtLatActFram = find_start_end_frame_of_latAct(curr_interact_tgt_latAct, req_tgt_latAct)
                    
                    # Find the intersection between ego and target frames
                    inter = intersection_judge(egoLatActFram, tgtLatActFram)
                    if len(inter) == 0:
                        continue

                    # Current ego info
                    curr_ego_start_row = tracks_36[(tracks_36['trackId'] == curr_ego) & (tracks_36['frame'] == inter[0])].reset_index(drop=True)
                    curr_ego_end_row = tracks_36[(tracks_36['trackId'] == curr_ego) & (tracks_36['frame'] == inter[1])].reset_index(drop=True)
                    curr_ego_life = tracks_36[(tracks_36['trackId'] == curr_ego) & tracks_36['frame'].between(inter[0], inter[1])].reset_index(drop=True)
                    # Current target info
                    curr_tgt_start_row = tracks_36[(tracks_36['trackId'] == curr_interact_tgt) & (tracks_36['frame'] == inter[0])].reset_index(drop=True)
                    curr_tgt_end_row = tracks_36[(tracks_36['trackId'] == curr_interact_tgt) & (tracks_36['frame'] == inter[1])].reset_index(drop=True)

                    # lane ID 
                    if curr_ego_end_row.empty or curr_ego_start_row.empty or curr_tgt_start_row.empty or curr_tgt_end_row.empty:
                        continue
                    
                    if 'laneId' not in curr_ego_end_row or 'laneId' not in curr_ego_start_row or 'laneId' not in curr_tgt_start_row or 'laneId' not in curr_tgt_end_row:
                        continue

                    if curr_ego_end_row['laneId'].empty or curr_ego_start_row['laneId'].empty or curr_tgt_start_row['laneId'].empty or curr_tgt_end_row['laneId'].empty:
                        continue

                    if 0 not in curr_ego_end_row['laneId'].index or 0 not in curr_ego_start_row['laneId'].index or 0 not in curr_tgt_start_row['laneId'].index or 0 not in curr_tgt_end_row['laneId'].index:
                        continue                              
                    if curr_ego_end_row['laneId'][0] ==  'Unknown' or curr_ego_start_row['laneId'][0]==  'Unknown' or curr_tgt_start_row['laneId'][0] ==  'Unknown'or curr_tgt_end_row['laneId'][0]==  'Unknown':
                        continue

                    curr_ego_start_lane = curr_ego_start_row['laneId'][0]
                    curr_ego_end_lane = curr_ego_end_row['laneId'][0]
                    curr_tgt_start_lane = curr_tgt_start_row['laneId'][0]
                    curr_tgt_end_lane = curr_tgt_end_row['laneId'][0]

                    match = re.search(r'\d+', file_path)
                    if match:
                        index = int(match.group(0))
                        if 39 <= index <= 52:
                            ego_drive_direction = curr_ego_end_row['xCenter'][0] - curr_ego_start_row['xCenter'][0]
                            delta_x_tgt_ego_start = curr_tgt_start_row['xCenter'][0] - curr_ego_start_row['xCenter'][0]                    
                        else:
                            ego_drive_direction = -(curr_ego_end_row['xCenter'][0] - curr_ego_start_row['xCenter'][0])
                            delta_x_tgt_ego_start = -(curr_tgt_start_row['xCenter'][0] - curr_ego_start_row['xCenter'][0])

                    laneDiffStart = curr_tgt_start_lane - curr_ego_start_lane
                    curr_tgt_pos_start = pos_calc(laneDiffStart, ego_drive_direction, delta_x_tgt_ego_start, req_tgt_startPos_type)

                    if req_ego_latAct == 'off-ramp':
                        for i in range(len(curr_ego_latActs) - 2, -1, -1):
                            if curr_tgt_pos_start is None or curr_tgt_pos_start != req_tgt_startPos:
                                egoLatActFram = find_start_end_frame_of_off_ramp(curr_ego_latActs.iloc[:i], egoLatAct_endFrame)
                                inter = intersection_judge(egoLatActFram, tgtLatActFram)
                                if len(inter) == 0:
                                    continue

                                curr_ego_start_row = tracks_36[(tracks_36['trackId'] == curr_ego) & (tracks_36['frame'] == inter[0])].reset_index(drop=True)
                                curr_ego_end_row = tracks_36[(tracks_36['trackId'] == curr_ego) & (tracks_36['frame'] == inter[1])].reset_index(drop=True)
                                curr_ego_life = tracks_36[(tracks_36['trackId'] == curr_ego) & tracks_36['frame'].between(inter[0], inter[1])].reset_index(drop=True)
                                curr_tgt_start_row = tracks_36[(tracks_36['trackId'] == curr_interact_tgt) & (tracks_36['frame'] == inter[0])].reset_index(drop=True)
                                curr_tgt_end_row = tracks_36[(tracks_36['trackId'] == curr_interact_tgt) & (tracks_36['frame'] == inter[1])].reset_index(drop=True)

                                curr_ego_start_lane = curr_ego_start_row['laneId'][0]
                                curr_ego_end_lane = curr_ego_end_row['laneId'][0]
                                curr_tgt_start_lane = curr_tgt_start_row['laneId'][0]
                                curr_tgt_end_lane = curr_tgt_end_row['laneId'][0]
                                
                                match = re.search(r'\d+', file_path)
                                if match:
                                    index = int(match.group(0))
                                    if 39 <= index <= 52:
                                        ego_drive_direction = curr_ego_end_row['xCenter'][0] - curr_ego_start_row['xCenter'][0]
                                        delta_x_tgt_ego_start = curr_tgt_start_row['xCenter'][0] - curr_ego_start_row['xCenter'][0]                                
                                    else:
                                        ego_drive_direction = -(curr_ego_end_row['xCenter'][0] - curr_ego_start_row['xCenter'][0])
                                        delta_x_tgt_ego_start = -(curr_tgt_start_row['xCenter'][0] - curr_ego_start_row['xCenter'][0])
                                        
                                laneDiffStart = curr_tgt_start_lane - curr_ego_start_lane
                                curr_tgt_pos_start = pos_calc(laneDiffStart, ego_drive_direction, delta_x_tgt_ego_start, req_tgt_startPos_type)

                                if curr_tgt_pos_start is None or curr_tgt_pos_start != req_tgt_startPos:
                                    continue
                            else:
                                break
                        
                    if curr_tgt_pos_start == req_tgt_startPos:
                        match = re.search(r'\d+', file_path)
                        if match:
                            index = int(match.group(0))
                            if 39 <= index <= 52:
                                delta_x_tgt_ego_end = curr_tgt_end_row['xCenter'][0] - curr_ego_end_row['xCenter'][0]
                            else:
                                delta_x_tgt_ego_end = -(curr_tgt_end_row['xCenter'][0] - curr_ego_end_row['xCenter'][0])

                        laneDiffEnd = curr_tgt_end_lane - curr_ego_end_lane
                        curr_tgt_pos_end = pos_calc(laneDiffEnd, ego_drive_direction, delta_x_tgt_ego_end, req_tgt_endPos_type)
                        if curr_tgt_pos_end == req_tgt_endPos:
                            if req_ego_lonAct == 'NA' and req_tgt_longAct == 'NA':
                                tgt_list.append(curr_interact_tgt)
                                interFinal = []
                                interFinal.append(inter[0])
                                interFinal.append(inter[1])
                                continue

                            if req_ego_lonAct not in curr_ego_lonActs['LongitudinalActivity'].values:
                                continue

                            curr_tgt_lonAct = longActDict[curr_interact_tgt]
                            if req_tgt_longAct not in curr_tgt_lonAct['LongitudinalActivity'].values:
                                continue
                            egoLonActFram = find_start_end_frame_of_lonAct(curr_ego_lonActs, req_ego_lonAct)
                            tgtLonActFram = find_start_end_frame_of_lonAct(curr_tgt_lonAct, req_tgt_longAct)
                            interLon = intersection_judge(egoLonActFram, tgtLonActFram)
                            if len(interLon) != 0:
                                interFinal = intersection_judge(inter, interLon)
                                if len(interFinal) != 0:
                                    tgt_list.append(curr_tgt_start_row['trackId'][0])
                                    break

                if len(tgt_list) != 0:
                    scenarioList.append(curr_ego)
                    scenarioList.append(tgt_list)
                    scenarioList.append(interFinal[0])
                    scenarioList.append(interFinal[1])

                if len(scenarioList) != 0:
                    scenarioLists.append(scenarioList)
        else:
            req_ego_rampAct, req_tgt_rampAct = ScenarioIdentification.get_activity_from_LLM_response_ExitD_Ramp(key_label)
            scenarioLists = []
            for key in tracks_36['trackId'].unique():
                curr_ego = key  # current ego id
                curr_ego_rampActs = tracks_36[tracks_36['trackId'] == curr_ego]['activity_type'].unique()
                if req_ego_rampAct not in curr_ego_rampActs:
                    continue

                curr_interact_tgts = interactIdDict.get(curr_ego, [])
                for curr_interact_tgt in curr_interact_tgts:
                    if curr_interact_tgt == -1:
                        continue
                    curr_tgt_rampActs = tracks_36[tracks_36['trackId'] == curr_interact_tgt]['activity_type'].unique()
                    if req_tgt_rampAct not in curr_tgt_rampActs:
                        continue

                    scenarioList = [curr_ego, [curr_interact_tgt]]
                    scenarioLists.append(scenarioList)

        return scenarioLists
