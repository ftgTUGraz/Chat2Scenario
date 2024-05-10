import xml.etree.ElementTree as ET
import math
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd

def calculate_width(ds, a, b, c, d):
    """ Calculate the width based on polynomial coefficients and distance along the road """
    return a + b * ds + c * (ds**2) + d * (ds**3)

def find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_ids):
    num_roads = len(set(road_ids))  # 道路的数量
    unique_road_ids = set(road_ids)  # 创建集合，移除重复项，无序
    sorted_road_ids = sorted(unique_road_ids)  # 对集合中的元素排序
    nearest_endpoints_per_road = {str(road_id): [] for road_id in sorted_road_ids}

    for i in range(len(x_endpoints)):
        current_road_id = str(road_ids[i])  # 使用字符串类型作为键
        nearest_distances = sorted(
            [(j, math.sqrt((x_endpoints[i] - x_endpoints[j])**2 + (y_endpoints[i] - y_endpoints[j])**2))
            for j in range(len(x_endpoints)) if str(road_ids[j]) != current_road_id],
            key=lambda x: x[1]
        )
        if current_road_id == '1' and i==3 :
            nearest_distances[0] = (6,math.sqrt((x_endpoints[i] - x_endpoints[6])**2 + (y_endpoints[i] - y_endpoints[6])**2))

        # 为每条道路记录最近的两个端点，包括距离
        if nearest_distances:
            nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[0][0], nearest_distances[0][1]))

    # 确保选择的两个端点不是同一个起始端点
    two_nearest_endpoints_per_road = {}
    polygan_jonctions = []
    cpt = 1
    for road_id, endpoints_info in nearest_endpoints_per_road.items():
        unique_indices = set()
        selected_endpoints = []
        for info in sorted(endpoints_info, key=lambda x: x[2]):  # 按距离排序
            if info[0] not in unique_indices:
                selected_endpoints.append(info)
                unique_indices.add(info[0])
            if len(selected_endpoints) == 2:
                break
        two_nearest_endpoints_per_road[road_id] = selected_endpoints
        first_elements = [endpoint[0] for endpoint in selected_endpoints]
        sorted_elements = sorted(first_elements)
        if cpt == 1:
            polygan_jonctions.append((x_endpoints[sorted_elements[0]],y_endpoints[sorted_elements[0]]))
            cpt += 1
        polygan_jonctions.append((x_endpoints[sorted_elements[1]],y_endpoints[sorted_elements[1]]))
        for first,seconds,third in selected_endpoints:
            if first == sorted_elements[1]:
                polygan_jonctions.append((x_endpoints[seconds],y_endpoints[seconds]))


    return two_nearest_endpoints_per_road , polygan_jonctions


def connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids):
    # 用于存储连接的集合，格式为：(endpoint_index, connected_endpoint_index)
    connections = []
    connected_indices = set()  # 用来存储已经连接过的端点
    
    # 遍历每条道路的两个最近端点
    for road_id, endpoints_info in two_nearest_endpoints_per_road.items():
        for endpoint_info in endpoints_info:
            start_index, end_index, _ = endpoint_info
            # 检查端点是否已经被连接过
            if start_index not in connected_indices and end_index not in connected_indices:
                connections.append((start_index, end_index))
                connected_indices.update([start_index, end_index])  # 添加端点到已连接集合中
    
    return connections



