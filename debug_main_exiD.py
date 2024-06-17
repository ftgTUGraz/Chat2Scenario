
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
from shapely.geometry import Polygon
import shapely.wkt
import pickle
import json
from shapely.geometry import mapping
import json
from shapely.geometry import shape, Polygon

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
            '''
            if 0 <= index <= 9:
                recordings_meta_file_1_18 = f'./0{index}_recordingMeta.csv'
            else:  
                recordings_meta_file_1_18 = f'./{index}_recordingMeta.csv'  
            '''
            #x_utm_origin_1_18, y_utm_origin_1_18 = get_utm_origin(recordings_meta_file_1_18)
            #x_utm_origin_1_18, y_utm_origin_1_18 = 352146.6000,5651141.9000

            # 提取playground1-18 KML文件中的多边形
            '''
            onramp_polygon_1_18 = playground1_18.extract_polygon_from_kml(
                './scenario_mining/exiD_scenario_mining/playground1-18_lane-5_OnRamp.kml',
                ['lane-8.1', 'lane-8.2', 'lane-6.2', 'lane-7.1', 'lane-8.1'],
                x_utm_origin_1_18,
                y_utm_origin_1_18
            )
            '''
            # 定义多边形的顶点
            onramp_polygon_1_18_coords = [(282, -131), (355, -210), (358, -207), (284, -127), (282, -131)]

            onramp_polygon_1_18 = Polygon(onramp_polygon_1_18_coords)
            '''
            offramp_polygon_1_18 = playground1_18.extract_polygon_from_kml(
                './scenario_mining/exiD_scenario_mining/playground1-18_lane4_OffRamp.kml',
                ['lane6.1', 'lane6.2', 'lane6.3', 'lane7.2', 'lane7.1', 'lane6.1'],
                x_utm_origin_1_18,
                y_utm_origin_1_18
            )
            '''
            offramp_polygon_1_18_coords = [(374, -160), (395, -191), (432, -244), (435, -242), (378, -157), (374, -160)]
            offramp_polygon_1_18 = Polygon(offramp_polygon_1_18_coords)
            '''
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
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_1_18
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_1_18.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 lanes_polygons_1_18.json 文件中")          
            '''
            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    278.2847802300239,
                                    -68.28092145547271
                                ],
                                [
                                    302.053729856445,
                                    -99.01711041945964
                                ],
                                [
                                    341.5536070037633,
                                    -150.50600938219577
                                ],
                                [
                                    404.015857748338,
                                    -232.06003621127456
                                ],
                                [
                                    468.42643810703885,
                                    -316.21292255073786
                                ],
                                [
                                    518.0983297112398,
                                    -380.7375992992893
                                ],
                                [
                                    565.6732355263084,
                                    -443.1176361842081
                                ],
                                [
                                    592.2262458913028,
                                    -478.28804612066597
                                ],
                                [
                                    595.1432088135043,
                                    -475.96898970846087
                                ],
                                [
                                    568.517238310189,
                                    -440.9959609368816
                                ],
                                [
                                    521.1563677398954,
                                    -378.4508457351476
                                ],
                                [
                                    471.68376324500423,
                                    -313.7131992755458
                                ],
                                [
                                    407.4056204241351,
                                    -230.03073590248823
                                ],
                                [
                                    344.41979613661533,
                                    -148.14884167257696
                                ],
                                [
                                    304.7899339782307,
                                    -96.69401827827096
                                ],
                                [
                                    281.176278100349,
                                    -65.50648467894644
                                ],
                                [
                                    278.2847802300239,
                                    -68.28092145547271
                                ]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    281.176278100349,
                                    -65.50648467894644
                                ],
                                [
                                    304.7899339782307,
                                    -96.69401827827096
                                ],
                                [
                                    344.41979613661533,
                                    -148.14884167257696
                                ],
                                [
                                    407.4056204241351,
                                    -230.03073590248823
                                ],
                                [
                                    471.68376324500423,
                                    -313.7131992755458
                                ],
                                [
                                    521.1563677398954,
                                    -378.4508457351476
                                ],
                                [
                                    568.517238310189,
                                    -440.9959609368816
                                ],
                                [
                                    595.1432088135043,
                                    -475.96898970846087
                                ],
                                [
                                    597.7939362504985,
                                    -473.6040585162118
                                ],
                                [
                                    571.3793934920104,
                                    -438.6628754064441
                                ],
                                [
                                    524.17645837483,
                                    -376.27572779357433
                                ],
                                [
                                    474.9058749125106,
                                    -311.2921170219779
                                ],
                                [
                                    410.5690287416801,
                                    -227.48205582611263
                                ],
                                [
                                    347.5037615931942,
                                    -145.34914367552847
                                ],
                                [
                                    308.23519699892495,
                                    -93.94504444487393
                                ],
                                [
                                    284.2456872285111,
                                    -62.81778566259891
                                ],
                                [
                                    281.176278100349,
                                    -65.50648467894644
                                ]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    370.49833874450997,
                                    -164.17523724306375
                                ],
                                [
                                    414.2029782922473,
                                    -224.43043146189302
                                ],
                                [
                                    463.9402883455041,
                                    -296.8572966000065
                                ],
                                [
                                    474.9058749125106,
                                    -311.2921170219779
                                ],
                                [
                                    524.17645837483,
                                    -376.27572779357433
                                ],
                                [
                                    571.3793934920104,
                                    -438.6628754064441
                                ],
                                [
                                    597.7939362504985,
                                    -473.6040585162118
                                ],
                                [
                                    599.8424440906965,
                                    -470.60003031324595
                                ],
                                [
                                    580.9387144310749,
                                    -445.43545870296657
                                ],
                                [
                                    526.9216672151815,
                                    -373.958112728782
                                ],
                                [
                                    477.73136994300876,
                                    -308.78664700407535
                                ],
                                [
                                    416.65450132638216,
                                    -221.6445157788694
                                ],
                                [
                                    394.9449618161307,
                                    -190.8647281276062
                                ],
                                [
                                    372.7636280420702,
                                    -161.27871040720493
                                ],
                                [
                                    370.49833874450997,
                                    -164.17523724306375
                                ]
                            ]
                        ]
                    }
                ],
                [
                    4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    374.4888390492415,
                                    -159.7541891876608
                                ],
                                [
                                    394.9449618161307,
                                    -190.8647281276062
                                ],
                                [
                                    416.65450132638216,
                                    -221.6445157788694
                                ],
                                [
                                    477.73136994300876,
                                    -308.78664700407535
                                ],
                                [
                                    526.9216672151815,
                                    -373.958112728782
                                ],
                                [
                                    580.9387144310749,
                                    -445.43545870296657
                                ],
                                [
                                    562.9689124572906,
                                    -416.39214814733714
                                ],
                                [
                                    529.6359066521982,
                                    -371.7245691185817
                                ],
                                [
                                    480.3468829652411,
                                    -306.3319803047925
                                ],
                                [
                                    419.0660473003518,
                                    -219.42061564140022
                                ],
                                [
                                    377.73254355299287,
                                    -157.30422125663608
                                ],
                                [
                                    374.4888390492415,
                                    -159.7541891876608
                                ]
                            ]
                        ]
                    }
                ],
                [
                    4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    374.4888390492415,
                                    -159.7541891876608
                                ],
                                [
                                    394.9449618161307,
                                    -190.8647281276062
                                ],
                                [
                                    432.11060787690803,
                                    -243.98820682242513
                                ],
                                [
                                    434.68041734898,
                                    -241.94324372708797
                                ],
                                [
                                    377.73254355299287,
                                    -157.30422125663608
                                ],
                                [
                                    374.4888390492415,
                                    -159.7541891876608
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    272.65575653564883,
                                    -72.5970634734258
                                ],
                                [
                                    336.39145104191266,
                                    -155.64232034049928
                                ],
                                [
                                    398.9133712934563,
                                    -237.1114298524335
                                ],
                                [
                                    512.9574332652846,
                                    -385.5034197727218
                                ],
                                [
                                    587.2198447982082,
                                    -483.19663551356643
                                ],
                                [
                                    589.9398582216818,
                                    -481.00704958382994
                                ],
                                [
                                    515.4763043537969,
                                    -383.1971084205434
                                ],
                                [
                                    401.4844288995955,
                                    -234.4820140255615
                                ],
                                [
                                    339.1340694014216,
                                    -153.12261707615107
                                ],
                                [
                                    275.68927806417923,
                                    -70.36574067547917
                                ],
                                [
                                    272.65575653564883,
                                    -72.5970634734258
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    269.48172801872715,
                                    -75.26019941549748
                                ],
                                [
                                    333.1207564016804,
                                    -158.40131418779492
                                ],
                                [
                                    360.49984337366186,
                                    -194.5785504207015
                                ],
                                [
                                    452.61391461314633,
                                    -313.1382520580664
                                ],
                                [
                                    510.36197446787264,
                                    -388.2304834499955
                                ],
                                [
                                    562.3631445922074,
                                    -456.95451681222767
                                ],
                                [
                                    584.7048105150461,
                                    -485.8785347864032
                                ],
                                [
                                    587.2198447982082,
                                    -483.19663551356643
                                ],
                                [
                                    512.9574332652846,
                                    -385.5034197727218
                                ],
                                [
                                    398.9133712934563,
                                    -237.1114298524335
                                ],
                                [
                                    336.39145104191266,
                                    -155.64232034049928
                                ],
                                [
                                    272.65575653564883,
                                    -72.5970634734258
                                ],
                                [
                                    269.48172801872715,
                                    -75.26019941549748
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    266.8677170102019,
                                    -77.97903019748628
                                ],
                                [
                                    344.65700547758024,
                                    -178.99704697728157
                                ],
                                [
                                    360.49984337366186,
                                    -194.5785504207015
                                ],
                                [
                                    333.1207564016804,
                                    -158.40131418779492
                                ],
                                [
                                    269.48172801872715,
                                    -75.26019941549748
                                ],
                                [
                                    266.8677170102019,
                                    -77.97903019748628
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    259.5532058150857,
                                    -85.11782492883503
                                ],
                                [
                                    334.0283684451133,
                                    -179.91773108951747
                                ],
                                [
                                    449.2819532647263,
                                    -316.18775018304586
                                ],
                                [
                                    480.97705319186207,
                                    -357.44373666029423
                                ],
                                [
                                    562.3631445922074,
                                    -456.95451681222767
                                ],
                                [
                                    510.36197446787264,
                                    -388.2304834499955
                                ],
                                [
                                    452.61391461314633,
                                    -313.1382520580664
                                ],
                                [
                                    393.50459216273157,
                                    -242.3003060258925
                                ],
                                [
                                    327.2534539208864,
                                    -164.8254524357617
                                ],
                                [
                                    263.4830346395029,
                                    -81.9562173821032
                                ],
                                [
                                    259.5532058150857,
                                    -85.11782492883503
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -5,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    282.46261962444987,
                                    -131.11906064115465
                                ],
                                [
                                    320.86997411272023,
                                    -171.39956625830382
                                ],
                                [
                                    446.6366176751908,
                                    -318.73995826020837
                                ],
                                [
                                    449.2819532647263,
                                    -316.18775018304586
                                ],
                                [
                                    334.0283684451133,
                                    -179.91773108951747
                                ],
                                [
                                    284.4459443225642,
                                    -127.28177763149142
                                ],
                                [
                                    282.46261962444987,
                                    -131.11906064115465
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -5,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    282.46261962444987,
                                    -131.11906064115465
                                ],
                                [
                                    354.66170536749996,
                                    -209.70990161038935
                                ],
                                [
                                    357.62887006113306,
                                    -207.0684313448146
                                ],
                                [
                                    284.4459443225642,
                                    -127.28177763149142
                                ],
                                [
                                    282.46261962444987,
                                    -131.11906064115465
                                ]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的元组列表
            lanes_polygons_1_18 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]
            
            if 0 <= index <= 9:
                
                input_file_1_18 = f'0{index}_tracks.csv'
                output_file_1_18 = f'0{index}_updated_tracks.csv'
            else :
                input_file_1_18 = f'{index}_tracks.csv'
                output_file_1_18 = f'{index}_updated_tracks.csv'
            playground1_18.update_track_data(input_file_1_18, output_file_1_18, onramp_polygon_1_18, offramp_polygon_1_18, lanes_polygons_1_18)
            '''
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
            '''
            '''
            # 保存 kml_files_and_names_1_18 到文件
            with open('kml_files_and_names_1_18.pkl', 'wb') as f:
                pickle.dump(kml_files_and_names_1_18, f)
            
            # 从文件中加载 kml_files_and_names_1_18
            with open('kml_files_and_names_1_18.pkl', 'rb') as f:
                kml_files_and_names_1_18 = pickle.load(f)
            '''
            '''
            labels_1_18 = [
                'lane 1', 'lane 2', 'lane 3', 'lane 4', 'lane 4 OffRamp',
                'lane -1', 'lane -2', 'lane -3', 'lane -4', 'lane -5', 'lane 5 OnRamp'
            ]

            colors_1_18 = [
                'red', 'blue', 'green', 'purple', 'orange', 
                'cyan', 'magenta', 'yellow', 'brown', 'pink', 'grey'
            ]
            playground1_18.create_polygon_and_plot(kml_files_and_names_1_18, labels_1_18, colors_1_18, x_utm_origin_1_18, y_utm_origin_1_18)
            '''
        elif 19 <= index <= 38:

            # 获取playground19-38的xUtmOrigin和yUtmOrigin
            #recordings_meta_file_19_38 =  f'./{index}_recordingMeta.csv'  
            #x_utm_origin_19_38, y_utm_origin_19_38 = get_utm_origin(recordings_meta_file_19_38)
            #x_utm_origin_19_38, y_utm_origin_19_38 = 351816.7000,5651523.4000
            # 提取playground19-38 KML文件中的多边形
            '''
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
            # 将多边形转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {key: (mapping(polygon), value) for key, (polygon, value) in onramp_polygons_19_38.items()}

            # 将数据保存到 JSON 文件中
            with open('onramp_polygons_19_38.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 onramp_polygons_19_38.json 文件中")
            '''
            onramp_polygon_19_38_coords_1 = [
                (417.9635702712694, -237.5015376629308),
                (400.2264643313829, -214.5553731545806),
                (358.43832916312385, -174.91530229430646),
                (314.6819614908309, -143.90204749349505),
                (311.43236986891134, -148.65390884503722),
                (354.7595205893158, -179.08403029013425),
                (395.4013636430609, -218.46967659518123),
                (414.14003745338414, -240.33766895905137),
                (417.9635702712694, -237.5015376629308)
            ]
            onramp_polygon_19_38_coords_2 = [
                (543.493799658725, -335.4048775937408),
                (580.8542123081279, -374.5348250856623),
                (606.472093112825, -386.2462885538116),
                (610.5825320084696, -382.49000732041895),
                (583.9023105505039, -371.73521982319653),
                (546.4489273423678, -332.77966612856835),
                (543.493799658725, -335.4048775937408)
            ]

            # 创建Polygon对象
            onramp_polygon_19_38_1 = Polygon(onramp_polygon_19_38_coords_1)
            onramp_polygon_19_38_2 = Polygon(onramp_polygon_19_38_coords_2)

            # 创建onramp_polygons_19_38字典
            onramp_polygons_19_38 = {
                'playground19-38_lane-4_OnRamp': (onramp_polygon_19_38_1, -4),
                'playground19-38_lane4_OnRamp': (onramp_polygon_19_38_2, 4)
            }
            '''
            offramp_polygons_19_38 = {
                'playground19-38_lane-5_OffRamp': (playground19_38.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground19-38_lane-5_OffRamp.kml',
                    ['lane-6.1', 'lane-6.2', 'lane-6.3', 'lane-7.3', 'lane-7.2', 'lane-7.1', 'lane-6.1'],
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
            # 将多边形转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {key: (mapping(polygon), value) for key, (polygon, value) in offramp_polygons_19_38.items()}

            # 将数据保存到 JSON 文件中
            with open('offramp_polygons_19_38.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 offramp_polygons_19_38.json 文件中")
            '''
            # 从JSON数据中提取的多边形坐标和值
            offramp_polygon_19_38_coords_1 = [
                (557.5267711196211, -421.4385609002784),
                (520.4895956247346, -376.65872219670564),
                (479.5424434004235, -324.3662158176303),
                (487.58549427083926, -340.0177958542481),
                (517.5840260589612, -379.28128955326974),
                (551.7076426656567, -426.50686578452587),
                (557.5267711196211, -421.4385609002784)
            ]
            offramp_polygon_19_38_coords_2 = [
                (379.80832447629655, -81.84228744637221),
                (396.74548233364476, -130.27554988861084),
                (430.6301221573958, -187.89729742053896),
                (434.561310428835, -184.49044726602733),
                (401.79181745427195, -128.2541870670393),
                (385.1939919034485, -81.1246771691367),
                (379.80832447629655, -81.84228744637221)
            ]

            # 创建Polygon对象
            offramp_polygon_19_38_1 = Polygon(offramp_polygon_19_38_coords_1)
            offramp_polygon_19_38_2 = Polygon(offramp_polygon_19_38_coords_2)

            # 创建offramp_polygons_19_38字典
            offramp_polygons_19_38 = {
                'playground19-38_lane-5_OffRamp': (offramp_polygon_19_38_1, -5),
                'playground19-38_lane4_OffRamp': (offramp_polygon_19_38_2, 4)
            }
            '''
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
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_19_38
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_19_38.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 lanes_polygons_19_38.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    308.8621880970313,
                                    -59.10356215201318
                                ],
                                [
                                    354.5640190876438,
                                    -118.66652759723365
                                ],
                                [
                                    454.1943377442076,
                                    -248.52964199054986
                                ],
                                [
                                    576.2723304494866,
                                    -407.840584105812
                                ],
                                [
                                    578.9418257932994,
                                    -405.3973595900461
                                ],
                                [
                                    456.9036577557563,
                                    -245.97693165391684
                                ],
                                [
                                    357.0340984921786,
                                    -116.08048329409212
                                ],
                                [
                                    311.7750581847504,
                                    -56.31830155942589
                                ],
                                [
                                    308.8621880970313,
                                    -59.10356215201318
                                ]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    311.7750581847504,
                                    -56.31830155942589
                                ],
                                [
                                    357.0340984921786,
                                    -116.08048329409212
                                ],
                                [
                                    456.9036577557563,
                                    -245.97693165391684
                                ],
                                [
                                    578.9418257932994,
                                    -405.3973595900461
                                ],
                                [
                                    582.2572947255685,
                                    -402.3929488584399
                                ],
                                [
                                    460.03933578619035,
                                    -243.15093315858394
                                ],
                                [
                                    360.33784745965386,
                                    -113.16343545354903
                                ],
                                [
                                    314.41641447442817,
                                    -53.41711242683232
                                ],
                                [
                                    311.7750581847504,
                                    -56.31830155942589
                                ]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    319.29476028261706,
                                    -48.476206965744495
                                ],
                                [
                                    428.1699137362302,
                                    -190.38442600425333
                                ],
                                [
                                    540.956289619382,
                                    -337.4571679318324
                                ],
                                [
                                    587.1041600945173,
                                    -397.75375586748123
                                ],
                                [
                                    589.7894139915588,
                                    -395.53222673386335
                                ],
                                [
                                    543.493799658725,
                                    -335.4048775937408
                                ],
                                [
                                    430.6301221573958,
                                    -187.89729742053896
                                ],
                                [
                                    321.70928901137086,
                                    -45.57247888389975
                                ],
                                [
                                    319.29476028261706,
                                    -48.476206965744495
                                ]
                            ]
                        ]
                    }
                ],
                [
                    4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    379.80832447629655,
                                    -81.84228744637221
                                ],
                                [
                                    396.74548233364476,
                                    -130.27554988861084
                                ],
                                [
                                    430.6301221573958,
                                    -187.89729742053896
                                ],
                                [
                                    543.493799658725,
                                    -335.4048775937408
                                ],
                                [
                                    580.8542123081279,
                                    -374.5348250856623
                                ],
                                [
                                    610.5825320084696,
                                    -382.49000732041895
                                ],
                                [
                                    583.9023105505039,
                                    -371.73521982319653
                                ],
                                [
                                    546.4489273423678,
                                    -332.77966612856835
                                ],
                                [
                                    434.561310428835,
                                    -184.49044726602733
                                ],
                                [
                                    401.79181745427195,
                                    -128.2541870670393
                                ],
                                [
                                    379.80832447629655,
                                    -81.84228744637221
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    573.5580388903036,
                                    -410.1542776217684
                                ],
                                [
                                    451.3923153327196,
                                    -250.53686138242483
                                ],
                                [
                                    351.57553154957714,
                                    -120.64847174379975
                                ],
                                [
                                    305.90319931466365,
                                    -61.10528236441314
                                ],
                                [
                                    302.37332523131045,
                                    -63.132339674048126
                                ],
                                [
                                    348.6576564591378,
                                    -122.77555314730853
                                ],
                                [
                                    448.4474046481773,
                                    -252.68703379668295
                                ],
                                [
                                    570.4898319427157,
                                    -412.20731523353606
                                ],
                                [
                                    573.5580388903036,
                                    -410.1542776217684
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    570.4898319427157,
                                    -412.20731523353606
                                ],
                                [
                                    448.4474046481773,
                                    -252.68703379668295
                                ],
                                [
                                    348.6576564591378,
                                    -122.77555314730853
                                ],
                                [
                                    302.37332523131045,
                                    -63.132339674048126
                                ],
                                [
                                    298.9112099871272,
                                    -65.06216375995427
                                ],
                                [
                                    345.01769594539655,
                                    -125.20385039877146
                                ],
                                [
                                    445.264686854498,
                                    -255.31260212510824
                                ],
                                [
                                    567.1287262705155,
                                    -414.65824346151203
                                ],
                                [
                                    570.4898319427157,
                                    -412.20731523353606
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    566.0114862072514,
                                    -415.3952153129503
                                ],
                                [
                                    526.3178615267971,
                                    -371.9273846587166
                                ],
                                [
                                    420.9142636442557,
                                    -235.39138147141784
                                ],
                                [
                                    293.12768723414047,
                                    -69.02471667807549
                                ],
                                [
                                    290.07174751145067,
                                    -70.6578523144126
                                ],
                                [
                                    417.9635702712694,
                                    -237.5015376629308
                                ],
                                [
                                    523.348176593252,
                                    -374.3870524233207
                                ],
                                [
                                    562.9411560249864,
                                    -417.51383363083005
                                ],
                                [
                                    566.0114862072514,
                                    -415.3952153129503
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    560.8794837046298,
                                    -418.56981870532036
                                ],
                                [
                                    523.348176593252,
                                    -374.3870524233207
                                ],
                                [
                                    482.364855578111,
                                    -321.393402970396
                                ],
                                [
                                    417.9635702712694,
                                    -237.5015376629308
                                ],
                                [
                                    400.2264643313829,
                                    -214.5553731545806
                                ],
                                [
                                    358.43832916312385,
                                    -174.91530229430646
                                ],
                                [
                                    314.6819614908309,
                                    -143.90204749349505
                                ],
                                [
                                    311.43236986891134,
                                    -148.65390884503722
                                ],
                                [
                                    354.7595205893158,
                                    -179.08403029013425
                                ],
                                [
                                    395.4013636430609,
                                    -218.46967659518123
                                ],
                                [
                                    414.14003745338414,
                                    -240.33766895905137
                                ],
                                [
                                    479.5424434004235,
                                    -324.3662158176303
                                ],
                                [
                                    520.4895956247346,
                                    -376.65872219670564
                                ],
                                [
                                    557.5267711196211,
                                    -421.4385609002784
                                ],
                                [
                                    560.8794837046298,
                                    -418.56981870532036
                                ]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的元组列表
            lanes_polygons_19_38 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]            

            # 更新playground19-38的轨迹数据
            input_file_19_38 = f'{index}_tracks.csv'
            output_file_19_38 = f'{index}_updated_tracks.csv'
            playground19_38.update_track_data(input_file_19_38, output_file_19_38, onramp_polygons_19_38, offramp_polygons_19_38, lanes_polygons_19_38)
            '''
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
            '''
        elif 39 <= index <= 52:


            # 获取playground39-52的xUtmOrigin和yUtmOrigin
            #recordings_meta_file_39_52 = f'./{index}_recordingMeta.csv' 
            #x_utm_origin_39_52, y_utm_origin_39_52 = get_utm_origin(recordings_meta_file_39_52)
            #x_utm_origin_39_52, y_utm_origin_39_52 = 298089.6,5626462.9
            '''
            # 提取playground39-52 KML文件中的多边形
            onramp_polygons_39_52 = {
                'playground39-52_lane-3_OnRamp': (playground39_52.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground39-52_lane-3_OnRamp.kml',
                    ['lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.3'],
                    x_utm_origin_39_52,
                    y_utm_origin_39_52
                ), -3)
            }
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in onramp_polygons_39_52.items()
            }

            # 将数据保存到 JSON 文件中
            with open('onramp_polygons_39_52.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 onramp_polygons_39_52.json 文件中")
            '''

            # 提供的 JSON 数据
            json_data = {
                "playground39-52_lane-3_OnRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    728.9518131427467,
                                    -303.89075079280883
                                ],
                                [
                                    759.2265630253823,
                                    -260.64898117631674
                                ],
                                [
                                    772.9346081644762,
                                    -231.45304796658456
                                ],
                                [
                                    781.7091981001431,
                                    -198.51846698950976
                                ],
                                [
                                    782.0868422087515,
                                    -172.79553107358515
                                ],
                                [
                                    778.1012791024987,
                                    -171.9681030884385
                                ],
                                [
                                    778.0676012065378,
                                    -197.2596454527229
                                ],
                                [
                                    769.5015542802867,
                                    -229.9336008913815
                                ],
                                [
                                    755.4992944031255,
                                    -258.5593629768118
                                ],
                                [
                                    725.5469827312045,
                                    -302.29101979825646
                                ],
                                [
                                    728.9518131427467,
                                    -303.89075079280883
                                ]
                            ]
                        ]
                    },
                    -3
                ]
            }
            
            # 将 JSON 数据转换为包含 Polygon 对象的字典
            onramp_polygons_39_52 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }
            '''
            offramp_polygons_39_52 = {
                'playground39-52_lane3_OffRamp': (playground39_52.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground39-52_lane3_OffRamp.kml',
                    ['lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane3.3'],
                    x_utm_origin_39_52,
                    y_utm_origin_39_52
                ), 3)
            }
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in offramp_polygons_39_52.items()
            }

            # 将数据保存到 JSON 文件中
            with open('offramp_polygons_39_52.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 offramp_polygons_39_52.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = {
                "playground39-52_lane3_OffRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    758.7882475814549,
                                    -298.12368457764387
                                ],
                                [
                                    789.6128554748138,
                                    -256.79227890912443
                                ],
                                [
                                    808.6673423104221,
                                    -240.34378073178232
                                ],
                                [
                                    832.2387319568079,
                                    -227.70339542347938
                                ],
                                [
                                    864.34231781587,
                                    -218.31831522099674
                                ],
                                [
                                    864.8554476378486,
                                    -221.93957885261625
                                ],
                                [
                                    834.1090655809967,
                                    -231.06522625125945
                                ],
                                [
                                    811.9765433611465,
                                    -243.47062540706247
                                ],
                                [
                                    792.6502347435453,
                                    -259.39667652361095
                                ],
                                [
                                    762.197262930451,
                                    -299.9399224091321
                                ],
                                [
                                    758.7882475814549,
                                    -298.12368457764387
                                ]
                            ]
                        ]
                    },
                    3
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            offramp_polygons_39_52 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }

            '''
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
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_39_52
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_39_52.json', 'w') as f:
                json.dump(save_data, f, indent=4)     
            '''
            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    550.3666555886157,
                                    -613.2468181429431
                                ],
                                [
                                    650.6351881056908,
                                    -446.5388767309487
                                ],
                                [
                                    751.9961593647604,
                                    -294.6560219908133
                                ],
                                [
                                    818.3653080437798,
                                    -202.98225261922926
                                ],
                                [
                                    821.7713480112143,
                                    -204.83774710912257
                                ],
                                [
                                    755.4363849782385,
                                    -296.4591388395056
                                ],
                                [
                                    654.0720736680087,
                                    -448.28273222316056
                                ],
                                [
                                    553.7309505094308,
                                    -615.0203938810155
                                ],
                                [
                                    550.3666555886157,
                                    -613.2468181429431
                                ]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    821.7713480112143,
                                    -204.83774710912257
                                ],
                                [
                                    755.4363849782385,
                                    -296.4591388395056
                                ],
                                [
                                    654.0720736680087,
                                    -448.28273222316056
                                ],
                                [
                                    553.7309505094308,
                                    -615.0203938810155
                                ],
                                [
                                    557.1847433248768,
                                    -616.7197587182745
                                ],
                                [
                                    657.6569919321337,
                                    -449.7838460467756
                                ],
                                [
                                    758.7882475814549,
                                    -298.12368457764387
                                ],
                                [
                                    825.0851369101438,
                                    -206.51859422773123
                                ],
                                [
                                    821.7713480112143,
                                    -204.83774710912257
                                ]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    657.6569919321337,
                                    -449.7838460467756
                                ],
                                [
                                    758.7882475814549,
                                    -298.12368457764387
                                ],
                                [
                                    789.6128554748138,
                                    -256.79227890912443
                                ],
                                [
                                    808.6673423104221,
                                    -240.34378073178232
                                ],
                                [
                                    832.2387319568079,
                                    -227.70339542347938
                                ],
                                [
                                    864.34231781587,
                                    -218.31831522099674
                                ],
                                [
                                    864.8554476378486,
                                    -221.93957885261625
                                ],
                                [
                                    834.1090655809967,
                                    -231.06522625125945
                                ],
                                [
                                    811.9765433611465,
                                    -243.47062540706247
                                ],
                                [
                                    792.6502347435453,
                                    -259.39667652361095
                                ],
                                [
                                    762.197262930451,
                                    -299.9399224091321
                                ],
                                [
                                    679.3283944293507,
                                    -422.59100539330393
                                ],
                                [
                                    671.4714580529835,
                                    -433.7532955799252
                                ],
                                [
                                    657.6569919321337,
                                    -449.7838460467756
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    545.002065553097,
                                    -610.8200022112578
                                ],
                                [
                                    645.6008328213356,
                                    -443.5356948794797
                                ],
                                [
                                    746.8890539419372,
                                    -291.889259560965
                                ],
                                [
                                    813.5014277292648,
                                    -199.74753678496927
                                ],
                                [
                                    810.121714251989,
                                    -197.84799278341234
                                ],
                                [
                                    743.6359536906821,
                                    -290.082047409378
                                ],
                                [
                                    641.9355473061441,
                                    -441.9713333239779
                                ],
                                [
                                    541.5157484423835,
                                    -609.2880500555038
                                ],
                                [
                                    545.002065553097,
                                    -610.8200022112578
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    541.5157484423835,
                                    -609.2880500555038
                                ],
                                [
                                    641.9355473061441,
                                    -441.9713333239779
                                ],
                                [
                                    743.6359536906821,
                                    -290.082047409378
                                ],
                                [
                                    810.121714251989,
                                    -197.84799278341234
                                ],
                                [
                                    806.7676769854152,
                                    -195.76804823800921
                                ],
                                [
                                    740.0616079965839,
                                    -288.1973986700177
                                ],
                                [
                                    638.6830915680621,
                                    -440.420826215297
                                ],
                                [
                                    537.9852168856887,
                                    -607.4726453796029
                                ],
                                [
                                    541.5157484423835,
                                    -609.2880500555038
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    621.4728849959793,
                                    -466.8916496504098
                                ],
                                [
                                    638.6830915680621,
                                    -440.420826215297
                                ],
                                [
                                    740.0616079965839,
                                    -288.1973986700177
                                ],
                                [
                                    759.2265630253823,
                                    -260.64898117631674
                                ],
                                [
                                    772.9346081644762,
                                    -231.45304796658456
                                ],
                                [
                                    781.7091981001431,
                                    -198.51846698950976
                                ],
                                [
                                    782.0868422087515,
                                    -172.79553107358515
                                ],
                                [
                                    778.1012791024987,
                                    -171.9681030884385
                                ],
                                [
                                    778.0676012065378,
                                    -197.2596454527229
                                ],
                                [
                                    769.5015542802867,
                                    -229.9336008913815
                                ],
                                [
                                    755.4992944031255,
                                    -258.5593629768118
                                ],
                                [
                                    736.6671986082802,
                                    -286.3566905800253
                                ],
                                [
                                    642.3361816246179,
                                    -427.91532318573445
                                ],
                                [
                                    621.4728849959793,
                                    -466.8916496504098
                                ]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的列表
            lanes_polygons_39_52 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]

            # 更新playground39-52的轨迹数据
            input_file_39_52 = f'{index}_tracks.csv'
            output_file_39_52 = f'{index}_updated_tracks.csv'
            playground39_52.update_track_data(input_file_39_52, output_file_39_52, onramp_polygons_39_52, offramp_polygons_39_52, lanes_polygons_39_52)
            '''
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
            '''
        elif 53 <= index <= 60:


            # 获取playground53-60的xUtmOrigin和yUtmOrigin
            #recordings_meta_file_53_60 = f'./{index}_recordingMeta.csv' 
            #x_utm_origin_53_60, y_utm_origin_53_60 = get_utm_origin(recordings_meta_file_53_60)
            #x_utm_origin_53_60, y_utm_origin_53_60 = 334905.3,5645453.9
            # 提取playground53-60 KML文件中的多边形
            '''
            onramp_polygons_53_60 = {
                'playground53-60_lane-3_OnRamp': (playground53_60.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground53-60_lane-3_OnRamp.kml',
                    ['lane-3.2', 'lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3', 'lane-4.2', 'lane-3.2'],
                    x_utm_origin_53_60,
                    y_utm_origin_53_60
                ), -3)
            }
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in onramp_polygons_53_60.items()
            }

            # 将数据保存到 JSON 文件中
            with open('onramp_polygons_53_60.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 onramp_polygons_53_60.json 文件中") 
            '''      
            # 提供的 JSON 数据
            json_data = {
                "playground53-60_lane-3_OnRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    223.58338449295843,
                                    -128.0273137204349
                                ],
                                [
                                    192.26323484949535,
                                    -113.11643671337515
                                ],
                                [
                                    173.12065171304857,
                                    -110.46281152684242
                                ],
                                [
                                    156.6132822323707,
                                    -113.41854413133115
                                ],
                                [
                                    138.20514047151664,
                                    -122.68086718861014
                                ],
                                [
                                    129.72205294534797,
                                    -129.91261112876236
                                ],
                                [
                                    133.70443896419602,
                                    -133.39887781720608
                                ],
                                [
                                    141.736638714734,
                                    -126.64131337963045
                                ],
                                [
                                    158.16590475983685,
                                    -118.38563675433397
                                ],
                                [
                                    172.95008070126642,
                                    -115.7540500825271
                                ],
                                [
                                    191.0450799096143,
                                    -117.95953868981451
                                ],
                                [
                                    221.86966175981797,
                                    -131.18159038946033
                                ],
                                [
                                    223.58338449295843,
                                    -128.0273137204349
                                ]
                            ]
                        ]
                    },
                    -3
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            onramp_polygons_53_60 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            } 

            '''
            offramp_polygons_53_60 = {
                'playground53-60_lane3_OffRamp': (playground53_60.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground53-60_lane3_OffRamp.kml',
                    ['lane3.2', 'lane3.3', 'lane3.4', 'lane3.5', 'lane3.6', 'lane3.7', 'lane4.7', 'lane4.6', 'lane4.5', 'lane4.4', 'lane4.3', 'lane4.2', 'lane3.2'],
                    x_utm_origin_53_60,
                    y_utm_origin_53_60
                ), 3)
            }

            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in offramp_polygons_53_60.items()
            }

            # 将数据保存到 JSON 文件中
            with open('offramp_polygons_53_60.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 offramp_polygons_53_60.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = {
                "playground53-60_lane3_OffRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    197.51190760784084,
                                    -90.91433231905103
                                ],
                                [
                                    158.12112418928882,
                                    -65.67478009033948
                                ],
                                [
                                    142.68293568259105,
                                    -45.06852611619979
                                ],
                                [
                                    135.9712366592139,
                                    -28.777733232825994
                                ],
                                [
                                    132.684275651176,
                                    -14.30917145870626
                                ],
                                [
                                    137.8017475529341,
                                    -13.61771634221077
                                ],
                                [
                                    140.74390690383734,
                                    -27.770826203748584
                                ],
                                [
                                    147.4138604705804,
                                    -43.37214694172144
                                ],
                                [
                                    161.42728643032024,
                                    -61.88382932450622
                                ],
                                [
                                    199.0122889878694,
                                    -87.70675852801651
                                ],
                                [
                                    197.51190760784084,
                                    -90.91433231905103
                                ]
                            ]
                        ]
                    },
                    3
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            offramp_polygons_53_60 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }

            '''
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

            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_53_60
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_53_60.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 lanes_polygons_53_60.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    117.20271561591653,
                                    -58.938874788582325
                                ],
                                [
                                    229.44932671432616,
                                    -116.66345312166959
                                ],
                                [
                                    397.9694953231956,
                                    -214.89697796013206
                                ],
                                [
                                    532.8395297052921,
                                    -304.51059701666236
                                ],
                                [
                                    632.8117391615524,
                                    -377.8651793738827
                                ],
                                [
                                    635.1499898479669,
                                    -374.76201635506004
                                ],
                                [
                                    535.0786481642281,
                                    -301.06720384955406
                                ],
                                [
                                    399.92788268980803,
                                    -211.38999832514673
                                ],
                                [
                                    231.4318656352698,
                                    -113.3328992659226
                                ],
                                [
                                    118.91059820359806,
                                    -55.43421153817326
                                ],
                                [
                                    117.20271561591653,
                                    -58.938874788582325
                                ]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    118.91059820359806,
                                    -55.43421153817326
                                ],
                                [
                                    231.4318656352698,
                                    -113.3328992659226
                                ],
                                [
                                    399.92788268980803,
                                    -211.38999832514673
                                ],
                                [
                                    535.0786481642281,
                                    -301.06720384955406
                                ],
                                [
                                    635.1499898479669,
                                    -374.76201635506004
                                ],
                                [
                                    637.4144628685317,
                                    -371.501572615467
                                ],
                                [
                                    537.3629221259034,
                                    -297.9485155874863
                                ],
                                [
                                    362.67262475087773,
                                    -183.74338776618242
                                ],
                                [
                                    197.51190760784084,
                                    -90.91433231905103
                                ],
                                [
                                    120.60195964894956,
                                    -52.01342283282429
                                ],
                                [
                                    118.91059820359806,
                                    -55.43421153817326
                                ]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    362.67262475087773,
                                    -183.74338776618242
                                ],
                                [
                                    197.51190760784084,
                                    -90.91433231905103
                                ],
                                [
                                    158.12112418928882,
                                    -65.67478009033948
                                ],
                                [
                                    142.68293568259105,
                                    -45.06852611619979
                                ],
                                [
                                    135.9712366592139,
                                    -28.777733232825994
                                ],
                                [
                                    132.684275651176,
                                    -14.30917145870626
                                ],
                                [
                                    137.8017475529341,
                                    -13.61771634221077
                                ],
                                [
                                    140.74390690383734,
                                    -27.770826203748584
                                ],
                                [
                                    147.4138604705804,
                                    -43.37214694172144
                                ],
                                [
                                    161.42728643032024,
                                    -61.88382932450622
                                ],
                                [
                                    199.0122889878694,
                                    -87.70675852801651
                                ],
                                [
                                    345.9566527066636,
                                    -169.8531254865229
                                ],
                                [
                                    362.67262475087773,
                                    -183.74338776618242
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    115.22734667401528,
                                    -63.193462835624814
                                ],
                                [
                                    227.2205741875223,
                                    -120.83693976514041
                                ],
                                [
                                    395.4332379512489,
                                    -218.91724339220673
                                ],
                                [
                                    530.1730520018027,
                                    -308.562404721044
                                ],
                                [
                                    629.8837721864111,
                                    -381.7960853353143
                                ],
                                [
                                    627.9504478701274,
                                    -385.1334453076124
                                ],
                                [
                                    528.1258461243124,
                                    -311.7245090967044
                                ],
                                [
                                    393.3076447880012,
                                    -222.24247655738145
                                ],
                                [
                                    225.63613232941134,
                                    -124.20627369266003
                                ],
                                [
                                    113.4513862291933,
                                    -66.64918459579349
                                ],
                                [
                                    115.22734667401528,
                                    -63.193462835624814
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    113.4513862291933,
                                    -66.64918459579349
                                ],
                                [
                                    225.63613232941134,
                                    -124.20627369266003
                                ],
                                [
                                    393.3076447880012,
                                    -222.24247655738145
                                ],
                                [
                                    528.1258461243124,
                                    -311.7245090967044
                                ],
                                [
                                    627.9504478701274,
                                    -385.1334453076124
                                ],
                                [
                                    625.8340475181467,
                                    -388.2124215774238
                                ],
                                [
                                    525.9742620319012,
                                    -314.842709492892
                                ],
                                [
                                    393.88254722207785,
                                    -227.3482881207019
                                ],
                                [
                                    223.58338449295843,
                                    -128.0273137204349
                                ],
                                [
                                    111.88539303623838,
                                    -70.06441183015704
                                ],
                                [
                                    113.4513862291933,
                                    -66.64918459579349
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    393.88254722207785,
                                    -227.3482881207019
                                ],
                                [
                                    223.58338449295843,
                                    -128.0273137204349
                                ],
                                [
                                    192.26323484949535,
                                    -113.11643671337515
                                ],
                                [
                                    173.12065171304857,
                                    -110.46281152684242
                                ],
                                [
                                    156.6132822323707,
                                    -113.41854413133115
                                ],
                                [
                                    138.20514047151664,
                                    -122.68086718861014
                                ],
                                [
                                    129.72205294534797,
                                    -129.91261112876236
                                ],
                                [
                                    133.70443896419602,
                                    -133.39887781720608
                                ],
                                [
                                    141.736638714734,
                                    -126.64131337963045
                                ],
                                [
                                    158.16590475983685,
                                    -118.38563675433397
                                ],
                                [
                                    172.95008070126642,
                                    -115.7540500825271
                                ],
                                [
                                    191.0450799096143,
                                    -117.95953868981451
                                ],
                                [
                                    221.86966175981797,
                                    -131.18159038946033
                                ],
                                [
                                    365.73461041244445,
                                    -213.55968860723078
                                ],
                                [
                                    393.88254722207785,
                                    -227.3482881207019
                                ]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的列表
            lanes_polygons_53_60 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]

            # 更新playground53-60的轨迹数据
            input_file_53_60 = f'{index}_tracks.csv'
            output_file_53_60 = f'{index}_updated_tracks.csv'
            playground53_60.update_track_data(input_file_53_60, output_file_53_60, onramp_polygons_53_60, offramp_polygons_53_60, lanes_polygons_53_60)
            '''
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
            '''

        elif 61 <= index <= 72:

            # 获取playground61-72的xUtmOrigin和yUtmOrigin
            #recordings_meta_file_61_72 = f'./{index}_recordingMeta.csv'  
            #x_utm_origin_61_72, y_utm_origin_61_72 = get_utm_origin(recordings_meta_file_61_72)
            x_utm_origin_61_72, y_utm_origin_61_72 = 353013.5,5640508.6
            '''
            # 提取playground61-72 KML文件中的多边形
            onramp_polygons_61_72 = {
                'playground61-72_lane-4_OnRamp': (playground61_72.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground61-72_lane-4_OnRamp.kml',
                    ['lane-4.1', 'lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-5.1'],
                    x_utm_origin_61_72,
                    y_utm_origin_61_72
                ), -4)
            }

            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in onramp_polygons_61_72.items()
            }

            # 将数据保存到 JSON 文件中
            with open('onramp_polygons_61_72.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 onramp_polygons_61_72.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = {
                "playground61-72_lane-4_OnRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    206.2076705044601,
                                    -115.37323923502117
                                ],
                                [
                                    227.88828218803974,
                                    -115.57763012405485
                                ],
                                [
                                    250.43598903343081,
                                    -122.48490178119391
                                ],
                                [
                                    283.2511679963209,
                                    -142.53341248910874
                                ],
                                [
                                    281.1516709565767,
                                    -145.75687058549374
                                ],
                                [
                                    248.9384520109743,
                                    -126.29956251103431
                                ],
                                [
                                    226.94264434929937,
                                    -120.38067143782973
                                ],
                                [
                                    206.47340086544864,
                                    -120.21420096978545
                                ],
                                [
                                    206.2076705044601,
                                    -115.37323923502117
                                ]
                            ]
                        ]
                    },
                    -4
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            onramp_polygons_61_72 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }

            '''
            offramp_polygons_61_72 = {
                'playground61-72_lane5_OffRamp': (playground61_72.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground61-72_lane5_OffRamp.kml',
                    ['lane5.2', 'lane5.3', 'lane5.4', 'lane5.5', 'lane5.6', 'lane5.7', 'lane6.7', 'lane6.6', 'lane6.5', 'lane6.4', 'lane6.3', 'lane6.2'],
                    x_utm_origin_61_72,
                    y_utm_origin_61_72
                ), 5)
            }
        
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in offramp_polygons_61_72.items()
            }

            # 将数据保存到 JSON 文件中
            with open('offramp_polygons_61_72.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 offramp_polygons_61_72.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = {
                "playground61-72_lane5_OffRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    565.5234739436419,
                                    -310.9411968300119
                                ],
                                [
                                    534.8999565317063,
                                    -288.78701154422015
                                ],
                                [
                                    496.6148354165489,
                                    -261.2809901004657
                                ],
                                [
                                    260.54205231240485,
                                    -74.44542392715812
                                ],
                                [
                                    252.00208915304393,
                                    -59.33214652817696
                                ],
                                [
                                    248.52432821883122,
                                    -49.946176561526954
                                ],
                                [
                                    253.22605462610954,
                                    -49.89816542621702
                                ],
                                [
                                    255.99231852043886,
                                    -56.84220281802118
                                ],
                                [
                                    263.65351855778135,
                                    -71.50808530393988
                                ],
                                [
                                    499.32528877130244,
                                    -257.9632156332955
                                ],
                                [
                                    537.1020240220823,
                                    -285.77878213394433
                                ],
                                [
                                    567.9139405603055,
                                    -308.14936825819314
                                ],
                                [
                                    565.5234739436419,
                                    -310.9411968300119
                                ]
                            ]
                        ]
                    },
                    5
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            offramp_polygons_61_72 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }

            '''
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

            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_61_72
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_61_72.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 lanes_polygons_61_72.json 文件中")
            '''

            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    199.7528698508395,
                                    -58.88251463882625
                                ],
                                [
                                    421.8922060029581,
                                    -228.3810955826193
                                ],
                                [
                                    589.8540199060226,
                                    -356.57166468631476
                                ],
                                [
                                    592.8856647034409,
                                    -354.1953278807923
                                ],
                                [
                                    423.9843883778667,
                                    -225.4016336640343
                                ],
                                [
                                    201.73108322860207,
                                    -55.73038669489324
                                ],
                                [
                                    199.7528698508395,
                                    -58.88251463882625
                                ]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    201.73108322860207,
                                    -55.73038669489324
                                ],
                                [
                                    423.9843883778667,
                                    -225.4016336640343
                                ],
                                [
                                    592.8856647034409,
                                    -354.1953278807923
                                ],
                                [
                                    595.1826933711418,
                                    -351.4235248453915
                                ],
                                [
                                    426.1397002771264,
                                    -222.43411164637655
                                ],
                                [
                                    204.19483034696896,
                                    -52.6755635291338
                                ],
                                [
                                    201.73108322860207,
                                    -55.73038669489324
                                ]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    204.19483034696896,
                                    -52.6755635291338
                                ],
                                [
                                    426.1397002771264,
                                    -222.43411164637655
                                ],
                                [
                                    595.1826933711418,
                                    -351.4235248453915
                                ],
                                [
                                    597.9844595876639,
                                    -348.5840550046414
                                ],
                                [
                                    429.0937870767666,
                                    -219.4894353542477
                                ],
                                [
                                    206.5563710021088,
                                    -49.749009487219155
                                ],
                                [
                                    204.19483034696896,
                                    -52.6755635291338
                                ]
                            ]
                        ]
                    }
                ],
                [
                    4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    260.22034040943254,
                                    -90.38586152438074
                                ],
                                [
                                    429.0937870767666,
                                    -219.4894353542477
                                ],
                                [
                                    466.100724158925,
                                    -247.48745163250715
                                ],
                                [
                                    532.5083125162637,
                                    -291.61650065146387
                                ],
                                [
                                    563.268279851065,
                                    -313.83217592630535
                                ],
                                [
                                    596.5461311991094,
                                    -339.2740910788998
                                ],
                                [
                                    598.8085226374096,
                                    -336.30775270145386
                                ],
                                [
                                    565.5234739436419,
                                    -310.9411968300119
                                ],
                                [
                                    534.8999565317063,
                                    -288.78701154422015
                                ],
                                [
                                    468.6873936757911,
                                    -244.40049742907286
                                ],
                                [
                                    296.676552525023,
                                    -113.62161269597709
                                ],
                                [
                                    260.22034040943254,
                                    -90.38586152438074
                                ]
                            ]
                        ]
                    }
                ],
                [
                    5,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    598.8085226374096,
                                    -336.30775270145386
                                ],
                                [
                                    565.5234739436419,
                                    -310.9411968300119
                                ],
                                [
                                    534.8999565317063,
                                    -288.78701154422015
                                ],
                                [
                                    496.6148354165489,
                                    -261.2809901004657
                                ],
                                [
                                    260.54205231240485,
                                    -74.44542392715812
                                ],
                                [
                                    252.00208915304393,
                                    -59.33214652817696
                                ],
                                [
                                    248.52432821883122,
                                    -49.946176561526954
                                ],
                                [
                                    253.22605462610954,
                                    -49.89816542621702
                                ],
                                [
                                    255.99231852043886,
                                    -56.84220281802118
                                ],
                                [
                                    263.65351855778135,
                                    -71.50808530393988
                                ],
                                [
                                    499.32528877130244,
                                    -257.9632156332955
                                ],
                                [
                                    537.1020240220823,
                                    -285.77878213394433
                                ],
                                [
                                    567.9139405603055,
                                    -308.14936825819314
                                ],
                                [
                                    601.3802907891222,
                                    -333.87199932616204
                                ],
                                [
                                    598.8085226374096,
                                    -336.30775270145386
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    196.34060166415293,
                                    -63.266610086895525
                                ],
                                [
                                    419.1478538449155,
                                    -231.83256856910884
                                ],
                                [
                                    512.2971844507847,
                                    -302.25334256421775
                                ],
                                [
                                    587.6115253046155,
                                    -359.4205900076777
                                ],
                                [
                                    585.3774578514276,
                                    -362.6438646428287
                                ],
                                [
                                    510.1847485131584,
                                    -305.4217784088105
                                ],
                                [
                                    416.79674175276887,
                                    -234.69771222490817
                                ],
                                [
                                    194.09432631719392,
                                    -65.95914579648525
                                ],
                                [
                                    196.34060166415293,
                                    -63.266610086895525
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    194.09432631719392,
                                    -65.95914579648525
                                ],
                                [
                                    416.79674175276887,
                                    -234.69771222490817
                                ],
                                [
                                    510.1847485131584,
                                    -305.4217784088105
                                ],
                                [
                                    585.3774578514276,
                                    -362.6438646428287
                                ],
                                [
                                    583.5846246602596,
                                    -365.28971661347896
                                ],
                                [
                                    508.55773212667555,
                                    -307.7751582786441
                                ],
                                [
                                    415.0155542079592,
                                    -236.87643437180668
                                ],
                                [
                                    191.61249600618612,
                                    -68.93761909846216
                                ],
                                [
                                    194.09432631719392,
                                    -65.95914579648525
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    191.61249600618612,
                                    -68.93761909846216
                                ],
                                [
                                    415.0155542079592,
                                    -236.87643437180668
                                ],
                                [
                                    508.55773212667555,
                                    -307.7751582786441
                                ],
                                [
                                    583.5846246602596,
                                    -365.28971661347896
                                ],
                                [
                                    581.0525071910815,
                                    -368.12281759176403
                                ],
                                [
                                    506.23980621260125,
                                    -311.10373738687485
                                ],
                                [
                                    412.42346060601994,
                                    -240.28948007244617
                                ],
                                [
                                    189.47076355689205,
                                    -71.79049652069807
                                ],
                                [
                                    191.61249600618612,
                                    -68.93761909846216
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    206.2076705044601,
                                    -115.37323923502117
                                ],
                                [
                                    227.88828218803974,
                                    -115.57763012405485
                                ],
                                [
                                    250.43598903343081,
                                    -122.48490178119391
                                ],
                                [
                                    283.2511679963209,
                                    -142.53341248910874
                                ],
                                [
                                    412.42346060601994,
                                    -240.28948007244617
                                ],
                                [
                                    506.23980621260125,
                                    -311.10373738687485
                                ],
                                [
                                    581.0525071910815,
                                    -368.12281759176403
                                ],
                                [
                                    578.8145715391147,
                                    -370.9800532720983
                                ],
                                [
                                    503.87060799542814,
                                    -314.1458373051137
                                ],
                                [
                                    410.3676430612104,
                                    -243.32052029576153
                                ],
                                [
                                    281.1516709565767,
                                    -145.75687058549374
                                ],
                                [
                                    248.9384520109743,
                                    -126.29956251103431
                                ],
                                [
                                    226.94264434929937,
                                    -120.38067143782973
                                ],
                                [
                                    206.47340086544864,
                                    -120.21420096978545
                                ],
                                [
                                    206.2076705044601,
                                    -115.37323923502117
                                ]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的列表
            lanes_polygons_61_72 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]

            # 更新playground61-72的轨迹数据
            input_file_61_72 = f'{index}_tracks.csv'
            output_file_61_72 = f'{index}_updated_tracks.csv'
            playground61_72.update_track_data(input_file_61_72, output_file_61_72, onramp_polygons_61_72, offramp_polygons_61_72, lanes_polygons_61_72)
            '''
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
            '''


        elif 73 <= index <= 77:

            # 获取playground73-77的xUtmOrigin和yUtmOrigin
            #recordings_meta_file_73_77 = f'./{index}_recordingMeta.csv'  
            #x_utm_origin_73_77, y_utm_origin_73_77 = get_utm_origin(recordings_meta_file_73_77)
            x_utm_origin_73_77, y_utm_origin_73_77 = 293790.2,5632271.9
            '''
            # 提取playground73-77 KML文件中的多边形
            onramp_polygons_73_77 = {
                'playground73-77_lane-3_2_OnRamp': (playground73_77.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground73-77_lane-3_2_OnRamp.kml',
                    ['lane-3.3', 'lane-3.4', 'lane-3.5', 'lane-3.6', 'lane-3.7', 'lane-3.8', 'lane-3.9', 'lane-4.9', 'lane-4.8', 'lane-4.7', 'lane-4.6', 'lane-4.5', 'lane-4.4', 'lane-4.3'],
                    x_utm_origin_73_77,
                    y_utm_origin_73_77
                ), -3)
            }
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in onramp_polygons_73_77.items()
            }

            # 将数据保存到 JSON 文件中
            with open('onramp_polygons_73_77.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 onramp_polygons_73_77.json 文件中")
            '''

            # 提供的 JSON 数据
            json_data = {
                "playground73-77_lane-3_2_OnRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    456.2317980565713,
                                    -230.84965080209076
                                ],
                                [
                                    398.654124442779,
                                    -224.20319501776248
                                ],
                                [
                                    290.4496003231616,
                                    -214.50107068102807
                                ],
                                [
                                    249.25741549010854,
                                    -217.04836969822645
                                ],
                                [
                                    206.75857236643787,
                                    -231.63568141777068
                                ],
                                [
                                    173.74861418554792,
                                    -256.21120259538293
                                ],
                                [
                                    141.11146027914947,
                                    -297.3545501260087
                                ],
                                [
                                    147.84526016603922,
                                    -298.2768837790936
                                ],
                                [
                                    175.26814870012458,
                                    -263.56742668151855
                                ],
                                [
                                    249.52515570342075,
                                    -222.58917430602014
                                ],
                                [
                                    290.18457668164046,
                                    -219.91098031308502
                                ],
                                [
                                    398.3033586781821,
                                    -229.70171984098852
                                ],
                                [
                                    455.70584721810883,
                                    -235.1164313852787
                                ],
                                [
                                    456.2317980565713,
                                    -230.84965080209076
                                ]
                            ]
                        ]
                    },
                    -3
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            onramp_polygons_73_77 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }

            '''
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
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_73_77
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_73_77.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 lanes_polygons_73_77.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    166.84985236852663,
                                    -164.25414068624377
                                ],
                                [
                                    344.07220963336295,
                                    -202.62857048865408
                                ],
                                [
                                    489.090756805439,
                                    -220.6836821725592
                                ],
                                [
                                    620.8615620149649,
                                    -227.58154553174973
                                ],
                                [
                                    621.4395065055578,
                                    -223.57716563623399
                                ],
                                [
                                    489.2294118743739,
                                    -216.86048901546746
                                ],
                                [
                                    345.02561524457997,
                                    -198.995265125297
                                ],
                                [
                                    167.30390963266836,
                                    -160.7638707952574
                                ],
                                [
                                    166.84985236852663,
                                    -164.25414068624377
                                ]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    167.30390963266836,
                                    -160.7638707952574
                                ],
                                [
                                    345.02561524457997,
                                    -198.995265125297
                                ],
                                [
                                    489.2294118743739,
                                    -216.86048901546746
                                ],
                                [
                                    621.4395065055578,
                                    -223.57716563623399
                                ],
                                [
                                    622.3515688145417,
                                    -219.94125907029957
                                ],
                                [
                                    571.7737211478525,
                                    -218.10255759675056
                                ],
                                [
                                    489.89572577376384,
                                    -213.20237041916698
                                ],
                                [
                                    346.0360416874173,
                                    -195.26769498363137
                                ],
                                [
                                    168.10345733637223,
                                    -156.53046164754778
                                ],
                                [
                                    167.30390963266836,
                                    -160.7638707952574
                                ]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    168.10345733637223,
                                    -156.53046164754778
                                ],
                                [
                                    346.0360416874173,
                                    -195.26769498363137
                                ],
                                [
                                    489.89572577376384,
                                    -213.20237041916698
                                ],
                                [
                                    571.7737211478525,
                                    -218.10255759675056
                                ],
                                [
                                    525.331442024908,
                                    -212.000446354039
                                ],
                                [
                                    346.79337047907757,
                                    -191.32299136463553
                                ],
                                [
                                    169.34480862511555,
                                    -152.56562845315784
                                ],
                                [
                                    168.10345733637223,
                                    -156.53046164754778
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    165.8751812191913,
                                    -169.2845778465271
                                ],
                                [
                                    343.19874894974055,
                                    -207.86667210701853
                                ],
                                [
                                    488.6729970804299,
                                    -225.92117277905345
                                ],
                                [
                                    620.0126073542051,
                                    -232.8105358676985
                                ],
                                [
                                    619.2597756969626,
                                    -236.72883277572691
                                ],
                                [
                                    488.37395921879215,
                                    -229.7740030111745
                                ],
                                [
                                    342.5917526424746,
                                    -211.65504547115415
                                ],
                                [
                                    164.88852937245974,
                                    -173.04342979285866
                                ],
                                [
                                    165.8751812191913,
                                    -169.2845778465271
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    164.88852937245974,
                                    -173.04342979285866
                                ],
                                [
                                    342.5917526424746,
                                    -211.65504547115415
                                ],
                                [
                                    488.37395921879215,
                                    -229.7740030111745
                                ],
                                [
                                    619.2597756969626,
                                    -236.72883277572691
                                ],
                                [
                                    617.8033289198647,
                                    -240.17581957112998
                                ],
                                [
                                    488.1390988982166,
                                    -233.76189156528562
                                ],
                                [
                                    342.0308746805531,
                                    -215.48386460356414
                                ],
                                [
                                    164.03853953600628,
                                    -176.75943206064403
                                ],
                                [
                                    164.88852937245974,
                                    -173.04342979285866
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    164.03853953600628,
                                    -176.75943206064403
                                ],
                                [
                                    305.5049174751621,
                                    -209.1492570033297
                                ],
                                [
                                    259.01487428491237,
                                    -204.2803290626034
                                ],
                                [
                                    162.82017994992202,
                                    -181.3672174885869
                                ],
                                [
                                    164.03853953600628,
                                    -176.75943206064403
                                ]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    617.8033289198647,
                                    -240.17581957112998
                                ],
                                [
                                    488.1390988982166,
                                    -233.76189156528562
                                ],
                                [
                                    456.2317980565713,
                                    -230.84965080209076
                                ],
                                [
                                    398.654124442779,
                                    -224.20319501776248
                                ],
                                [
                                    290.4496003231616,
                                    -214.50107068102807
                                ],
                                [
                                    249.25741549010854,
                                    -217.04836969822645
                                ],
                                [
                                    206.75857236643787,
                                    -231.63568141777068
                                ],
                                [
                                    173.74861418554792,
                                    -256.21120259538293
                                ],
                                [
                                    141.11146027914947,
                                    -297.3545501260087
                                ],
                                [
                                    147.84526016603922,
                                    -298.2768837790936
                                ],
                                [
                                    175.26814870012458,
                                    -263.56742668151855
                                ],
                                [
                                    249.52515570342075,
                                    -222.58917430602014
                                ],
                                [
                                    290.18457668164046,
                                    -219.91098031308502
                                ],
                                [
                                    398.3033586781821,
                                    -229.70171984098852
                                ],
                                [
                                    455.70584721810883,
                                    -235.1164313852787
                                ],
                                [
                                    487.5451225893339,
                                    -237.9811628786847
                                ],
                                [
                                    576.3207039347035,
                                    -242.95893792249262
                                ],
                                [
                                    617.8033289198647,
                                    -240.17581957112998
                                ]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的列表
            lanes_polygons_73_77 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]
            # 更新playground73-77的轨迹数据
            input_file_73_77 = f'{index}_tracks.csv'
            output_file_73_77 = f'{index}_updated_tracks.csv'
            playground73_77.update_track_data(input_file_73_77, output_file_73_77, onramp_polygons_73_77, {}, lanes_polygons_73_77)
            '''
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
            '''
        elif 78 <= index <= 92:
            # 获取playground78-92的xUtmOrigin和yUtmOrigin
            #recordings_meta_file_78_92 = f'./{index}_recordingMeta.csv'  
            #x_utm_origin_78_92, y_utm_origin_78_92 = get_utm_origin(recordings_meta_file_78_92)
            x_utm_origin_78_92, y_utm_origin_78_92 = 325298.1,5635819.6
            '''
            # 提取playground78-92 KML文件中的多边形
            onramp_polygons_78_92 = {
                'playground78-92_lane-4_OnRamp': (playground78_92.extract_polygon_from_kml(
                    './scenario_mining/exiD_scenario_mining/playground78-92_lane-4_OnRamp.kml',
                    ['lane-4.2', 'lane-4.3', 'lane-4.4', 'lane-5.4', 'lane-5.3', 'lane-5.2', 'lane-4.2'],
                    x_utm_origin_78_92,
                    y_utm_origin_78_92
                ), -4)
            }
            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = {
                key: (mapping(polygon), value) for key, (polygon, value) in onramp_polygons_78_92.items()
            }

            # 将数据保存到 JSON 文件中
            with open('onramp_polygons_78_92.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 onramp_polygons_78_92.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = {
                "playground78-92_lane-4_OnRamp": [
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    229.09799224347807,
                                    -192.7720360942185
                                ],
                                [
                                    181.52490168676013,
                                    -182.55082058161497
                                ],
                                [
                                    142.16098015318858,
                                    -178.19536578841507
                                ],
                                [
                                    142.02600464527495,
                                    -182.1322208782658
                                ],
                                [
                                    181.17362394125666,
                                    -186.88141773920506
                                ],
                                [
                                    228.2494398506824,
                                    -196.0396619811654
                                ],
                                [
                                    229.09799224347807,
                                    -192.7720360942185
                                ]
                            ]
                        ]
                    },
                    -4
                ]
            }

            # 将 JSON 数据转换为包含 Polygon 对象的字典
            onramp_polygons_78_92 = {
                key: (shape(polygon_dict), value) for key, (polygon_dict, value) in json_data.items()
            }

            '''
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

            # 将Polygon对象转换为GeoJSON格式的字典，并准备保存的数据结构
            save_data = [
                (index, mapping(polygon)) for index, polygon in lanes_polygons_78_92
            ]

            # 将数据保存到 JSON 文件中
            with open('lanes_polygons_78_92.json', 'w') as f:
                json.dump(save_data, f, indent=4)

            print("数据已保存到 lanes_polygons_78_92.json 文件中")
            '''
            # 提供的 JSON 数据
            json_data = [
                [
                    1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [161.71666925644968, -158.77304366137832],
                                [263.6138481046655, -183.71928334981203],
                                [398.96226431406103, -202.68468141369522],
                                [531.6694073449471, -205.8734359620139],
                                [625.6525993812247, -199.49685859773308],
                                [625.4627091660514, -196.0492461901158],
                                [532.088232494425, -202.46224755141884],
                                [399.58306589064887, -199.18671039678156],
                                [264.640748057398, -180.22710664570332],
                                [162.73014204425272, -155.7763953730464],
                                [161.71666925644968, -158.77304366137832]
                            ]
                        ]
                    }
                ],
                [
                    2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [162.73014204425272, -155.7763953730464],
                                [264.640748057398, -180.22710664570332],
                                [399.58306589064887, -199.18671039678156],
                                [532.088232494425, -202.46224755141884],
                                [625.4627091660514, -196.0492461901158],
                                [625.4696691671852, -192.5553435496986],
                                [532.0676969599444, -199.08497660420835],
                                [400.24862387333997, -195.62047519814223],
                                [265.35720851202495, -177.179349033162],
                                [163.91759377671406, -152.42154890764505],
                                [162.73014204425272, -155.7763953730464]
                            ]
                        ]
                    }
                ],
                [
                    3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [163.91759377671406, -152.42154890764505],
                                [265.35720851202495, -177.179349033162],
                                [400.24862387333997, -195.62047519814223],
                                [532.0676969599444, -199.08497660420835],
                                [625.4696691671852, -192.5553435496986],
                                [625.2222583608236, -188.38682702928782],
                                [532.350844241213, -194.91189060360193],
                                [400.7411521091708, -191.63252855557948],
                                [266.2927190720802, -173.01897241640836],
                                [164.9983187520411, -148.442154398188],
                                [163.91759377671406, -152.42154890764505]
                            ]
                        ]
                    }
                ],
                [
                    4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [164.9983187520411, -148.442154398188],
                                [266.2927190720802, -173.01897241640836],
                                [240.26121517666616, -164.38445562962443],
                                [166.23630215507, -144.84157807473093],
                                [164.9983187520411, -148.442154398188]
                            ]
                        ]
                    }
                ],
                [
                    -1,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [160.1264579782728, -163.49117635190487],
                                [262.6576433563605, -188.74107418674976],
                                [398.7658353461884, -207.45197968930006],
                                [531.9735133151407, -210.69477769266814],
                                [626.1242311465903, -204.48631690908223],
                                [626.3111792387208, -207.93537582550198],
                                [532.1494449793827, -214.42946713324636],
                                [398.3418601072044, -211.0580907696858],
                                [262.1637209067121, -192.0681145451963],
                                [159.0023594504455, -166.78651167824864],
                                [160.1264579782728, -163.49117635190487]
                            ]
                        ]
                    }
                ],
                [
                    -2,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [159.0023594504455, -166.78651167824864],
                                [262.1637209067121, -192.0681145451963],
                                [398.3418601072044, -211.0580907696858],
                                [532.1494449793827, -214.42946713324636],
                                [626.3111792387208, -207.93537582550198],
                                [626.3239339536522, -211.70998435094953],
                                [532.1273266393691, -218.0581733621657],
                                [397.9349996271194, -214.3602666668594],
                                [261.4752896595164, -195.48493790999055],
                                [157.84891748533119, -170.24914437253028],
                                [159.0023594504455, -166.78651167824864]
                            ]
                        ]
                    }
                ],
                [
                    -3,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [157.84891748533119, -170.24914437253028],
                                [261.4752896595164, -195.48493790999055],
                                [397.9349996271194, -214.3602666668594],
                                [532.1273266393691, -218.0581733621657],
                                [626.3239339536522, -211.70998435094953],
                                [626.9010350959143, -215.48258580546826],
                                [538.2421960920328, -221.87179120071232],
                                [445.8501973710372, -221.53589808475226],
                                [397.5169586263364, -218.44168304745108],
                                [260.570892135147, -199.28493526671082],
                                [229.09799224347807, -192.7720360942185],
                                [156.9676248668693, -173.905443739146],
                                [157.84891748533119, -170.24914437253028]
                            ]
                        ]
                    }
                ],
                [
                    -4,
                    {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [445.8501973710372, -221.53589808475226],
                                [397.5169586263364, -218.44168304745108],
                                [260.570892135147, -199.28493526671082],
                                [229.09799224347807, -192.7720360942185],
                                [181.52490168676013, -182.55082058161497],
                                [142.16098015318858, -178.19536578841507],
                                [142.02600464527495, -182.1322208782658],
                                [181.17362394125666, -186.88141773920506],
                                [228.2494398506824, -196.0396619811654],
                                [260.0472922104527, -202.36944045033306],
                                [397.35230419121217, -221.4818561039865],
                                [424.1873057843768, -222.62427121121436],
                                [445.8501973710372, -221.53589808475226]
                            ]
                        ]
                    }
                ]
            ]

            # 将 JSON 数据转换为包含 Polygon 对象的列表
            lanes_polygons_78_92 = [
                (index, shape(polygon_dict)) for index, polygon_dict in json_data
            ]


            # 更新playground78-92的轨迹数据
            input_file_78_92 = f'{index}_tracks.csv'
            output_file_78_92 = f'{index}_updated_tracks.csv'
            playground78_92.update_track_data(input_file_78_92, output_file_78_92, onramp_polygons_78_92, {}, lanes_polygons_78_92)
            '''
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
            '''

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


