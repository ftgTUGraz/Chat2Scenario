
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
matplotlib.use('TkAgg')  # 或 'Qt5Agg', 'GTK3Agg', 'WXAgg' 等，取决于你的系统配置
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
select_playground(file_path)

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
    'Target end position': {'rear': ['right rear']}, 
    'Target behavior': {'target longitudinal activity': ['NA'], 
    'target lateral activity': ['follow lane']}}}
    """

# Ego vehicle was trying to on-ramp; The ego vehicle has to watch out the vehicles driving on the highway
response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
    'Ego lateral activity': ['on-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'rear': ['left rear']}, 
    'Target end position': {'same lane': ['behind']}, 
    'Target behavior': {'target longitudinal activity': ['NA'], 
    'target lateral activity': ['follow lane']}}}"""
# for cut in


# 3240 frames with ego 141, target 145
response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
    'Ego lateral activity': ['on-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'rear': ['left rear']}, 
    'Target end position': {'same lane': ['front']}, 
    'Target behavior': {'target longitudinal activity': ['NA'], 
    'target lateral activity': ['follow lane']}}}"""

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
dataset_load = './39_updated_tracks.csv'
key_label = extract_json_from_response(response)
print('Response of the LLM:')
print(key_label)
tracks_original = pd.read_csv(dataset_load)    
progress_bar = st.progress(0)
longActDict, latActDict, interactIdDict = main_fcn_veh_activity(tracks_original, progress_bar,dataset_option)
#print(longActDict, latActDict, interactIdDict)
scenarioList = scenario_identification.mainFunctionScenarioIdentification_ExitD(tracks_original, key_label, latActDict, longActDict, interactIdDict, progress_bar)
print(scenarioList)                        