def process_opendrive_file(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    previous_lane_coords ={}
    plt.figure(figsize=(10, 5))
    road_lane_paths = {} 
    x_endpoints = []
    y_endpoints = []
    road_endpoint_ids = []

    # 提取关心的道路ID列表
    road_ids_of_interest = {'1', '2', '3'}

    for road in root.findall('road'):
        road_id = road.get('id')
        if road_id in road_ids_of_interest:
            print(f"Processing road ID: {road_id}")
            previous_lane_coords[int(road_id)] = {}
            road_lane_paths[int(road_id)] = {}
            for geometry in road.findall('.//geometry'):
                param_poly3 = geometry.find('.//paramPoly3')

                if param_poly3 is not None:
                    #等到遇到param_poly3类型且一条road中不止两条lane的时候再补充
                    #如果遇到param_poly3类型且一条road中两条lane的时候可以用FrenetToGlobal_jonctions.py这个代码
                    print("This is a paramPoly3 type geometry.")
                else:
                    print("This is a line type geometry.")
                    x = float(geometry.get('x'))
                    y = float(geometry.get('y'))
                    hdg = float(geometry.get('hdg'))
                    length = float(geometry.get('length'))
                    points = np.linspace(0, length, num=1000)
                    lane_line_x = [x + point * math.cos(hdg) for point in points]
                    lane_line_y = [y + point * math.sin(hdg) for point in points]
                    plt.plot(lane_line_x, lane_line_y, 'k--', label='Center Lane')
                    previous_lane_coords[int(road_id)][0] = (lane_line_x, lane_line_y)
                    #plt.plot(lane_line_x1, lane_line_y1, 'k--', label='Center Lane')  

                    accumulated_widths = [0] * (len(points) + 1)
                    accumulated_widths2 = [0] * (len(points) + 1)
                    compte1 = 0
                    compte = 0
                    for laneSection in road.findall('.//laneSection'):
                        if compte1 == 0:
                            ls_s = float(laneSection.get('s'))
                            lanes_data = []
                            driving_lanes = []
                            compte += 1
                            for lane in laneSection.findall('.//lane'):
                                lane_id = int(lane.get('id'))
                                lane_type = lane.get('type')
                                if lane_type == "driving" or lane_type == "median":
                                    width_data = []

                                    for widthElement in lane.findall('.//width'):
                                        sOffset = float(widthElement.get('sOffset'))
                                        a = float(widthElement.get('a'))
                                        b = float(widthElement.get('b'))
                                        c = float(widthElement.get('c'))
                                        d = float(widthElement.get('d'))
                                        s = sOffset + ls_s
                                        #s =  - (ls_s +  sOffset )

                                        lane_widths = [calculate_width(point + s, a, b, c, d) for point in points]
                                        width_data.append(lane_widths)

                                    lanes_data.append((lane_id, width_data))

                                    if lane_type == "driving":
                                        driving_lanes.append((lane_id, width_data))

                            # 对车道按照ID进行排序，负数ID递减，正数ID递增
                            driving_lanes.sort(key=lambda x: x[0])
                            positive_lanes = sorted((lane for lane in lanes_data if lane[0] > 0), key=lambda x: x[0])
        
                            negative_lanes = sorted((lane for lane in lanes_data if lane[0] < 0), key=lambda x: x[0], reverse=True)

                            min_lane_id, max_lane_id = driving_lanes[0][0], driving_lanes[-1][0]

                            # 处理排序后的车道数据
                            accumulated_widths = np.zeros(len(points))
                            accumulated_widths2 = np.zeros(len(points))
                            for lanes_data in [positive_lanes, negative_lanes]:
                                for lane_id, all_widths in lanes_data:
                                    lane_line_x = []
                                    lane_line_y = []
                                    current_lane_x  = []
                                    current_lane_y  = []
                                    next_lane_x = []
                                    next_lane_y = []

                                    for index, width_at_point in enumerate(all_widths[0]):  # Assuming one width segment per lane for simplicity
                                        center_x = x + points[index] * math.cos(hdg)
                                        center_y = y + points[index] * math.sin(hdg)

                                        if lane_id > 0:
                                            accumulated_widths[index] += width_at_point
                                            point_width_x = center_x - accumulated_widths[index] * math.sin(hdg)
                                            point_width_y = center_y + accumulated_widths[index] * math.cos(hdg)
                                        else:
                                            accumulated_widths2[index] -= width_at_point
                                            point_width_x = center_x - accumulated_widths2[index] * math.sin(hdg)
                                            point_width_y = center_y + accumulated_widths2[index] * math.cos(hdg)

                                        lane_line_x.append(point_width_x)
                                        lane_line_y.append(point_width_y)

                                        if lane_id == min_lane_id or lane_id == max_lane_id:
                                            if ((index==0 and compte ==1) or (index == len(all_widths[0])-1 and compte ==1)):
                                                x_endpoints.append(point_width_x)
                                                y_endpoints.append(point_width_y)
                                                road_endpoint_ids.append(road_id)

                                    plt.plot(lane_line_x, lane_line_y, label=f"Lane ID {lane_id}")
                                    
                                    previous_lane_coords[int(road_id)][lane_id] = (lane_line_x, lane_line_y)
                        compte1 += 1


    # 创建多边形补丁
    for road_id, lanes in previous_lane_coords.items():
        lane_ids = sorted(lanes.keys())
        for i in range(len(lane_ids) - 1):
            lane_id = lane_ids[i]
            #人为设置数字最小lane是1
            lane_id_call = i + 1
            next_lane_id = lane_ids[i + 1]
            current_lane_x, current_lane_y = lanes[lane_id]
            next_lane_x, next_lane_y = lanes[next_lane_id]

            # 创建多边形路径
            path_vertices = list(zip(current_lane_x, current_lane_y)) + list(zip(reversed(next_lane_x), reversed(next_lane_y)))
            codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
            path = Path(path_vertices, codes)
            patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
            plt.gca().add_patch(patch)

            road_lane_paths[int(road_id)][lane_id_call] = path
      
     # 计算每条道路与其他道路最近的两个端点
    two_nearest_endpoints_per_road , polygan_jonctions = find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_endpoint_ids)

    # 创建连接
    connections = connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids)

    # 绘制连接
    for connection in connections:
        plt.plot([x_endpoints[connection[0]], x_endpoints[connection[1]]],
                [y_endpoints[connection[0]], y_endpoints[connection[1]]], 'r-')

    # 绘制用于连接的端点
    for road_id, nearest_endpoints in two_nearest_endpoints_per_road.items():
        for endpoint_info in nearest_endpoints:
            endpoint_index = endpoint_info[0]
            plt.scatter(x_endpoints[endpoint_index], y_endpoints[endpoint_index], c='blue')
    '''
    # 创建jonctions的polygan
    # 创建多边形顶点列表，确保是二维的
    path_vertices = polygan_jonctions
    codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(path_vertices, codes)
    patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
    plt.gca().add_patch(patch)
    road_lane_paths[100] = {}
    road_lane_paths[100][1] = path
    '''


    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Visualization of Roads and Lanes")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

    return road_lane_paths

