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
        if current_road_id == '5' and i==53 :
            nearest_distances[0] = (23,math.sqrt((x_endpoints[i] - x_endpoints[23])**2 + (y_endpoints[i] - y_endpoints[23])**2))

        # 为每条道路记录最近的两个端点，包括距离
        if nearest_distances and i!=24 and i!=23:
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

def plot_polygon_from_indices(road_lane_paths,x_endpoints, y_endpoints, indices, color='orange', label='Polygon'):
    """ 根据提供的端点索引绘制多边形 """
    x_coords = [x_endpoints[i] for i in indices]
    y_coords = [y_endpoints[i] for i in indices]
    path_vertices = list(zip(x_coords, y_coords))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(indices) - 2) + [Path.CLOSEPOLY]
    path = Path(path_vertices, codes)
    patch = PathPatch(path, facecolor=color, edgecolor='black', alpha=0.5, label=label)
    plt.gca().add_patch(patch)
    road_lane_paths[6][100] = path



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
    road_ids_of_interest = {'0', '5', '6'}

    for road in root.findall('road'):
        road_id = road.get('id')
        if road_id in road_ids_of_interest:
            print(f"Processing road ID: {road_id}")
            previous_lane_coords[int(road_id)] = {}
            road_lane_paths[int(road_id)] = {}
            compte1 = 0
            compte = 0
            geometry_ranges = []
            max_s = 0
            geometry_data = []
            geometry_index = 0
            for geometry in road.findall('.//geometry'):
                s_start = float(geometry.get('s'))
                x = float(geometry.get('x'))
                y = float(geometry.get('y'))
                hdg = float(geometry.get('hdg'))
                length = float(geometry.get('length'))
                max_s = max(max_s, s_start + length)
                geometry_ranges.append((s_start, s_start + length, geometry))

                # 检查是否是 paramPoly3 类型
                paramPoly3 = geometry.find('paramPoly3')
                if paramPoly3 is not None:
                    # 处理 paramPoly3 类型的几何元素
                    print("This is a paramPoly3 type geometry.")
                    aU = float(paramPoly3.get('aU'))
                    bU = float(paramPoly3.get('bU'))
                    cU = float(paramPoly3.get('cU'))
                    dU = float(paramPoly3.get('dU'))
                    aV = float(paramPoly3.get('aV'))
                    bV = float(paramPoly3.get('bV'))
                    cV = float(paramPoly3.get('cV'))
                    dV = float(paramPoly3.get('dV'))

                    t_values = np.linspace(0, length, num=1000)
                    u_values = aU + bU * t_values + cU * t_values**2 + dU * t_values**3
                    v_values = aV + bV * t_values + cV * t_values**2 + dV * t_values**3

                    lane_line_x = x + u_values * np.cos(hdg) - v_values * np.sin(hdg)
                    lane_line_y = y + u_values * np.sin(hdg) + v_values * np.cos(hdg)
                    plt.plot(lane_line_x, lane_line_y, 'k--', label=f'ParamPoly3 Road ID {road_id}')
                    type = 'paramPoly3'
                    geometry_data.append((s_start, length, t_values, lane_line_x, lane_line_y, hdg,u_values,v_values,x,y,type))

                # 检测几何元素类型并进行相应处理
                elif geometry.find('line') is not None:
                    print("This is a straight line geometry.")
                    points = np.linspace(0, length, num=1000)
                    lane_line_x = x + points * np.cos(hdg)
                    lane_line_y = y + points * np.sin(hdg)
                    plt.plot(lane_line_x, lane_line_y, 'k--', label=f'Straight Line Road ID {road_id}')
                    type = 'line'
                    geometry_data.append((s_start, length, points, lane_line_x, lane_line_y, hdg,0,0,x,y,type))

                elif geometry.find('spiral') is not None:
                    print("This is a spiral geometry.")
                    spiral = geometry.find('spiral')
                    curvStart = float(spiral.get('curvStart'))
                    curvEnd = float(spiral.get('curvEnd'))
                    t_values = np.linspace(0, length, num=1000)
                    curvatures = np.linspace(curvStart, curvEnd, num=1000)
                    theta = hdg
                    dx = dy = 0
                    lane_line_x = [x]
                    lane_line_y = [y]
                    for i in range(1, len(t_values)):
                        ds = t_values[i] - t_values[i - 1]
                        curv = curvatures[i]
                        dtheta = ds * curv
                        theta += dtheta
                        dx += ds * np.cos(theta)
                        dy += ds * np.sin(theta)
                        lane_line_x.append(x + dx)
                        lane_line_y.append(y + dy)
                    plt.plot(lane_line_x, lane_line_y, 'k--', label=f'Spiral Road ID {road_id}')
                    type = 'spiral'
                    geometry_data.append((s_start, length, t_values, lane_line_x, lane_line_y, hdg,0,0,x,y,type))

                elif geometry.find('arc') is not None:
                    print("This is an arc geometry.")
                    arc = geometry.find('arc')
                    curvature = float(arc.get('curvature'))
                    points = np.linspace(0, length, num=1000)
                    '''
                    theta = np.linspace(hdg, hdg + curvature * length, num=1000)
                    lane_line_x = x + (np.sin(theta) - np.sin(hdg)) / curvature
                    lane_line_y = y - (np.cos(theta) - np.cos(hdg)) / curvature
                    '''
                    
                    radius = 1 / curvature if curvature != 0 else float('inf')  # 防止曲率为0导致除数为0
                    theta = hdg + curvature * points  # 这里计算每个点的航向角变化
                     # 计算每个点的坐标
                    lane_line_x = x + radius * (np.sin(theta) - np.sin(hdg)) 
                    lane_line_y = y - radius * (np.cos(theta) - np.cos(hdg)) 


                    plt.plot(lane_line_x, lane_line_y, 'k--', label=f'Arc Road ID {road_id}')
                    type = 'arc'
                    geometry_data.append((s_start, length, theta, lane_line_x, lane_line_y, hdg,0,0,x,y,type))

                # 更新道路坐标存储结构，用于后续的多边形补丁创建
                if int(road_id) not in previous_lane_coords:
                    previous_lane_coords[int(road_id)] = {}
                if 0 not in previous_lane_coords[int(road_id)]:
                    previous_lane_coords[int(road_id)][0] = {}
                previous_lane_coords[int(road_id)][0][geometry_index] = (lane_line_x, lane_line_y)
                geometry_index += 1



                    
            for laneSection in road.findall('.//laneSection'):
                if compte1 == 0:
                    ls_s = float(laneSection.get('s'))
                    lanes_data = []
                    driving_lanes = []
                    compte += 1
                    for lane in laneSection.findall('.//lane'):
                        lane_type = lane.get('type')
                        if lane_type == "driving" or lane_type == "restricted":
                            lane_id = int(lane.get('id'))
                            width_data = []
                            compte_width = 1
                            for widthElement in lane.findall('.//width'):
                                if compte_width != 1: #width只进行一次，为了简化，后续有需求可以再添加
                                    break
                                total_s = float(widthElement.get('sOffset')) + ls_s
                                a = float(widthElement.get('a'))
                                b = float(widthElement.get('b'))
                                c = float(widthElement.get('c'))
                                d = float(widthElement.get('d'))
                                compte_width += 1 

                                for (g_s_start, g_length, g_t_values, g_x, g_y, g_hdg,u_values,v_values,x,y,type) in geometry_data:
                                    ds = total_s - g_s_start
                                    #s =  - (ls_s +  sOffset )
                                    
                                    lane_widths = [calculate_width(point - ds, a, b, c, d) for point in g_t_values]
                                    width_data.append(lane_widths)

                                    lanes_data.append((lane_id, width_data,g_hdg,x,y,g_t_values,type))

                            if lane_type == "driving":
                                driving_lanes.append((lane_id, width_data))

                    # 对车道按照ID进行排序，负数ID递减，正数ID递增
                    driving_lanes.sort(key=lambda x: x[0])
                    positive_lanes = sorted((lane for lane in lanes_data if lane[0] > 0), key=lambda x: x[0])

                    negative_lanes = sorted((lane for lane in lanes_data if lane[0] < 0), key=lambda x: x[0], reverse=True)

                    min_lane_id, max_lane_id = driving_lanes[0][0], driving_lanes[-1][0]

                    # 处理排序后的车道数据
                    num_geometries = len(geometry_data)  # 例如有5个不同的geometry segments
                    num_points_per_geometry = 1000  # 每个segment有1000个计算点

                    # 初始化所有值为0
                    accumulated_widths = [[0 for _ in range(num_points_per_geometry)] for _ in range(num_geometries)]
                    accumulated_widths2 = [[0 for _ in range(num_points_per_geometry)] for _ in range(num_geometries)]
                    #accumulated_widths = np.zeros(len(points))
                    #accumulated_widths2 = np.zeros(len(points))
                    geometry_index = 0

                    for lanes_data in [positive_lanes, negative_lanes]:
                        last_lane_id = lanes_data[0][0]
                        index_geometry_id = -1 #为了accumulated_widths结构
                        for lane_id, all_widths,g_hdg,x,y,points,type in lanes_data:
                            if last_lane_id == lane_id:
                                index_geometry_id += 1
                            elif last_lane_id != lane_id: 
                                index_geometry_id = 0
                                last_lane_id = lane_id
                            lane_line_x = []
                            lane_line_y = []
                            current_lane_x  = []
                            current_lane_y  = []
                            next_lane_x = []
                            next_lane_y = []
                            curvature = float(arc.get('curvature')) 
                            for index, width_at_point in enumerate(all_widths[0]):  # Assuming one width segment per lane for simplicity
                                if type == 'line':
                                    center_x = x + points[index] * math.cos(g_hdg)
                                    center_y = y + points[index] * math.sin(g_hdg)

                                    if lane_id > 0:
                                        accumulated_widths[index_geometry_id][index] += width_at_point
                                        point_width_x = center_x - accumulated_widths[index_geometry_id][index] * math.sin(g_hdg)
                                        point_width_y = center_y + accumulated_widths[index_geometry_id][index] * math.cos(g_hdg)
                                    else:
                                        accumulated_widths2[index_geometry_id][index] -= width_at_point
                                        point_width_x = center_x - accumulated_widths2[index_geometry_id][index] * math.sin(g_hdg)
                                        point_width_y = center_y + accumulated_widths2[index_geometry_id][index] * math.cos(g_hdg)
                                elif type == 'arc':
                                    center_x = (x + (np.sin(points[index]) - np.sin(g_hdg)) / curvature).tolist()
                                    center_y = (y - (np.cos(points[index]) - np.cos(g_hdg)) / curvature).tolist()
                                    if lane_id > 0:
                                        accumulated_widths[index_geometry_id][index] += width_at_point
                                        point_width_x = center_x - accumulated_widths[index_geometry_id][index] * math.sin(points[index])
                                        point_width_y = center_y + accumulated_widths[index_geometry_id][index] * math.cos(points[index])
                                    else:
                                        accumulated_widths2[index_geometry_id][index] -= width_at_point
                                        point_width_x = center_x - accumulated_widths2[index_geometry_id][index] * math.sin(points[index])
                                        point_width_y = center_y + accumulated_widths2[index_geometry_id][index] * math.cos(points[index])


                                lane_line_x.append(point_width_x)
                                lane_line_y.append(point_width_y)

                                if lane_id == min_lane_id or lane_id == max_lane_id:
                                    if ((index==0 and compte ==1) or (index == len(all_widths[0])-1 and compte ==1)):
                                        x_endpoints.append(point_width_x)
                                        y_endpoints.append(point_width_y)
                                        road_endpoint_ids.append(road_id)

                            plt.plot(lane_line_x, lane_line_y, label=f"Lane ID {lane_id}")
                            if int(road_id) not in previous_lane_coords:
                                previous_lane_coords[int(road_id)] = {}
                            if lane_id not in previous_lane_coords[int(road_id)]:
                                previous_lane_coords[int(road_id)][lane_id] = {}
                            if geometry_index not in previous_lane_coords[int(road_id)][lane_id]:
                                previous_lane_coords[int(road_id)][lane_id][geometry_index] = (None, None)  # 或者其他合适的默认值

                            previous_lane_coords[int(road_id)][lane_id][geometry_index] = (lane_line_x, lane_line_y)
                            geometry_index += 1
                compte1 += 1


    # 创建多边形补丁
    for road_id, lanes in previous_lane_coords.items():
        lane_ids = sorted(lanes.keys())
        for i in range(len(lane_ids) - 1):
            lane_id = lane_ids[i]
            next_lane_id = lane_ids[i + 1]
            # 为了创建补丁，需要收集两个相邻车道的所有几何段坐标
            all_current_lane_coords = []
            all_next_lane_coords = []

            # 遍历当前车道的所有几何段
            for geometry_index in sorted(lanes[lane_id].keys()):
                coords = lanes[lane_id][geometry_index]
                all_current_lane_coords.extend(zip(coords[0], coords[1]))

            # 遍历下一个车道的所有几何段
            for geometry_index in sorted(lanes[next_lane_id].keys()):
                coords = lanes[next_lane_id][geometry_index]
                all_next_lane_coords.extend(zip(coords[0], coords[1]))

            # 创建多边形路径
            path_vertices = all_current_lane_coords + list(reversed(all_next_lane_coords))
            codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
            path = Path(path_vertices, codes)
            patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
            plt.gca().add_patch(patch)

            # 人为设置数字最小lane是1
            lane_id_call = i + 1
            road_lane_paths[int(road_id)][lane_id_call] = path


    plot_polygon_from_indices(road_lane_paths,x_endpoints, y_endpoints, [25, 59, 57, 52, 25], color='orange', label='Custom Polygon')

      
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
    return -404, 404  # 如果没有找到匹配的车道，返回 -1,1，这里代表在jonctions中

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