def get_activity_from_LLM_response_ExitD_Ramp(LLM_response):
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
    req_ego_rampAct = LLM_response['Ego Vehicle']['Ego ramp activity'][0]

    req_tgt_rampAct = LLM_response['Target Vehicle #1']['Target ramp activity'][0]

    return  req_ego_rampAct, req_tgt_rampAct

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
            if req_ego_latAct == 'on-ramp':
                #这里需要写一个函数，需要连续找到'on-ramp'和'lane change left',在完成'lane change left'完成的下一帧，跟find_start_end_frame_of_latAct函数
                #中的endFrame = curr_latActs.iloc[index+1]['frame']一样，找到这里的[区间的egoLatActFra]。这里还有一个问题就是还没有给完成lane change left
                #后的第一帧打上follow lane，明天记得打上。
            else:
                egoLatActFram = find_start_end_frame_of_latAct(curr_ego_latActs, req_ego_latAct)
            #egoLatActFram = find_start_end_frame_of_latAct(curr_ego_latActs, req_ego_latAct)

            # Check the ego vehicle ramp activity
            '''
            curr_ego_rampActs = tracks_36[tracks_36['trackId'] == curr_ego]['activity_type'].unique()
            if req_ego_rampAct not in curr_ego_rampActs:
                continue
            '''
            tgt_list = []
            for curr_interact_tgt in curr_interact_tgts:
                if curr_interact_tgt == -1 or curr_interact_tgt not in latActDict or curr_interact_tgt not in longActDict:
                    continue

                # Judge the target vehicle lateral activity
                curr_interact_tgt_latAct = latActDict[curr_interact_tgt]
                if req_tgt_latAct not in curr_interact_tgt_latAct['LateralActivity'].values:
                    continue
                tgtLatActFram = find_start_end_frame_of_latAct(curr_interact_tgt_latAct, req_tgt_latAct)
                '''
                # Check the target vehicle ramp activity
                curr_tgt_rampActs = tracks_36[tracks_36['trackId'] == curr_interact_tgt]['activity_type'].unique()
                if req_tgt_rampAct not in curr_tgt_rampActs:
                    continue
                '''
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
                curr_tgt_pos_start = pos_calc(laneDiffStart, ego_drive_direction, delta_x_tgt_ego_start, req_tgt_startPos_type)

                # If current target vehicle was not once the leadId of the current ego vehicle, then skip
                if curr_interact_tgt not in curr_ego_life['leadId'].values:
                    continue

                if curr_tgt_pos_start == req_tgt_startPos:  # Judge the start position
                    # Calculate the target vehicle position at end
                    delta_x_tgt_ego_end = curr_tgt_end_row['xCenter'][0] - curr_ego_end_row['xCenter'][0]
                    laneDiffEnd = curr_tgt_end_lane - curr_ego_end_lane
                    curr_tgt_pos_end = pos_calc(laneDiffEnd, ego_drive_direction, delta_x_tgt_ego_end, req_tgt_endPos_type)
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
    else:
        req_ego_rampAct, req_tgt_rampAct = get_activity_from_LLM_response_ExitD_Ramp(key_label)
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


