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
import junctions_scenario_mining.bendplatz_01 as bendplatz
import junctions_scenario_mining.frankenburg_02 as frankenburg
import junctions_scenario_mining.heckstrasse_03 as heckstrasse
import junctions_scenario_mining.aseag_04 as aseag
import xml.etree.ElementTree as ET
import math
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # 或 'Qt5Agg', 'GTK3Agg', 'WXAgg' 等，取决于你的系统配置
import matplotlib.pyplot as plt


dataset_option = 'inD'
metric_option = {"Time-Scale": ["Encroachment Time (ET)", "Post-encroachment Time (PET)", "Potential Time To Collision (PTTC)", \
                           "Time Exposed TTC (TET)", \
                            "Time Integrated TTC (TIT)", "Time To Closest Encounter (TTCE)", "Time To Brake (TTB)",\
                                "Time To Kickdown (TTK)", "Time To Steer (TTS)", "Time To Collision (TTC)",\
                                    "Time Headway (THW)"]}
metric_suboption = "Time To Collision (TTC)" 

dataset_load = './01_tracks.csv'

def select_opendrive_map(file_path):
    # 从文件名中提取数字
    match = re.search(r'\d+', file_path)
    if match:
        index = int(match.group(0))
        # 根据不同的数字范围选择对应的地图文件和处理逻辑
        if 0 <= index <= 6:
            #添加了road和lane
            tracks_meta_df = aseag.update_tracks_with_lane_info(file_path, './junctions_scenario_mining/04_aseag/aseag.xodr')
            #添加了活动类型（如:right,left,straight）
            tracks_meta_df = aseag.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df
        
        elif 7 <= index <= 17:

            tracks_meta_df = bendplatz.update_tracks_with_lane_info(file_path, './junctions_scenario_mining/01_bendplatz/bendplatz.xodr')
            tracks_meta_df = bendplatz.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df

        elif 18 <= index <= 29:

            tracks_meta_df = frankenburg.update_tracks_with_lane_info(file_path, './junctions_scenario_mining/02_frankenburg/frankenburg.xodr')
            tracks_meta_df = frankenburg.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df

        elif 30 <= index <= 32:

            tracks_meta_df = heckstrasse.update_tracks_with_lane_info(file_path, './junctions_scenario_mining/03_heckstrasse/heckstrasse.xodr')
            tracks_meta_df = heckstrasse.process_tracks(tracks_meta_df)
            print(tracks_meta_df)
            return tracks_meta_df
    else:
        # 默认处理逻辑，如果没有找到合适的数字或者数字不在范围内
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
    根据提供的道路、车道和转向类型数据识别交叉口场景。

    参数:
        tracks_df (DataFrame): 包含追踪数据的 DataFrame，包括 'road_lane' 和 'turn_type' 列。
        key_label (dict): 包含Ego和Target车辆转向类型的字典。

    返回:
        scenarios (list): 包含识别到的各种场景信息的列表。
    """
    ego_turn, target_turn = get_turn_types_from_response(key_label)
    scenario_lists = []

    # 计算每个trackId的生命周期范围
    life_cycles = tracks_df.groupby('trackId').agg(start_frame=('frame', 'min'), end_frame=('frame', 'max')).reset_index()

    # 提取 road ID
    tracks_df['road_id'] = tracks_df['road_lane'].apply(lambda x: int(str(x).split('.')[0]))

    # 筛选出符合自车转向类型的数据行
    ego_tracks = tracks_df[tracks_df['turn_type'] == ego_turn].merge(life_cycles, on='trackId')
    target_tracks = tracks_df[tracks_df['turn_type'] == target_turn].merge(life_cycles, on='trackId')

    # 遍历每一个自车数据行
    for _, ego_row in ego_tracks.iterrows():
        ego_id = ego_row['trackId']
        ego_life = [ego_row['start_frame'], ego_row['end_frame']]
        ego_road_id = ego_row['road_id']

        # 遍历每一个目标车数据行
        for _, target_row in target_tracks.iterrows():
            target_id = target_row['trackId']
            if target_id == ego_id:
                continue  # 自车与目标车相同，跳过
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
                    new_scenario = {
                        'ego_id': ego_id,
                        'target_id': target_id,
                        'begin_frame': inter[0],
                        'end_frame': inter[1]
                    }
                    # 确保不重复添加相同的场景
                    if new_scenario not in scenario_lists:
                        scenario_lists.append(new_scenario)

    return scenario_lists

# 假设 tracks_meta_df 是已经载入的 DataFrame，包含了必要的列
# tracks_meta_df = pd.read_csv("path_to_tracks_meta_df.csv")
# scenarios = identify_junction_scenarios(tracks_meta_df)
# print(scenarios)

def extract_json_from_response(response):
    """
    Extract key labels from GPT response

    Parameters:
    ----------
    Inputs:
        response (str): response of GPT containing the key lables of scenarios

    Returns:
        key labels in the format of json
    ----------
    """
    start_index = response.find('{')
    end_index = response.rfind('}') + 1  # +1 to include the closing brace
    json_string = response[start_index:end_index]
    json_string = json_string.replace("'", '"')  # Replace single quotes with double quotes for valid JSON
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
reminder_holder = st.empty()
animation_holder = st.empty()

tracks_original = pd.read_csv(dataset_load) 
tracks_meta_df = select_opendrive_map(dataset_load)

response = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'right'
    },
    'Target Vehicle': 
    {
        'turn_type': 'straight'
    }
}
"""


key_label = extract_json_from_response(response)

scenarioList = identify_junction_scenarios(tracks_meta_df, key_label)

fictive_ego_list_sampled = []
fictive_target_dicts_sampled = {}

for scenario in scenarioList:
    ego_id = scenario['ego_id']
    target_ids = scenario['target_id']
    begin_frame = scenario['begin_frame']
    end_frame = scenario['end_frame']

    # Make sure target_ids is a list
    if isinstance(target_ids, int):
        target_ids = [target_ids]

    # Get ego vehicle data
    egoVehData = tracks_original[(tracks_original['trackId'] == ego_id) & 
                                 (tracks_original['frame'] >= begin_frame) & 
                                 (tracks_original['frame'] <= end_frame)].reset_index(drop=True)
    fictive_ego_list_sampled.append(egoVehData)

    # Get target vehicle data
    tgtVehsData = []
    for tgt_id in target_ids:
        tgtVehData = tracks_original[(tracks_original['trackId'] == tgt_id) & 
                                     (tracks_original['frame'] >= begin_frame) & 
                                     (tracks_original['frame'] <= end_frame)].reset_index(drop=True)
        tgtVehsData.append(tgtVehData)
    
    fictive_target_dicts_sampled[ego_id] = tgtVehsData

# Now call the preview function
preview_scenario(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, animation_holder, "inD")