def determine_turn_type(path):
    """ Determines the turning type based on specific pairs of road IDs. """
    # Convert path elements to strings for consistent comparison
    path = [str(item) for item in path]

    # Check for a valid path length
    if len(path) < 2:
        return "N/A"

    # Extract the first and last road IDs in the path using the helper function
    first_road_id = int(path[0].split('.')[0])
    last_road_id = int(path[-1].split('.')[0])

    # Return None if the road IDs could not be determined
    if first_road_id is None or last_road_id is None:
        return "N/A"

    # New rules for turn determination based on specific pairs of road IDs
    if (first_road_id, last_road_id) in [(0, 5), (5, 0)]:
        return "straight"
    elif (first_road_id, last_road_id) in [(0, 6)]:
        return "left"
    elif (first_road_id, last_road_id) in [(5, 6), (6, 0)]:
        return "right"
    elif (first_road_id, last_road_id) in [(6, 5)]:
        return "left"

    return "N/A"

def process_tracks(df):
    #df = pd.read_csv(file_path)
    df.sort_values(by=['trackId', 'frame'], inplace=True)
    grouped = df.groupby('trackId')['road_lane'].apply(list).reset_index()
    grouped['unique_path'] = grouped['road_lane'].apply(lambda x: [k for i, k in enumerate(x) if i == 0 or k != x[i-1]])
    grouped['turn_type'] = grouped['unique_path'].apply(determine_turn_type)
    result = grouped[['trackId', 'unique_path', 'turn_type']]
    #result.to_csv('00_processed_tracks.csv', index=False)

    grouped['turn_type'] = grouped['unique_path'].apply(determine_turn_type)
    turn_type_dict = grouped.set_index('trackId')['turn_type'].to_dict()
    df['turn_type'] = df['trackId'].map(turn_type_dict)

    return df
