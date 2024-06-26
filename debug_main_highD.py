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




dataset_option = 'highD'
metric_option = {"Time-Scale": ["Encroachment Time (ET)", "Post-encroachment Time (PET)", "Potential Time To Collision (PTTC)", \
                           "Time Exposed TTC (TET)", \
                            "Time Integrated TTC (TIT)", "Time To Closest Encounter (TTCE)", "Time To Brake (TTB)",\
                                "Time To Kickdown (TTK)", "Time To Steer (TTS)", "Time To Collision (TTC)",\
                                    "Time Headway (THW)"]}
metric_suboption = "Time To Collision (TTC)" 

dataset_load = './36_tracks.csv'


reminder_holder = st.empty()
animation_holder = st.empty()

response1 = """
{
    "Ego Vehicle": {"Ego longitudinal activity": ["keep velocity"], "Ego lateral activity": ["follow lane"]},
    "Target Vehicle #1": {
        "Target start position": {"adjacent lane": ["left adjacent lane"]},
        "Target end position": {"same lane": ["front"]},
        "Target behavior": {
            "target longitudinal activity": ["acceleration"],
            "target lateral activity": ["lane change right"]
        }
    }
}
"""

progress_bar = st.progress(0)

key_label = extract_json_from_response(response1)

print('Response of the LLM:')
print(key_label)
# Check if key_label is valid
check_key_label = validate_scenario(key_label, reminder_holder)


tracks_original = pd.read_csv(dataset_load)    
'''
longActDict, latActDict, interactIdDict = main_fcn_veh_activity(tracks_original, progress_bar,dataset_option)

scenarioList = mainFunctionScenarioIdentification(tracks_original, key_label, latActDict, longActDict, interactIdDict, progress_bar)
print("The following scenarios are in the scenario pool:")
print(scenarioList)
'''
scenarioList = [[109, [108], 1014, 1151], [153, [150], 1603, 1715], [172, [173], 1888, 1988], [220, [219], 2415, 2456], [222, [223], 2508, 2586], [300, [296], 3218, 3253], [312, [310], 3275, 3284], [320, [319], 3124, 3276], [353, [346], 3611, 3631], [381, [371], 3960, 4087], [394, [396], 4143, 4164], [474, [476], 5187, 5234], [514, [505], 5658, 5752], [538, [537], 5807, 5841], [540, [551], 6111, 6132], [698, [699], 8011, 8072], [822, [821], 9262, 9323], [943, [939], 10844, 10895], [967, [969], 11438, 11451], [981, [977], 11473, 11557], [1051, [1052], 12327, 12457], [1166, [1162], 13742, 13761], [1246, [1240], 14897, 15088], [1345, [1346], 16318, 16355], [1373, [1370], 16492, 16567], [1379, [1383], 16763, 16804], [1442, [1438], 17334, 17688], [1576, [1575], 18947, 19207], [1818, [1819], 21961, 22085], [1940, [1935], 23431, 23618], [1948, [1947], 23596, 23692], [1995, [1991], 24644, 24720], [2096, [2100], 25606, 25657], [2100, [2098], 25400, 25482], [2119, [2121], 25948, 25960], [2183, [2178], 26618, 26840], [2196, [2195], 26769, 26873], [2278, [2267], 27586, 27651], [2303, [2297], 27953, 28067]]

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
    egoVehData = tracks_original[(tracks_original['id'] == ego_id) & 
                                 (tracks_original['frame'] >= begin_frame) & 
                                 (tracks_original['frame'] <= end_frame)].reset_index(drop=True)
    fictive_ego_list_sampled.append(egoVehData)

    # Get target vehicle data
    tgtVehsData = []
    for tgt_id in target_ids:
        tgtVehData = tracks_original[(tracks_original['id'] == tgt_id) & 
                                     (tracks_original['frame'] >= begin_frame) & 
                                     (tracks_original['frame'] <= end_frame)].reset_index(drop=True)
        tgtVehsData.append(tgtVehData)
    
    fictive_target_dicts_sampled[ego_id] = tgtVehsData


preview_scenario(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, animation_holder, dataset_option,dataset_load)