def find_lane_by_coordinates(road_lane_paths, x, y):
    """ Given a point (x, y), determine the road and lane ID it belongs to. """
    for road_id, lanes in road_lane_paths.items():
        for lane_id, path in lanes.items():
            if path.contains_point((x, y)):
                return road_id, lane_id
    return 100, 1  # 如果没有找到匹配的车道，返回 -1,1，这里代表在jonctions中

def update_tracks_with_lane_info(csv_path, opendrive_file_path):
    # 读取 CSV 文件
    tracks_meta_df = pd.read_csv(csv_path)

    # 处理 OpenDRIVE 文件
    road_lane_paths = process_opendrive_file(opendrive_file_path)

    # 新增列
    tracks_meta_df['road_lane'] = ''

    # 逐行处理 DataFrame
    for index, row in tracks_meta_df.iterrows():
        x, y = row['xCenter'], row['yCenter']
        road_id, lane_id = find_lane_by_coordinates(road_lane_paths, x, y)
        tracks_meta_df.at[index, 'road_lane'] = f'{road_id}.{lane_id}'

    # 保存修改后的 DataFrame
    #updated_csv_path = csv_path.replace('.csv', '_updated.csv')
    #tracks_meta_df.to_csv(updated_csv_path, index=False)

    # 返回更新后的 DataFrame 路径
    return tracks_meta_df

def extract_road_id(road_lane):
    """ Extracts the road ID from a 'road.lane' string. """
    return int(road_lane.split('.')[0]) if '.' in road_lane else None
def determine_turn_type(path):
    """ Determines the turning type based on specific pairs of road IDs before and after '100.1'. """
    # Convert path elements to strings for consistent comparison
    path = [str(item) for item in path]

    # Check for a valid path length
    if len(path) < 2:
        return "N/A"

    # Extract the first and last road IDs in the path
    first_road_id = int(path[0].split('.')[0])
    last_road_id = int(path[-1].split('.')[0])

    # New rules for turn determination based on specific pairs of road IDs
    if (first_road_id, last_road_id) in [(1, 2), (2, 1)]:
        return "straight"
    elif (first_road_id, last_road_id) in [(1, 3)]:
        return "left"
    elif (first_road_id, last_road_id) in [(2, 3), (3, 1)]:
        return "right"
    elif (first_road_id, last_road_id) in [(3, 2)]:
        return "left"

    return "N/A"

def process_tracks(df):
    #df = pd.read_csv(file_path)
    df.sort_values(by=['trackId', 'frame'], inplace=True)
    grouped = df.groupby('trackId')['road_lane'].apply(list).reset_index()
    grouped['unique_path'] = grouped['road_lane'].apply(lambda x: [k for i, k in enumerate(x) if i == 0 or k != x[i-1]])
    grouped['turn_type'] = grouped['unique_path'].apply(determine_turn_type)
    result = grouped[['trackId', 'unique_path', 'turn_type']]
    #result.to_csv('30_processed_tracks.csv', index=False)

    grouped['turn_type'] = grouped['unique_path'].apply(determine_turn_type)
    turn_type_dict = grouped.set_index('trackId')['turn_type'].to_dict()
    df['turn_type'] = df['trackId'].map(turn_type_dict)

    return df
    
