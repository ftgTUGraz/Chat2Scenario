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


tracks_meta_df = select_opendrive_map(dataset_load)
scenarioList = mainFunctionScenarioIdentification(tracks_meta_df, key_label,  progress_bar)
                   