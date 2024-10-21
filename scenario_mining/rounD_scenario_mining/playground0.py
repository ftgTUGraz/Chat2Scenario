# Playground0.py
import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from pyproj import Transformer
import map_data.RounD_map_data.RounD_data as RounD_data
import pandas as pd

class Playground0:
    def __init__(self):
        self.lane_polygons = {}
        exit_lane8 = 0
        # 遍历 RounD_data 中的 polygons 并根据需要的 lane_id 进行关联
        for i, polygon in enumerate(RounD_data.lanes_polygons):
            # 根据 RounD_data 中的顺序设置 lane_id
            if i == 0:
                lane_id = 1  # 第一组多边形数据对应 lane_id = 1
            elif i == 1:
                lane_id = 12  # 第二组多边形数据对应 lane_id = 12
            else:
                lane_id = i  # 其余按照正常顺序关联

            # 将多边形对象添加到相应的 lane_id
            if lane_id not in self.lane_polygons:
                self.lane_polygons[lane_id] = []
            self.lane_polygons[lane_id].append(polygon)

    def parse_kml_coordinates(self, kml_file):
        tree = ET.parse(kml_file)
        root = tree.getroot()
        
        namespace = '{http://www.opengis.net/kml/2.2}'
        
        coordinates = []
        for placemark in root.findall(f'.//{namespace}Placemark'):
            for coords in placemark.findall(f'.//{namespace}coordinates'):
                coord_text = coords.text.strip()
                coord_list = coord_text.split()
                for coord in coord_list:
                    lon, lat, alt = map(float, coord.split(','))
                    coordinates.append((lon, lat))
        
        return coordinates

    def transform_coordinates(self, coords, x_utm_origin, y_utm_origin):
        transformer = Transformer.from_crs("epsg:4326", "epsg:32632")  # UTM zone 32N
        transformed_coords = []
        for lon, lat in coords:
            x, y = transformer.transform(lat, lon)
            local_x = x - x_utm_origin
            local_y = y - y_utm_origin
            transformed_coords.append((local_x, local_y))
        return transformed_coords

    def read_tracks(self, file_obj):
        tracks = []
        '''
        # Use io.StringIO to convert the contents of the file into a stream of strings
        file_content = io.StringIO(file_obj.read().decode('utf-8'))  # 假设文件编码为 UTF-8
        reader = csv.DictReader(file_content)

        for row in reader:
            track_id = int(row['trackId'])
            x_center = float(row['xCenter'])
            y_center = float(row['yCenter'])
            tracks.append((track_id, x_center, y_center, row))  
        '''      
        '''
        with open(file_obj, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                track_id = int(row['trackId'])
                x_center = float(row['xCenter'])
                y_center = float(row['yCenter'])
                tracks.append((track_id, x_center, y_center, row))
        return tracks
        '''
        df = pd.read_csv(file_obj)

        return df
        

    def get_lane_id(self, point):
        for lane_id, polygons in self.lane_polygons.items():
            for polygon in polygons:
                if polygon.contains(point):
                    return lane_id
        return None

    def simplify_lane_sequence(self, lane_sequence):
        simplified_sequence = []
        previous_lane = None
        for lane in lane_sequence:
            if lane != previous_lane:
                simplified_sequence.append(lane)
                previous_lane = lane
        return simplified_sequence

    def determine_activity_type(self,lane_sequence):
        if len(lane_sequence) < 2:
            return None
        
        lane_id_start = lane_sequence[0]
        lane_id_end = lane_sequence[-1]
        
        if lane_id_start == 2:
            if 8 in lane_sequence:
                return "turning right"
            elif lane_id_end == 10:
                return "go straight"
            elif lane_id_end == 11:
                return "turning left"
            elif 6 in lane_sequence:
                return "making U-turn"
        elif lane_id_start == 9:
            if lane_id_end == 10 and 3 in lane_sequence:
                return "turning right"
            elif lane_id_end == 11 and 3 in lane_sequence:
                return "go straight"
            elif lane_id_end == 6 and 3 in lane_sequence:
                return "turning left"
            elif lane_id_end == 9 and 3 in lane_sequence and 1 in lane_sequence and 8 in lane_sequence:
                return "making U-turn"
        elif lane_id_start == 4:
            if lane_id_end == 11:
                return "turning right"
            elif lane_id_end == 6 and 1 in lane_sequence:
                return "go straight"
            elif lane_id_end == 9 and 1 in lane_sequence and 8 in lane_sequence:
                return "turning left"
            elif lane_id_end == 10:
                return "making U-turn"
        elif lane_id_start == 5:
            if 6 in lane_sequence:
                return "turning right"
            elif lane_id_end == 9 and 1 in lane_sequence and 8 in lane_sequence:
                return "go straight"
            elif lane_id_end == 10:
                return "turning left"
            elif lane_id_end == 11:
                return "making U-turn"
        return None
    
    def determine_roundabout_activity(self, lane_id, track_lane_sequence, current_index):
        """
        Determine the activity type based on the current lane_id and track_lane_sequence.
        
        Parameters:
        lane_id (int): The ID of the lane in which the vehicle is currently located.
        track_lane_sequence (list): The sequence of lane IDs for the current trackId.
        current_index (int): The current index within the track_lane_sequence being processed.
        
        Returns:
        str: The activity type ('enter', 'inside', 'exit') based on lane_id and lane sequence.
        """

        if lane_id in [2, 3, 4, 5]:
            return "enter"
        elif lane_id in [1, 12]:
            return "inside"
        elif lane_id in [6, 8, 10, 11]:
            if lane_id == 8:
                self.exit_lane8 = 1
            return "exit"
        elif lane_id == 9:
            # Check if this is the first entry for this trackId
            if current_index == 0 or track_lane_sequence[0] == 9:
                return "enter"
            # Check the previous lane_id if it exists
            elif self.exit_lane8 == 1:
                return "exit"
        return None
    
    def plot_multiple_polygons(self):
        fig, ax = plt.subplots()
        colormap = plt.get_cmap('hsv')
        
        for i, (lane_id, polygons) in enumerate(self.lane_polygons.items()):
            color = colormap(i / len(self.lane_polygons))  # Use hsv colormap for diverse colors
            for polygon in polygons:
                x, y = polygon.exterior.xy
                ax.fill(x, y, alpha=0.5, fc=color, ec='black', label=f'Lane {lane_id}')
        
        ax.set_aspect('equal', 'box')
        plt.xlabel('Local X (m)')
        plt.ylabel('Local Y (m)')
        plt.title('Transformed Polygons')
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = dict(zip(labels, handles))
        ax.legend(unique_labels.values(), unique_labels.keys())
        plt.show()

    def write_lane_polygons_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write("from shapely.geometry import Polygon\n\n")
            for lane_id, polygons in self.lane_polygons.items():
                for i, polygon in enumerate(polygons):
                    coords = list(polygon.exterior.coords)
                    coords_str = ", ".join(f"({x:.6f}, {y:.6f})" for x, y in coords)
                    f.write(f"lane_{lane_id}_polygon_{i}_coords = [{coords_str}]\n")
                    f.write(f"lane_{lane_id}_polygon_{i} = Polygon(lane_{lane_id}_polygon_{i}_coords)\n\n")
            f.write("lanes_polygons = [\n")
            for lane_id, polygons in self.lane_polygons.items():
                for i in range(len(polygons)):
                    f.write(f"    lane_{lane_id}_polygon_{i},\n")
            f.write("]\n")

    def process(self, kml_files, x_utm_origin, y_utm_origin):
        for lane_id, files in kml_files.items():
            polygons = []
            for kml_file in files:
                coords = self.parse_kml_coordinates(kml_file)
                transformed_coords = self.transform_coordinates(coords, x_utm_origin, y_utm_origin)
                polygon = Polygon(transformed_coords)
                polygons.append(polygon)
            self.lane_polygons[lane_id] = polygons

    def update_track_file(self, tracks_file):
        # 重置文件指针到文件开头
        #tracks_file.seek(0)
        
        # 打印文件内容进行调试（可选）
        #content = tracks_file.read()
        #print(content)
        #tracks_file.seek(0)

        # 使用 pandas 读取 CSV 文件
        df = pd.read_csv(tracks_file)

        # 初始化新列 'laneId' 和 'activity_type'
        df['laneId'] = None
        df['activity_type'] = None

        # 构建包含 DataFrame 索引的 track_lane_sequences
        track_lane_sequences = {}
        for index, row in df.iterrows():
            x_center = float(row['xCenter'])
            y_center = float(row['yCenter'])
            point = Point(x_center, y_center)

            # 确定 lane_id
            lane_id = self.get_lane_id(point)

            # 将 (index, lane_id) 存储到 track_lane_sequences
            track_id = row['trackId']
            if track_id not in track_lane_sequences:
                track_lane_sequences[track_id] = []
            track_lane_sequences[track_id].append((index, lane_id))

            # 更新 DataFrame 的 'laneId' 列
            df.at[index, 'laneId'] = lane_id

        # 为每个 track_id 确定 activity_type
        for track_id, index_lane_list in track_lane_sequences.items():
            lane_sequence = [lane_id for idx, lane_id in index_lane_list]
            simplified_sequence = self.simplify_lane_sequence(lane_sequence)
            for i, (idx, lane_id) in enumerate(index_lane_list):
                if lane_id is not None:
                    activity_type = self.determine_roundabout_activity(lane_id, lane_sequence, i)
                    df.at[idx, 'activity_type'] = activity_type

        return df


        '''
        # Read the track data
        tracks = self.read_tracks(tracks_file)
        track_lane_sequences = {}

        # Determine the lane for each track point
        for track_id, x_center, y_center, row in tracks:
            point = Point(x_center, y_center)
            lane_id = self.get_lane_id(point)
            if track_id not in track_lane_sequences:
                track_lane_sequences[track_id] = []
            track_lane_sequences[track_id].append(lane_id)

        updated_tracks = []
        
        tracks_file.seek(0)
        file_content = io.StringIO(tracks_file.read().decode('utf-8'))
        # Read the original track data
        #with open(tracks_file, 'r') as csvfile:
            #reader = csv.DictReader(csvfile)
        reader = csv.DictReader(file_content)
        fieldnames = reader.fieldnames + ['laneId', 'activity_type']
        
        index = 0
        last_track_id = 0
        
        for row in reader:
            track_id = int(row['trackId'])
            
            # Reset the index when track_id changes
            if last_track_id != track_id:
                index = 0
                last_track_id = track_id
            
            # Add laneId and activity_type columns based on track_lane_sequences
            if track_id in track_lane_sequences:
                lane_sequence = self.simplify_lane_sequence(track_lane_sequences[track_id])
                
                if index < len(track_lane_sequences[track_id]):
                    row['laneId'] = track_lane_sequences[track_id][index]
                    index += 1
                
                lane_sequence = [lane for lane in lane_sequence if lane is not None]
                row['activity_type'] = self.determine_roundabout_activity(row['laneId'], track_lane_sequences[track_id], index)

            else:
                row['laneId'] = None
                row['activity_type'] = None
            
            updated_tracks.append(row)

        # Convert updated_tracks to a pandas DataFrame
        updated_tracks_df = pd.DataFrame(updated_tracks, columns=fieldnames)
        
        # Return the DataFrame
        return updated_tracks_df
        '''