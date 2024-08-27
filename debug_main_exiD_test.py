
import re
import csv
import scenario_mining.exiD_scenario_mining.playground1_18 as playground1_18
import scenario_mining.exiD_scenario_mining.playground19_38 as playground19_38
import scenario_mining.exiD_scenario_mining.playground39_52 as playground39_52
import scenario_mining.exiD_scenario_mining.playground53_60 as playground53_60
import scenario_mining.exiD_scenario_mining.playground61_72 as playground61_72
import scenario_mining.exiD_scenario_mining.playground73_77 as playground73_77
import scenario_mining.exiD_scenario_mining.playground78_92 as playground78_92
import scenario_mining.exiD_scenario_mining.scenario_identification as scenario_identification
from NLP.Scenario_Description_Understand import *
import streamlit as st
import pandas as pd
from GUI.Web_Sidebar import *
from utils.helper_original_scenario import generate_xosc
import time
import sympy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from utils.prompt_engineering import *
from NLP.Scenario_Description_Understand import *
from scenario_mining.activity_identification import *
from scenario_mining.scenario_identification import *
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
from shapely.geometry import Polygon
import shapely.wkt
import pickle
import json
from shapely.geometry import mapping
import json
from shapely.geometry import shape, Polygon
from scenario_mining.exiD_scenario_mining.scenario_identification import *


file_path = '39_tracks.csv'

scenario_identification = ScenarioIdentification()

json_data,updated_tracks_df =  scenario_identification.select_playground(file_path)

def get_json() :
    return json_data

'''
response = """
{
    'Ego Vehicle': 
    {
        'Ego ramp activity': ['KeepRamp']
    },
    'Target Vehicle #1': 
    {
        'Target ramp activity': ['OnRamp']
    }
}
"""

response = """
{
    'Ego Vehicle': 
    {
        'Ego ramp activity': ['OffRamp']
    },
    'Target Vehicle #1': 
    {
        'Target ramp activity': ['KeepRamp']
    }
}
"""
# Ego vehicle was trying to off-ramp; However, the target vehicle driving parallelly.
'''

response = """
{'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
    'Ego lateral activity': ['off-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'adjacent lane': ['right adjacent lane']}, 
    'Target end position': {'rear': ['left rear']}, 
    'Target behavior': {'target longitudinal activity': ['NA'], 
    'target lateral activity': ['follow lane']}}}
    """

'''
# Ego vehicle was trying to on-ramp; The ego vehicle has to watch out the vehicles driving on the highway
response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
    'Ego lateral activity': ['on-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'rear': ['left rear']}, 
    'Target end position': {'same lane': ['behind']}, 
    'Target behavior': {'target longitudinal activity': ['NA'], 
    'target lateral activity': ['follow lane']}}}"""
# for cut in
'''
'''
# 3240 frames with ego 141, target 145
response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
    'Ego lateral activity': ['on-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'rear': ['left rear']}, 
    'Target end position': {'same lane': ['front']}, 
    'Target behavior': {'target longitudinal activity': ['NA'], 
    'target lateral activity': ['follow lane']}}}"""
'''
'''
response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 

  'Ego lateral activity': ['follow lane']}, 

  'Target Vehicle #1': {'Target start position': {'rear': ['left rear']}, 

  'Target end position': {'same lane': ['front']}, 

  'Target behavior': {'target longitudinal activity': ['NA'], 

  'target lateral activity': ['follow lane']}}}"""
'''

'''
response = """
{
    'Ego Vehicle': 
    {
        'Ego longitudinal activity': ['keep velocity'],
        'Ego lateral activity': ['follow lane'],
        'Ego ramp activity': ['KeepRamp']
    },
    'Target Vehicle #1': 
    {
        'Target start position': {'adjacent lane': ['left adjacent lane']},
        'Target end position': {'same lane': ['front']},
        'Target behavior': {'target longitudinal activity': ['acceleration'], 'target lateral activity': ['lane change right'], 'target ramp activity': ['KeepRamp']}
    }
}
"""

# for cut out
response = """
{
    'Ego Vehicle': 
    {
        'Ego longitudinal activity': ['keep velocity'],
        'Ego lateral activity': ['follow lane'],
        'Ego ramp activity': ['KeepRamp']
    },
    'Target Vehicle #1': 
    {
        'Target start position': {'same lane': ['front']},
        'Target end position': {'adjacent lane': ['left adjacent lane']},
        'Target behavior': {'target longitudinal activity': ['acceleration'], 'target lateral activity': ['lane change left'], 'target ramp activity': ['KeepRamp']}
    }
}
"""

# for following
response = """
{
    'Ego Vehicle': 
    {
        'Ego longitudinal activity': ['keep velocity'],
        'Ego lateral activity': ['follow lane'],
        'Ego ramp activity': ['KeepRamp']
    },
    'Target Vehicle #1': 
    {
        'Target start position': {'same lane': ['front']},
        'Target end position': {'same lane': ['front']},
        'Target behavior': {'target longitudinal activity': ['keep velocity'], 'target lateral activity': ['follow lane'], 'target ramp activity': ['KeepRamp']}
    }
}
"""
'''



dataset_option = "exitD"
'''
dataset_load = './39_updated_tracks.csv'
'''
key_label = extract_json_from_response(response)
print('Response of the LLM:')
print(key_label)
'''
tracks_original = pd.read_csv(dataset_load) 
'''   
'''
tracks_original =  pd.read_csv(file_path) 

updated_tracks_df = pd.DataFrame(updated_tracks)
tracks_combined = pd.concat([tracks_original, updated_tracks_df], ignore_index=True)
'''

progress_bar = st.progress(0)




longActDict, latActDict, interactIdDict = main_fcn_veh_activity(updated_tracks_df, progress_bar,dataset_option,file_path)
#print(longActDict, latActDict, interactIdDict)
scenarioList = scenario_identification.mainFunctionScenarioIdentification_ExitD(updated_tracks_df, key_label, latActDict, longActDict, interactIdDict, progress_bar,file_path)
print(scenarioList)     



#scenarioList = [[81, [82], 2621, 2992], [164, [166], 6365, 6777], [886, [885], 32879, 33252]]


fictive_ego_list_sampled = []
fictive_target_dicts_sampled = {}
reminder_holder = st.empty()
animation_holder = st.empty()

for scenario in scenarioList:
    ego_id = scenario[0]
    target_ids = scenario[1]
    begin_frame = scenario[2]
    end_frame = scenario[3]

    # Make sure target_ids is a list
    if isinstance(target_ids, int):
        target_ids = [target_ids]

    # Get ego vehicle data
    egoVehData = updated_tracks_df[(updated_tracks_df['trackId'] == ego_id) & 
                                 (updated_tracks_df['frame'] >= begin_frame) & 
                                 (updated_tracks_df['frame'] <= end_frame)].reset_index(drop=True)
    fictive_ego_list_sampled.append(egoVehData)

    # Get target vehicle data
    tgtVehsData = []
    for tgt_id in target_ids:
        tgtVehData = updated_tracks_df[(updated_tracks_df['trackId'] == tgt_id) & 
                                     (updated_tracks_df['frame'] >= begin_frame) & 
                                     (updated_tracks_df['frame'] <= end_frame)].reset_index(drop=True)
        tgtVehsData.append(tgtVehData)
    
    fictive_target_dicts_sampled[ego_id] = tgtVehsData

# Now call the preview function
preview_scenario(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, animation_holder, "exitD",file_path,json_data)