#file_path = '39_tracks.csv'
#select_playground(file_path)

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

response = """
{'Ego Vehicle': {'Ego longitudinal activity': ['deceleration'], 
    'Ego lateral activity': ['off-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'adjacent lane': ['right adjacent lane']}, 
    'Target end position': {'rear': ['right rear']}, 
    'Target behavior': {'target longitudinal activity': ['deceleration'], 
    'target lateral activity': ['follow lane']}}}
    """
'''
# Ego vehicle was trying to on-ramp; The ego vehicle has to watch out the vehicles driving on the highway
response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['acceleration'], 
    'Ego lateral activity': ['on-ramp']}, 
    'Target Vehicle #1': {'Target start position': {'rear': ['left rear']}, 
    'Target end position': {'same lane': ['behind']}, 
    'Target behavior': {'target longitudinal activity': ['acceleration'], 
    'target lateral activity': ['follow lane']}}}"""
# for cut in

response =""" {'Ego Vehicle': {'Ego longitudinal activity': ['acceleration'], 

  'Ego lateral activity': ['on-ramp']}, 

  'Target Vehicle #1': {'Target start position': {'same lane': ['behind']}, 

  'Target end position': {'same lane': ['behind']}, 

  'Target behavior': {'target longitudinal activity': ['acceleration'], 

  'target lateral activity': ['on-ramp']}}}"""

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
scenarioList = mainFunctionScenarioIdentification_ExitD(tracks_original, key_label, latActDict, longActDict, interactIdDict, progress_bar)
print(scenarioList)                        
