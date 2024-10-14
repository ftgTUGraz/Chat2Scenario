# Playground1.py
import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from pyproj import Transformer
import importlib
import map_data.RounD_map_data.RounD_data as RounD_data
import pandas as pd

class Playground1:
    def __init__(self):
        self.lane_polygons = {}
        # 遍历 RounD_data 中的 polygons 并根据需要的 lane_id 进行关联
        for i, polygon in enumerate(RounD_data.lanes_polygons1):
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

    def read_tracks(self, file_path):
        tracks = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                track_id = int(row['trackId'])
                x_center = float(row['xCenter'])
                y_center = float(row['yCenter'])
                tracks.append((track_id, x_center, y_center, row))
        return tracks

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

    def determine_activity_type(self, lane_sequence):
        if len(lane_sequence) < 2:
            return None
        
        lane_id_start = lane_sequence[0]
        lane_id_end = lane_sequence[-1]
        
        if lane_id_start in [2, 3]:
            if lane_id_end == 5 and 9 in lane_sequence:
                return "turning right"
            elif lane_id_end == 10:
                return "go straight"
            elif 12 in lane_sequence:
                return "turning left"
            elif lane_id_end == 8:
                return "making U-turn"
        elif lane_id_start == 5:
            if lane_id_end == 10:
                return "turning right"
            elif 12 in lane_sequence:
                return "go straight"
            elif lane_id_end == 8:
                return "turning left"
            elif lane_id_end == 5 and 4 in lane_sequence and 1 in lane_sequence and 9 in lane_sequence:
                return "making U-turn"
        elif lane_id_start == 6:
            if 12 in lane_sequence:
                return "turning right"
            elif lane_id_end == 8:
                return "go straight"
            elif lane_id_end == 5 and 9 in lane_sequence:
                return "turning left"
            elif lane_id_end == 10:
                return "making U-turn"
        elif lane_id_start == 7:
            if lane_id_end == 8:
                return "turning right"
            elif lane_id_end == 5 and 9 in lane_sequence:
                return "go straight"
            elif lane_id_end == 10:
                return "turning left"
            elif 12 in lane_sequence:
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

        if lane_id in [2, 3, 4, 6, 7]:
            return "enter"
        elif lane_id in [1, 12]:
            return "inside"
        elif lane_id in [8, 9, 10, 11]:
            if lane_id == 8:
                self.exit_lane8 = 1
            return "exit"
        elif lane_id == 5:
            # Check if this is the first entry for this trackId
            if current_index == 0 or track_lane_sequence[0] == 5:
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

    def write_lane_polygons_to_file(self, filename, lane_set_name):
        with open(filename, 'a') as f:  # Use 'a' mode to append to the file
            for lane_id, polygons in self.lane_polygons.items():
                for i, polygon in enumerate(polygons):
                    coords = list(polygon.exterior.coords)
                    coords_str = ", ".join(f"({x:.6f}, {y:.6f})" for x, y in coords)
                    f.write(f"{lane_set_name}_lane_{lane_id}_polygon_{i}_coords = [{coords_str}]\n")
                    f.write(f"{lane_set_name}_lane_{lane_id}_polygon_{i} = Polygon({lane_set_name}_lane_{lane_id}_polygon_{i}_coords)\n\n")

            f.write(f"{lane_set_name} = [\n")
            for lane_id, polygons in self.lane_polygons.items():
                for i in range(len(polygons)):
                    f.write(f"    {lane_set_name}_lane_{lane_id}_polygon_{i},\n")
            f.write("]\n\n")

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
        
        # Read the original track data
        with open(tracks_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
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
    def reload_RounD_data(self):
        importlib.reload(RounD_data)
