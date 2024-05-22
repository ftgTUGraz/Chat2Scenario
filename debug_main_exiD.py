
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

def get_utm_origin(recordings_meta_file):
    """
    从XX_recordingsMeta.csv文件中提取xUtmOrigin和yUtmOrigin值。
    
    参数:
    recordings_meta_file (str): XX_recordingsMeta.csv文件路径
    
    返回:
    tuple: (xUtmOrigin, yUtmOrigin)
    """
    with open(recordings_meta_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            x_utm_origin = float(row['xUtmOrigin'])
            y_utm_origin = float(row['yUtmOrigin'])
            return x_utm_origin, y_utm_origin
    raise ValueError("xUtmOrigin和yUtmOrigin在recordings meta文件中未找到")

def select_playground(file_path):
    """
    根据文件名中的数字选择对应的playground模块并执行相应的操作。

    参数:
    ----------
    file_path (str): 包含数字索引的文件路径，用于决定处理逻辑。

    返回:
    ----------
    None
    """
    # 从文件名中提取数字
    match = re.search(r'\d+', file_path)
    if match:
        index = int(match.group(0))
        # 根据不同的数字范围选择对应的playground模块
        if 0 <= index <= 18:
            # 获取playground1-18的xUtmOrigin和yUtmOrigin
            if 0 <= index <= 9:
                recordings_meta_file_1_18 = f'./0{index}_recordingMeta.csv'
            else:  
                recordings_meta_file_1_18 = f'./{index}_recordingMeta.csv'  
            x_utm_origin_1_18, y_utm_origin_1_18 = get_utm_origin(recordings_meta_file_1_18)

            # 提取playground1-18 KML文件中的多边形
            onramp_polygon_1_18 = playground1_18.extract_polygon_from_kml(
                './scenario_mining/exiD_scenario_mining/playground1-18_lane-5_OnRamp.kml',
                ['lane-8.1', 'lane-8.2', 'lane-6.2', 'lane-7.1', 'lane-8.1'],
                x_utm_origin_1_18,
                y_utm_origin_1_18
            )
            offramp_polygon_1_18 = playground1_18.extract_polygon_from_kml(
                './scenario_mining/exiD_scenario_mining/playground1-18_lane4_OffRamp.kml',
                ['lane6.1', 'lane6.2', 'lane6.3', 'lane7.2', 'lane7.1', 'lane6.1'],
                x_utm_origin_1_18,
                y_utm_origin_1_18
            )
            lanes_polygons_1_18 = [
                (1, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane1.5', 'lane1.6', 'lane1.7', 'lane1.8', 
                    'lane2.8', 'lane2.7', 'lane2.6', 'lane2.5', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (2, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane2.5', 'lane2.6', 'lane2.7', 'lane2.8', 
                    'lane3.8', 'lane3.7', 'lane3.6', 'lane3.5', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (3, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane3.kml', [
                    'lane4.1', 'lane4.2', 'lane4.3', 'lane4.4', 'lane4.5', 'lane4.6', 'lane4.7', 
                    'lane5.7', 'lane5.6', 'lane5.5', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.1', 'lane4.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (4, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane4.kml', [
                    'lane6.1', 'lane6.2', 'lane6.3', 'lane6.4', 'lane6.5', 'lane6.6', 'lane7.5', 'lane7.4', 
                    'lane7.3', 'lane7.2', 'lane7.1', 'lane6.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (4, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane4_OffRamp.kml', [
                    'lane6.1', 'lane6.2', 'lane6.3', 'lane7.2', 'lane7.1', 'lane6.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (-1, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane-1.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-2.5', 'lane-1.5', 'lane-1.4', 
                    'lane-1.3', 'lane-1.2', 'lane-1.1', 'lane-2.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (-2, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane-2.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 
                    'lane-2.5', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-3.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (-3, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane-3.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-3.3', 'lane-3.2', 'lane-3.1', 'lane-4.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (-4, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane-4.kml', [
                    'lane-6.1', 'lane-6.2', 'lane-6.3', 'lane-6.4', 'lane-6.5', 'lane-3.6', 'lane-3.5', 
                    'lane-3.4', 'lane-5.3', 'lane-5.2', 'lane-5.1', 'lane-6.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (-5, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane-5.kml', [
                    'lane-8.1', 'lane-8.2', 'lane-8.3', 'lane-6.4', 'lane-6.3', 'lane-6.2', 'lane-7.1', 'lane-8.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
                (-5, playground1_18.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground1-18_lane-5_OnRamp.kml', [
                    'lane-8.1', 'lane-8.2', 'lane-6.2', 'lane-7.1', 'lane-8.1'
                ], x_utm_origin_1_18, y_utm_origin_1_18)),
            ]

            # 更新playground1-18的轨迹数据
            if 0 <= index <= 9:
                
                input_file_1_18 = f'0{index}_tracks.csv'
                output_file_1_18 = f'0{index}_updated_tracks.csv'
            else :
                input_file_1_18 = f'{index}_tracks.csv'
                output_file_1_18 = f'{index}_updated_tracks.csv'
            playground1_18.update_track_data(input_file_1_18, output_file_1_18, onramp_polygon_1_18, offramp_polygon_1_18, lanes_polygons_1_18)

            # 创建并绘制playground1-18的多边形
            kml_files_and_names_1_18 = [
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane1.5',
                    'lane1.6', 'lane1.7', 'lane1.8', 'lane2.8', 'lane2.7',
                    'lane2.6', 'lane2.5', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane2.5',
                    'lane2.6', 'lane2.7', 'lane2.8', 'lane3.8', 'lane3.7',
                    'lane3.6', 'lane3.5', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane3.kml', [
                    'lane4.1', 'lane4.2', 'lane4.3', 'lane4.4', 'lane4.5', 'lane4.6', 'lane4.7',
                    'lane5.7', 'lane5.6', 'lane5.5', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.1', 'lane4.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane4.kml', [
                    'lane6.1', 'lane6.2', 'lane6.3', 'lane6.4', 'lane6.5', 'lane6.6',
                    'lane7.5', 'lane7.4', 'lane7.3', 'lane7.2', 'lane7.1', 'lane6.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane4_OffRamp.kml', [
                    'lane6.1', 'lane6.2', 'lane6.3', 'lane7.2', 'lane7.1', 'lane6.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane-1.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-2.5',
                    'lane-1.5', 'lane-1.4', 'lane-1.3', 'lane-1.2', 'lane-1.1', 'lane-2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane-2.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7',
                    'lane-2.5', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane-3.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-3.3', 'lane-3.2', 'lane-3.1', 'lane-4.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane-4.kml', [
                    'lane-6.1', 'lane-6.2', 'lane-6.3', 'lane-6.4', 'lane-6.5',
                    'lane-3.6', 'lane-3.5', 'lane-3.4', 'lane-5.3', 'lane-5.2', 'lane-5.1', 'lane-6.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane-5.kml', [
                    'lane-8.1', 'lane-8.2', 'lane-8.3', 'lane-6.4', 'lane-6.3', 'lane-6.2',
                    'lane-7.1', 'lane-8.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground1-18_lane-5_OnRamp.kml', [
                    'lane-8.1', 'lane-8.2', 'lane-6.2', 'lane-7.1', 'lane-8.1'
                ])
            ]

            labels_1_18 = [
                'lane 1', 'lane 2', 'lane 3', 'lane 4', 'lane 4 OffRamp',
                'lane -1', 'lane -2', 'lane -3', 'lane -4', 'lane -5', 'lane 5 OnRamp'
            ]

            colors_1_18 = [
                'red', 'blue', 'green', 'purple', 'orange', 
                'cyan', 'magenta', 'yellow', 'brown', 'pink', 'grey'
            ]
            playground1_18.create_polygon_and_plot(kml_files_and_names_1_18, labels_1_18, colors_1_18, x_utm_origin_1_18, y_utm_origin_1_18)
        elif 19 <= index <= 38:

            # 获取playground19-38的xUtmOrigin和yUtmOrigin
            recordings_meta_file_19_38 =  f'./{index}_recordingMeta.csv'  
            x_utm_origin_19_38, y_utm_origin_19_38 = get_utm_origin(recordings_meta_file_19_38)

            # 提取playground19-38 KML文件中的多边形
            onramp_polygons_19_38 = {
                'playground19-38_lane-4_OnRamp': (playground19_38.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground19-38_lane-4_OnRamp.kml',
                    ['lane-5.4', 'lane-5.5', 'lane-5.6', 'lane-5.7', 'lane-6.7', 'lane-6.6', 'lane-6.5', 'lane-6.4', 'lane-5.4'],
                    x_utm_origin_19_38,
                    y_utm_origin_19_38
                ), -4),
                'playground19-38_lane4_OnRamp': (playground19_38.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground19-38_lane4_OnRamp.kml',
                    ['lane5.2', 'lane5.1', 'lane5.0', 'lane6.0', 'lane6.1', 'lane6.2', 'lane5.2'],
                    x_utm_origin_19_38,
                    y_utm_origin_19_38
                ), 4)
            }

            offramp_polygons_19_38 = {
                'playground19-38_lane-5_OffRamp': (playground19_38.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground19-38_lane-5_OffRamp.kml',
                    ['lane6.1', 'lane6.2', 'lane6.3', 'lane7.3', 'lane7.2', 'lane7.1', 'lane6.1'],
                    x_utm_origin_19_38,
                    y_utm_origin_19_38
                ), -5),
                'playground19-38_lane4_OffRamp': (playground19_38.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground19-38_lane4_OffRamp.kml',
                    ['lane5.5', 'lane5.4', 'lane5.3', 'lane6.3', 'lane6.4', 'lane6.5', 'lane5.5'],
                    x_utm_origin_19_38,
                    y_utm_origin_19_38
                ), 4)
            }

            lanes_polygons_19_38 = [
                (1, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane1.kml', [
                    'lane1.4', 'lane1.3', 'lane1.2', 'lane1.1', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.4'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (2, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane2.1'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (3, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane3.kml', [
                    'lane4.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane5.1', 'lane5.2', 'lane5.3', 'lane5.4', 'lane4.4'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (4, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane4.kml', [
                    'lane5.5', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.1', 'lane6.0', 'lane6.1', 'lane6.2', 'lane6.3', 'lane6.4', 'lane5.5'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (-1, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (-2, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1', 'lane-2.1'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (-3, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane-3.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1', 'lane-4.1'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
                (-4, playground19_38.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground19-38_lane-4.kml', [
                    'lane-5.1', 'lane-5.2', 'lane-5.3', 'lane-5.4', 'lane-5.5', 'lane-5.6', 'lane-5.7', 'lane-6.7', 'lane-6.6', 'lane-6.5', 'lane-6.4', 'lane-6.3', 'lane-6.2', 'lane-6.1', 'lane-5.1'
                ], x_utm_origin_19_38, y_utm_origin_19_38)),
            ]

            # 更新playground19-38的轨迹数据
            input_file_19_38 = f'{index}_tracks.csv'
            output_file_19_38 = f'{index}_updated_tracks.csv'
            playground19_38.update_track_data(input_file_19_38, output_file_19_38, onramp_polygons_19_38, offramp_polygons_19_38, lanes_polygons_19_38)

            # 创建并绘制playground19-38的多边形
            kml_files_and_names_19_38 = [
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane1.kml', [
                    'lane1.4', 'lane1.3', 'lane1.2', 'lane1.1', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.4'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane3.kml', [
                    'lane4.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane5.1', 'lane5.2', 'lane5.3', 'lane5.4', 'lane4.4'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane4.kml', [
                    'lane5.5', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.1', 'lane6.0', 'lane6.1', 'lane6.2', 'lane6.3', 'lane6.4', 'lane5.5'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane4_OffRamp.kml', [
                    'lane5.5', 'lane5.4', 'lane5.3', 'lane6.3', 'lane6.4', 'lane6.5', 'lane5.5'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane4_OnRamp.kml', [
                    'lane5.2', 'lane5.1', 'lane5.0', 'lane6.0', 'lane6.1', 'lane6.2', 'lane5.2'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1', 'lane-2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane-3.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1', 'lane-4.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane-4.kml', [
                    'lane-5.1', 'lane-5.2', 'lane-5.3', 'lane-5.4', 'lane-5.5', 'lane-5.6', 'lane-5.7', 'lane-6.7', 'lane-6.6', 'lane-6.5', 'lane-6.4', 'lane-6.3', 'lane-6.2', 'lane-6.1', 'lane-5.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane-5_OffRamp.kml', [
                    'lane-6.1', 'lane-6.2', 'lane-6.3', 'lane-7.3', 'lane-7.2', 'lane-7.1', 'lane-6.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground19-38_lane-4_OnRamp.kml', [
                    'lane-5.4', 'lane-5.5', 'lane-5.6', 'lane-5.7', 'lane-6.7', 'lane-6.6', 'lane-6.5', 'lane-6.4', 'lane-5.4'
                ])
            ]

            labels_19_38 = [
                'lane 1', 'lane 2', 'lane 3', 'lane 4', 'lane 4 OffRamp',
                'lane 4 OnRamp', 'lane -1', 'lane -2', 'lane -3', 'lane -4', 'lane -5 OffRamp', 'lane -4 OnRamp'
            ]

            colors_19_38 = [
                'red', 'blue', 'green', 'purple', 'orange', 
                'cyan', 'magenta', 'yellow', 'brown', 'pink', 'grey', 'black'
            ]
        
            playground19_38.create_polygon_and_plot(kml_files_and_names_19_38, labels_19_38, colors_19_38, x_utm_origin_19_38, y_utm_origin_19_38)
        elif 39 <= index <= 52:


            # 获取playground39-52的xUtmOrigin和yUtmOrigin
            recordings_meta_file_39_52 = f'./{index}_recordingMeta.csv' 
            x_utm_origin_39_52, y_utm_origin_39_52 = get_utm_origin(recordings_meta_file_39_52)

            # 提取playground39-52 KML文件中的多边形
            onramp_polygons_39_52 = {
                'playground39-52_lane-3_OnRamp': (playground39_52.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground39-52_lane-3_OnRamp.kml',
                    ['lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.3'],
                    x_utm_origin_39_52,
                    y_utm_origin_39_52
                ), -3)
            }

            offramp_polygons_39_52 = {
                'playground39-52_lane3_OffRamp': (playground39_52.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground39-52_lane3_OffRamp.kml',
                    ['lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane3.3'],
                    x_utm_origin_39_52,
                    y_utm_origin_39_52
                ), 3)
            }

            lanes_polygons_39_52 = [
                (1, playground39_52.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground39-52_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane1.1'
                ], x_utm_origin_39_52, y_utm_origin_39_52)),
                (2, playground39_52.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground39-52_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane2.1'
                ], x_utm_origin_39_52, y_utm_origin_39_52)),
                (3, playground39_52.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground39-52_lane3.kml', [
                    'lane3.2', 'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.2'
                ], x_utm_origin_39_52, y_utm_origin_39_52)),
                (-1, playground39_52.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground39-52_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ], x_utm_origin_39_52, y_utm_origin_39_52)),
                (-2, playground39_52.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground39-52_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-2.1'
                ], x_utm_origin_39_52, y_utm_origin_39_52)),
                (-3, playground39_52.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground39-52_lane-3.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ], x_utm_origin_39_52, y_utm_origin_39_52))
            ]

            # 更新playground39-52的轨迹数据
            input_file_39_52 = f'{index}_tracks.csv'
            output_file_39_52 = f'{index}_updated_tracks.csv'
            playground39_52.update_track_data(input_file_39_52, output_file_39_52, onramp_polygons_39_52, offramp_polygons_39_52, lanes_polygons_39_52)

            # 创建并绘制playground39-52的多边形
            kml_files_and_names_39_52 = [
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane3.kml', [
                    'lane3.2', 'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.2'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane3_OffRamp.kml', [
                    'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane3.3'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane-3.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground39-52_lane-3_OnRamp.kml', [
                    'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.3'
                ])
            ]

            labels_39_52 = [
                'lane 1', 'lane 2', 'lane 3', 'lane 3 OffRamp', 'lane -1', 'lane -2', 'lane -3', 'lane 3 OnRamp'
            ]

            colors_39_52 = [
                'red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow'
            ]

            playground39_52.create_polygon_and_plot(kml_files_and_names_39_52, labels_39_52, colors_39_52, x_utm_origin_39_52, y_utm_origin_39_52)

        elif 53 <= index <= 60:


            # 获取playground53-60的xUtmOrigin和yUtmOrigin
            recordings_meta_file_53_60 = f'./{index}_recordingMeta.csv' 
            x_utm_origin_53_60, y_utm_origin_53_60 = get_utm_origin(recordings_meta_file_53_60)

            # 提取playground53-60 KML文件中的多边形
            onramp_polygons_53_60 = {
                'playground53-60_lane-3_OnRamp': (playground53_60.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground53-60_lane-3_OnRamp.kml',
                    ['lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.2'],
                    x_utm_origin_53_60,
                    y_utm_origin_53_60
                ), -3)
            }

            offramp_polygons_53_60 = {
                'playground53-60_lane3_OffRamp': (playground53_60.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground53-60_lane3_OffRamp.kml',
                    ['lane3.2', 'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane4.2', 'lane3.2'],
                    x_utm_origin_53_60,
                    y_utm_origin_53_60
                ), 3)
            }

            lanes_polygons_53_60 = [
                (1, playground53_60.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground53-60_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane1.5', 'lane2.5', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ], x_utm_origin_53_60, y_utm_origin_53_60)),
                (2, playground53_60.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground53-60_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane2.5', 'lane3.5', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ], x_utm_origin_53_60, y_utm_origin_53_60)),
                (3, playground53_60.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground53-60_lane3.kml', [
                    'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.1'
                ], x_utm_origin_53_60, y_utm_origin_53_60)),
                (-1, playground53_60.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground53-60_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-1.5', 'lane-2.5', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ], x_utm_origin_53_60, y_utm_origin_53_60)),
                (-2, playground53_60.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground53-60_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-2.5', 'lane-3.5', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1'
                ], x_utm_origin_53_60, y_utm_origin_53_60)),
                (-3, playground53_60.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground53-60_lane-3.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ], x_utm_origin_53_60, y_utm_origin_53_60))
            ]

            # 更新playground53-60的轨迹数据
            input_file_53_60 = f'{index}_tracks.csv'
            output_file_53_60 = f'{index}_updated_tracks.csv'
            playground53_60.update_track_data(input_file_53_60, output_file_53_60, onramp_polygons_53_60, offramp_polygons_53_60, lanes_polygons_53_60)

            # 创建并绘制playground53-60的多边形
            kml_files_and_names_53_60 = [
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane1.5', 'lane2.5', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane2.5', 'lane3.5', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane3.kml', [
                    'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane-3_OnRamp.kml', [
                    'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.2'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-1.5', 'lane-2.5', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-2.5', 'lane-3.5', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane-3.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground53-60_lane-3_OnRamp.kml', [
                    'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.2'
                ])
            ]

            labels_53_60 = [
                'lane 1', 'lane 2', 'lane 3', 'lane -3 OnRamp', 'lane -1', 'lane -2', 'lane -3', 'lane 3 OnRamp'
            ]

            colors_53_60 = [
                'red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow'
            ]

            playground53_60.create_polygon_and_plot(kml_files_and_names_53_60, labels_53_60, colors_53_60, x_utm_origin_53_60, y_utm_origin_53_60)


        elif 61 <= index <= 72:

            # 获取playground61-72的xUtmOrigin和yUtmOrigin
            recordings_meta_file_61_72 = f'./{index}_recordingMeta.csv'  
            x_utm_origin_61_72, y_utm_origin_61_72 = get_utm_origin(recordings_meta_file_61_72)

            # 提取playground61-72 KML文件中的多边形
            onramp_polygons_61_72 = {
                'playground61-72_lane-4_OnRamp': (playground61_72.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground61-72_lane-4_OnRamp.kml',
                    ['lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1'],
                    x_utm_origin_61_72,
                    y_utm_origin_61_72
                ), -4)
            }

            offramp_polygons_61_72 = {
                'playground61-72_lane5_OffRamp': (playground61_72.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground61-72_lane5_OffRamp.kml',
                    ['lane5.2', 'lane5.3', 'lane5.4', 'lane5.5', 'lane5.6', 'lane5.7', 'lane6.7', 'lane6.6', 'lane6.5', 'lane6.4', 'lane6.3', 'lane6.2'],
                    x_utm_origin_61_72,
                    y_utm_origin_61_72
                ), 5)
            }

            lanes_polygons_61_72 = [
                (1, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (2, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (3, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane3.kml', [
                    'lane3.1', 'lane3.2', 'lane3.3', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (4, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane4.kml', [
                    'lane4.1', 'lane4.2', 'lane4.3', 'lane4.4', 'lane4.5', 'lane4.6', 'lane5.5', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.1', 'lane4.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (5, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane5.kml', [
                    'lane5.1', 'lane5.2', 'lane5.3', 'lane5.4', 'lane5.5', 'lane5.6', 'lane5.7', 'lane6.7', 'lane6.6', 'lane6.5', 'lane6.4', 'lane6.3', 'lane6.2', 'lane6.1', 'lane5.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (-1, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (-2, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1', 'lane-2.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (-3, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane-3.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72)),
                (-4, playground61_72.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground61-72_lane-4.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-4.5', 'lane-4.6', 'lane-4.7', 'lane-5.7', 'lane-5.6', 'lane-5.5', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1'
                ], x_utm_origin_61_72, y_utm_origin_61_72))
            ]

            # 更新playground61-72的轨迹数据
            input_file_61_72 = f'{index}_tracks.csv'
            output_file_61_72 = f'{index}_updated_tracks.csv'
            playground61_72.update_track_data(input_file_61_72, output_file_61_72, onramp_polygons_61_72, offramp_polygons_61_72, lanes_polygons_61_72)

            # 创建并绘制playground61-72的多边形
            kml_files_and_names_61_72 = [
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane3.kml', [
                    'lane3.1', 'lane3.2', 'lane3.3', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane4.kml', [
                    'lane4.1', 'lane4.2', 'lane4.3', 'lane4.4', 'lane4.5', 'lane4.6', 'lane5.5', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.1', 'lane4.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane5.kml', [
                    'lane5.1', 'lane5.2', 'lane5.3', 'lane5.4', 'lane5.5', 'lane5.6', 'lane5.7', 'lane6.7', 'lane6.6', 'lane6.5', 'lane6.4', 'lane6.3', 'lane6.2', 'lane6.1', 'lane5.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane5_OffRamp.kml', [
                    'lane5.2', 'lane5.3', 'lane5.4', 'lane5.5', 'lane5.6', 'lane5.7', 'lane6.7', 'lane6.6', 'lane6.5', 'lane6.4', 'lane6.3', 'lane6.2', 'lane5.2'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1', 'lane-2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane-3.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane-4.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-4.5', 'lane-4.6', 'lane-4.7', 'lane-5.7', 'lane-5.6', 'lane-5.5', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground61-72_lane-4_OnRamp.kml', [
                    'lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1'
                ])
            ]

            labels_61_72 = [
                'lane 1', 'lane 2', 'lane 3', 'lane 4', 'lane 5', 'lane 5 OffRamp', 'lane -1', 'lane -2', 'lane -3', 'lane -4', 'lane -4 OnRamp'
            ]

            colors_61_72 = [
                'red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'brown', 'pink', 'grey'
            ]

            playground61_72.create_polygon_and_plot(kml_files_and_names_61_72, labels_61_72, colors_61_72, x_utm_origin_61_72, y_utm_origin_61_72)



        elif 73 <= index <= 77:

            # 获取playground73-77的xUtmOrigin和yUtmOrigin
            recordings_meta_file_73_77 = f'./{index}_recordingMeta.csv'  
            x_utm_origin_73_77, y_utm_origin_73_77 = get_utm_origin(recordings_meta_file_73_77)

            # 提取playground73-77 KML文件中的多边形
            onramp_polygons_73_77 = {
                'playground73-77_lane-3_2_OnRamp': (playground73_77.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground73-77_lane-3_2_OnRamp.kml',
                    ['lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-3.8', 'lane-3.9', 'lane-4.9', 'lane-4.8', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3'],
                    x_utm_origin_73_77,
                    y_utm_origin_73_77
                ), -3)
            }

            lanes_polygons_73_77 = [
                (1, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77)),
                (2, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.5', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77)),
                (3, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane3.kml', [
                    'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77)),
                (-1, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77)),
                (-2, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77)),
                (-3, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane-3_1.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77)),
                (-3, playground73_77.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground73-77_lane-3_2.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-3.8', 'lane-3.9', 'lane-4.9', 'lane-4.8', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ], x_utm_origin_73_77, y_utm_origin_73_77))
            ]

            # 更新playground73-77的轨迹数据
            input_file_73_77 = f'{index}_tracks.csv'
            output_file_73_77 = f'{index}_updated_tracks.csv'
            playground73_77.update_track_data(input_file_73_77, output_file_73_77, onramp_polygons_73_77, {}, lanes_polygons_73_77)

            # 创建并绘制playground73-77的多边形
            kml_files_and_names_73_77 = [
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane1.kml', [
                    'lane1.1', 'lane1.2', 'lane1.3', 'lane1.4', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.1', 'lane1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane2.kml', [
                    'lane2.1', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.5', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.1', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane3.kml', [
                    'lane3.1', 'lane3.2', 'lane3.3', 'lane3.4', 'lane4.3', 'lane4.2', 'lane4.1', 'lane3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane-1.kml', [
                    'lane-1.1', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.1', 'lane-1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane-2.kml', [
                    'lane-2.1', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane-3_1.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane-3_2.kml', [
                    'lane-3.1', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-3.8', 'lane-3.9', 'lane-4.9', 'lane-4.8', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-4.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground73-77_lane-3_2_OnRamp.kml', [
                    'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-3.8', 'lane-3.9', 'lane-4.9', 'lane-4.8', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3'
                ])
            ]

            labels_73_77 = [
                'lane 1', 'lane 2', 'lane 3', 'lane -1', 'lane -2', 'lane -3_1', 'lane -3_2', 'lane -3_2 OnRamp'
            ]

            colors_73_77 = [
                'red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow'
            ]

            playground73_77.create_polygon_and_plot(kml_files_and_names_73_77, labels_73_77, colors_73_77, x_utm_origin_73_77, y_utm_origin_73_77)

        elif 78 <= index <= 92:
            # 获取playground78-92的xUtmOrigin和yUtmOrigin
            recordings_meta_file_78_92 = f'./{index}_recordingMeta.csv'  
            x_utm_origin_78_92, y_utm_origin_78_92 = get_utm_origin(recordings_meta_file_78_92)

            # 提取playground78-92 KML文件中的多边形
            onramp_polygons_78_92 = {
                'playground78-92_lane-4_OnRamp': (playground78_92.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground78-92_lane-4_OnRamp.kml',
                    ['lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-4.2'],
                    x_utm_origin_78_92,
                    y_utm_origin_78_92
                ), -4)
            }

            lanes_polygons_78_92 = [
                (1, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane1.kml', [
                    'lane1.1', 'lane1.0', 'lane1.2', 'lane1.3', 'lane1.4', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.0', 'lane2.1', 'lane1.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (2, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane2.kml', [
                    'lane2.1', 'lane2.0', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.0', 'lane3.1', 'lane2.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (3, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane3.kml', [
                    'lane3.1', 'lane3.0', 'lane3.2', 'lane3.3', 'lane3.4', 'lane4.4', 'lane4.3', 'lane4.2', 'lane4.0', 'lane4.1', 'lane3.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (4, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane4.kml', [
                    'lane4.1', 'lane4.0', 'lane4.2', 'lane4.3', 'lane4.4', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.0', 'lane5.1', 'lane4.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (-1, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane-1.kml', [
                    'lane-1.1', 'lane-1.0', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.0', 'lane-2.1', 'lane-1.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (-2, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane-2.kml', [
                    'lane-2.1', 'lane-2.0', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.0', 'lane-3.1', 'lane-2.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (-3, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane-3.kml', [
                    'lane-3.1', 'lane-3.0', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-4.5', 'lane-4.4', 'lane-4.3','lane-4.9','lane-4.0' ,'lane-4.2' , 'lane-4.1', 'lane-3.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92)),
                (-4, playground78_92.extract_polygon_from_kml('./scenario_mining/exiD_scenario_mining/playground78-92_lane-4.kml', [
                    'lane-4.1','lane-4.9', 'lane-4.0', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.0', 'lane-5.9','lane-5.1', 'lane-4.1'
                ], x_utm_origin_78_92, y_utm_origin_78_92))
            ]

            # 更新playground78-92的轨迹数据
            input_file_78_92 = f'{index}_tracks.csv'
            output_file_78_92 = f'{index}_updated_tracks.csv'
            playground78_92.update_track_data(input_file_78_92, output_file_78_92, onramp_polygons_78_92, {}, lanes_polygons_78_92)

            # 创建并绘制playground78-92的多边形
            kml_files_and_names_78_92 = [
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane1.kml', [
                    'lane1.1', 'lane1.0', 'lane1.2', 'lane1.3', 'lane1.4', 'lane2.4', 'lane2.3', 'lane2.2', 'lane2.0', 'lane2.1', 'lane1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane2.kml', [
                    'lane2.1', 'lane2.0', 'lane2.2', 'lane2.3', 'lane2.4', 'lane3.4', 'lane3.3', 'lane3.2', 'lane3.0', 'lane3.1', 'lane2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane3.kml', [
                    'lane3.1', 'lane3.0', 'lane3.2', 'lane3.3', 'lane3.4', 'lane4.4', 'lane4.3', 'lane4.2', 'lane4.0', 'lane4.1', 'lane3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane4.kml', [
                    'lane4.1', 'lane4.0', 'lane4.2', 'lane4.3', 'lane4.4', 'lane5.4', 'lane5.3', 'lane5.2', 'lane5.0', 'lane5.1', 'lane4.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane-1.kml', [
                    'lane-1.1', 'lane-1.0', 'lane-1.2', 'lane-1.3', 'lane-1.4', 'lane-2.4', 'lane-2.3', 'lane-2.2', 'lane-2.0', 'lane-2.1', 'lane-1.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane-2.kml', [
                    'lane-2.1', 'lane-2.0', 'lane-2.2', 'lane-2.3', 'lane-2.4', 'lane-3.4', 'lane-3.3', 'lane-3.2', 'lane-3.0', 'lane-3.1', 'lane-2.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane-3.kml', [
                    'lane-3.1', 'lane-3.0', 'lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-4.5', 'lane-4.4', 'lane-4.3','lane-4.9','lane-4.0' ,'lane-4.2' , 'lane-4.1', 'lane-3.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane-4.kml', [
                    'lane-4.1','lane-4.9', 'lane-4.0', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.0', 'lane-5.9','lane-5.1', 'lane-4.1'
                ]),
                ('./scenario_mining/exiD_scenario_mining/playground78-92_lane-4_OnRamp.kml', [
                    'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-4.2'
                ])
            ]

            labels_78_92 = [
                'lane 1', 'lane 2', 'lane 3', 'lane 4', 'lane -1', 'lane -2', 'lane -3', 'lane -4', 'lane -4 OnRamp'
            ]

            colors_78_92 = [
                'red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'grey'
            ]

            playground78_92.create_polygon_and_plot(kml_files_and_names_78_92, labels_78_92, colors_78_92, x_utm_origin_78_92, y_utm_origin_78_92)


def get_activity_from_LLM_response_ExitD(LLM_response):
    """
    Refine the activity from LLM response.

    Parameters:
    -----------
    Inputs:
        LLM_response (dict): a dictionary containing LLM response
        dataset_option (str): the dataset option (highD, exitD, etc.)

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
    req_ego_rampAct = None
    req_ego_rampAct = LLM_response['Ego Vehicle']['Ego ramp activity'][0]

    # Target
    # Target start position
    tgt_startPos = LLM_response['Target Vehicle #1']['Target start position']
    start_item = list(tgt_startPos.items())[0]
    req_tgt_startPos = start_item[1][0]
    # Target end position
    tgt_endPos = LLM_response['Target Vehicle #1']['Target end position']
    end_item = list(tgt_endPos.items())[0]
    req_tgt_endPos = end_item[1][0]

    # Target lateral and longitudinal activity
    req_tgt_latAct = LLM_response['Target Vehicle #1']['Target behavior']['target lateral activity'][0]
    req_tgt_longAct = LLM_response['Target Vehicle #1']['Target behavior']['target longitudinal activity'][0]
    req_tgt_rampAct = None
    req_tgt_rampAct = LLM_response['Target Vehicle #1']['Target behavior']['target ramp activity'][0]

    return req_ego_latAct, req_ego_lonAct, req_ego_rampAct, req_tgt_startPos, req_tgt_endPos, req_tgt_latAct, req_tgt_longAct, req_tgt_rampAct


def  mainFunctionScenarioIdentification_ExitD(tracks_36, key_label, latActDict, longActDict, interactIdDict, progress_bar):
    """
    main function to search the desired scenarios

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

    req_ego_latAct, req_ego_lonAct, req_ego_rampAct, req_tgt_startPos, req_tgt_endPos, \
    req_tgt_latAct, req_tgt_longAct, req_tgt_rampAct = get_activity_from_LLM_response_ExitD(key_label)

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

        # Check the ego vehicle ramp activity
        curr_ego_rampActs = tracks_36[tracks_36['trackId'] == curr_ego]['activity_type'].unique()
        if req_ego_rampAct not in curr_ego_rampActs:
            continue

        tgt_list = []
        for curr_interact_tgt in curr_interact_tgts:
            if curr_interact_tgt == -1 or curr_interact_tgt not in latActDict or curr_interact_tgt not in longActDict:
                continue

            # Judge the target vehicle lateral activity
            curr_interact_tgt_latAct = latActDict[curr_interact_tgt]
            if req_tgt_latAct not in curr_interact_tgt_latAct['LateralActivity'].values:
                continue
            tgtLatActFram = find_start_end_frame_of_latAct(curr_interact_tgt_latAct, req_tgt_latAct)

            # Check the target vehicle ramp activity
            curr_tgt_rampActs = tracks_36[tracks_36['trackId'] == curr_interact_tgt]['activity_type'].unique()
            if req_tgt_rampAct not in curr_tgt_rampActs:
                continue

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
            curr_ego_start_lane = curr_ego_start_row['laneId'][0]
            curr_ego_end_lane = curr_ego_end_row['laneId'][0]
            curr_tgt_start_lane = curr_tgt_start_row['laneId'][0]
            curr_tgt_end_lane = curr_tgt_end_row['laneId'][0]

            # Calculate the target vehicle position at start  
            ego_drive_direction = curr_ego_end_row['xCenter'][0] - curr_ego_start_row['xCenter'][0]
            delta_x_tgt_ego_start = curr_tgt_start_row['xCenter'][0] - curr_ego_start_row['xCenter'][0]
            laneDiffStart = curr_tgt_start_lane - curr_ego_start_lane
            curr_tgt_pos_start = pos_calc(laneDiffStart, ego_drive_direction, delta_x_tgt_ego_start)

            # If current target vehicle was not once the leadId of the current ego vehicle, then skip
            if curr_interact_tgt not in curr_ego_life['leadId'].values:
                continue

            if curr_tgt_pos_start == req_tgt_startPos:  # Judge the start position
                # Calculate the target vehicle position at end
                delta_x_tgt_ego_end = curr_tgt_end_row['xCenter'][0] - curr_ego_end_row['xCenter'][0]
                laneDiffEnd = curr_tgt_end_lane - curr_ego_end_lane
                curr_tgt_pos_end = pos_calc(laneDiffEnd, ego_drive_direction, delta_x_tgt_ego_end)
                if curr_tgt_pos_end == req_tgt_endPos:  # Judge the end position
                    # If longitudinal activity is omitted, get current targetID and BegFrame, EndFrame
                    if req_ego_lonAct == 'NA' and req_tgt_longAct == 'NA':
                        tgt_list.append(curr_interact_tgt)
                        interFinal = []
                        interFinal.append(inter[0])
                        interFinal.append(inter[1])
                        continue

                    # Judge the ego vehicle longitudinal activity: if 'NA', omit longitudinal
                    if req_ego_lonAct not in curr_ego_lonActs['LongitudinalActivity'].values:
                        continue
                    # Judge the target vehicle longitudinal activity: 
                    curr_tgt_lonAct = longActDict[curr_interact_tgt]
                    if req_tgt_longAct not in curr_tgt_lonAct['LongitudinalActivity'].values:
                        continue
                    egoLonActFram = find_start_end_frame_of_lonAct(curr_ego_lonActs, req_ego_lonAct)
                    tgtLonActFram = find_start_end_frame_of_lonAct(curr_tgt_lonAct, req_tgt_longAct)
                    # intersected frames of longitudinal activity of ego and target
                    interLon = intersection_judge(egoLonActFram, tgtLonActFram)
                    if len(interLon) != 0:
                        # Intersected frames of lateral and longitudinal
                        interFinal = intersection_judge(inter, interLon)
                        if len(interFinal) != 0:
                            tgt_list.append(curr_tgt_start_row['trackId'][0])
                            break

        if len(tgt_list) != 0:
            scenarioList.append(curr_ego)
            scenarioList.append(tgt_list)
            scenarioList.append(interFinal[0])
            scenarioList.append(interFinal[1])

        # Append the scenario list into another list
        if len(scenarioList) != 0:
            scenarioLists.append(scenarioList)

    return scenarioLists


file_path = '00_tracks.csv'
select_playground(file_path)

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

dataset_option = "exitD"
dataset_load = './39_updated_tracks.csv'
key_label = extract_json_from_response(response)
print('Response of the LLM:')
print(key_label)
tracks_original = pd.read_csv(dataset_load)    
progress_bar = st.progress(0)
longActDict, latActDict, interactIdDict = main_fcn_veh_activity(tracks_original, progress_bar,dataset_option)
#print(longActDict, latActDict, interactIdDict)
scenarioList = mainFunctionScenarioIdentification_ExitD(tracks_original, key_label, latActDict, longActDict, interactIdDict, progress_bar)
print(scenarioList)                        
