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
from scenario_mining.junctions_scenario_mining.junctions_scenario_analysis import *
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


dataset_option = 'inD'
metric_option = {"Time-Scale": ["Encroachment Time (ET)", "Post-encroachment Time (PET)", "Potential Time To Collision (PTTC)", \
                           "Time Exposed TTC (TET)", \
                            "Time Integrated TTC (TIT)", "Time To Closest Encounter (TTCE)", "Time To Brake (TTB)",\
                                "Time To Kickdown (TTK)", "Time To Steer (TTS)", "Time To Collision (TTC)",\
                                    "Time Headway (THW)"]}
metric_suboption = "Time To Collision (TTC)" 

dataset_load = './08_tracks.csv'


reminder_holder = st.empty()
animation_holder = st.empty()

tracks_original = pd.read_csv(dataset_load) 
#tracks_meta_df = OpenDriveMapSelector(dataset_load).select_opendrive_map()
tracks_meta_df = OpenDriveMapSelector(dataset_load,tracks_original).select_opendrive_map()
response1 = """
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

response2 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'left'
    },
    'Target Vehicle': 
    {
        'turn_type': 'left'
    }
}
"""
response3 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'left'
    },
    'Target Vehicle': 
    {
        'turn_type': 'right'
    }
}
"""
response4 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'left'
    },
    'Target Vehicle': 
    {
        'turn_type': 'straight'
    }
}
"""
response5 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'right'
    },
    'Target Vehicle': 
    {
        'turn_type': 'left'
    }
}
"""
response6 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'right'
    },
    'Target Vehicle': 
    {
        'turn_type': 'right'
    }
}
"""

response7 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'straight'
    },
    'Target Vehicle': 
    {
        'turn_type': 'left'
    }
}
"""
response8 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'straight'
    },
    'Target Vehicle': 
    {
        'turn_type': 'right'
    }
}
"""
response9 = """
{
    'Ego Vehicle': 
    {
        'turn_type': 'straight'
    },
    'Target Vehicle': 
    {
        'turn_type': 'straight'
    }
}
"""
'''
# Process and print results individually
key_label1 = extract_json_from_response(response1)
scenarioList1 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label1)
print("Scenario 1 (Right Turn vs. Straight):", scenarioList1)

key_label2 = extract_json_from_response(response2)
scenarioList2 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label2)
print("Scenario 2 (Left Turn vs. Left Turn):", scenarioList2)

key_label3 = extract_json_from_response(response3)
scenarioList3 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label3)
print("Scenario 3 (Left Turn vs. Right Turn):", scenarioList3)

key_label4 = extract_json_from_response(response4)
scenarioList4 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label4)
print("Scenario 4 (Left Turn vs. Straight):", scenarioList4)

key_label5 = extract_json_from_response(response5)
scenarioList5 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label5)
print("Scenario 5 (Right Turn vs. Left Turn):", scenarioList5)

key_label6 = extract_json_from_response(response6)
scenarioList6 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label6)
print("Scenario 6 (Right Turn vs. Right Turn):", scenarioList6)

key_label7 = extract_json_from_response(response7)
scenarioList7 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label7)
print("Scenario 7 (Straight vs. Left Turn):", scenarioList7)

key_label8 = extract_json_from_response(response8)
scenarioList8 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label8)
print("Scenario 8 (Straight vs. Right Turn):", scenarioList8)

key_label9 = extract_json_from_response(response9)
scenarioList9 = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label9)
print("Scenario 9 (Straight vs. Straight):", scenarioList9)
'''






key_label = extract_json_from_response(response1)

scenarioList = OpenDriveMapSelector.identify_junction_scenarios_optimized(tracks_meta_df, key_label)
print(scenarioList)

fictive_ego_list_sampled = []
fictive_target_dicts_sampled = {}

for scenario in scenarioList:
    ego_id = scenario[0]
    target_ids = scenario[1]
    begin_frame = scenario[2]
    end_frame = scenario[3]

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
preview_scenario(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, animation_holder, "inD",dataset_load)
#preview_scenario_new(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, animation_holder, "inD")