from pyproj import Proj, transform
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import xml.etree.ElementTree as ET
from pyproj import Proj, Transformer
import csv
from collections import defaultdict

# 定义投影转换（示例从WGS84到UTM第32N区）
in_proj = 'epsg:4326'  # WGS84
out_proj = 'epsg:32632'  # UTM第32N区

# 使用 Transformer 类进行转换
transformer = Transformer.from_crs(in_proj, out_proj)

def extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin):
    """
    从KML文件中提取指定点的坐标并转换为本地坐标。
    
    参数:
    kml_file (str): KML文件路径
    placemark_names (list): 指定的地标名称列表
    x_utm_origin (float): UTM坐标系的X原点偏移量
    y_utm_origin (float): UTM坐标系的Y原点偏移量
    
    返回:
    list: 提取的本地坐标列表
    """
    tree = ET.parse(kml_file)
    root = tree.getroot()

    namespace = '{http://www.opengis.net/kml/2.2}'
    coords = []

    for placemark_name in placemark_names:
        for placemark in root.findall(f'.//{namespace}Placemark'):
            name = placemark.find(f'{namespace}name').text
            if name == placemark_name:
                coordinates_text = placemark.find(f'.//{namespace}coordinates').text.strip()
                coordinate_list = coordinates_text.split()
                for coordinate in coordinate_list:
                    lon, lat, _ = map(float, coordinate.split(','))
                    x, y = transformer.transform(lat,lon)
                    # 减去UTM原点偏移量
                    local_x = x - x_utm_origin
                    local_y = y - y_utm_origin
                    coords.append((local_x, local_y))
                print(f"Extracted coordinates for {name}: {coords}")
                break
    
    return coords

def create_polygon_and_plot(kml_files_and_names, labels, colors, x_utm_origin, y_utm_origin):
    """
    创建多边形并绘制从多个KML文件中提取的指定点。

    参数:
    kml_files_and_names (list): 包含多个 (KML文件路径, 地标名称列表) 的元组列表
    labels (list): 对应的图例标签列表
    colors (list): 对应的颜色列表
    x_utm_origin (float): UTM坐标系的X原点偏移量
    y_utm_origin (float): UTM坐标系的Y原点偏移量
    """
    fig, ax = plt.subplots()

    for (kml_file, placemark_names), label, color in zip(kml_files_and_names, labels, colors):
        # 提取坐标
        coords = extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin)

        # 检查是否提取到坐标
        if not coords:
            print(f"Error: No coordinates extracted for {label}")
            continue

        # 创建多边形
        polygon = Polygon(coords)

        # 绘制多边形
        path_vertices = coords + [coords[0]]  # 闭合多边形
        codes = [Path.MOVETO] + [Path.LINETO] * (len(coords) - 1) + [Path.CLOSEPOLY]
        path = Path(path_vertices, codes)
        patch = PathPatch(path, facecolor=color, edgecolor='black', alpha=0.5, label=label)
        ax.add_patch(patch)

    # 设置图像属性并显示
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.set_title("Visualization of Lanes and Polygons")
    ax.legend()
    ax.grid(True)
    ax.axis('equal')
    plt.show()

def extract_polygon_from_kml(kml_file, placemark_names, x_utm_origin, y_utm_origin):
    """
    从KML文件中提取指定点的多边形。
    
    参数:
    kml_file (str): KML文件路径
    placemark_names (list): 指定的地标名称列表
    x_utm_origin (float): UTM坐标系的X原点偏移量
    y_utm_origin (float): UTM坐标系的Y原点偏移量
    
    返回:
    Polygon: 提取的多边形
    """
    coords = extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin)
    return Polygon(coords) if coords else None

def determine_turn_type_and_lane(point, onramp_polygon, offramp_polygon, lanes_polygons):
    """
    确定轨迹点的转弯类型和车道ID。
    
    参数:
    point (Point): 轨迹点
    onramp_polygon (Polygon): OnRamp多边形
    offramp_polygon (Polygon): OffRamp多边形
    lanes_polygons (list): (lane_id, Polygon)元组列表
    
    返回:
    tuple: (转弯类型, 车道ID)
    """
    if onramp_polygon and onramp_polygon.contains(point):
        return 'OnRamp', -5  # Assuming OnRamp corresponds to lane -5
    if offramp_polygon and offramp_polygon.contains(point):
        return 'OffRamp', 4  # Assuming OffRamp corresponds to lane -5
    
    for lane_id, polygon in lanes_polygons:
        if polygon and polygon.contains(point):
            return 'KeepRamp', lane_id
    
    return 'Unknown', None

def update_track_data(input_file, output_file, onramp_polygon, offramp_polygon, lanes_polygons):
    """
    更新轨迹数据中的转弯类型和车道ID。
    
    参数:
    input_file (str): 输入轨迹数据文件路径
    output_file (str): 输出更新的轨迹数据文件路径
    onramp_polygon (Polygon): OnRamp多边形
    offramp_polygon (Polygon): OffRamp多边形
    lanes_polygons (list): (lane_id, Polygon)元组列表
    """
    tracks = defaultdict(list)

    # 首先读取输入文件并确定每个trackId的转弯类型
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['laneId', 'activity_type']
        for row in reader:
            x_center = float(row['xCenter'])
            y_center = float(row['yCenter'])
            point = Point(x_center, y_center)
            turn_type, lane_id = determine_turn_type_and_lane(point, onramp_polygon, offramp_polygon, lanes_polygons)
            row['laneId'] = lane_id
            row['activity_type'] = turn_type
            tracks[row['trackId']].append(row)

    #更新每个trackId的所有点的活动类型
    for track_id, rows in tracks.items():
        # 检查是否有任何点是OnRamp或OffRamp
        activities = set(row['activity_type'] for row in rows)
        if 'OnRamp' in activities and 'OffRamp' in activities:
            final_activity = 'OnRamp|OffRamp'
        elif 'OnRamp' in activities:
            final_activity = 'OnRamp'
        elif 'OffRamp' in activities:
            final_activity = 'OffRamp'
        else:
            final_activity = 'KeepRamp'
        
        # 更新所有点的活动类型
        for row in rows:
            row['activity_type'] = final_activity

    # 将更新后的数据写入输出文件
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for rows in tracks.values():
            writer.writerows(rows)

    print(f"Updated tracks have been saved to {output_file}")