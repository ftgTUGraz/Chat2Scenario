import xml.etree.ElementTree as ET
import math
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd
import pickle
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from io import BytesIO
from PIL import Image

class FrankenbergProcessor:
    def __init__(self):
        self.road_lane_paths = {}

    @staticmethod
    def save_road_lane_paths_pickle(road_lane_paths, file_path):
        """
        Save road lane paths data to a pickle file.

        Parameters:
        ----------
        road_lane_paths (dict): A dictionary containing the road lane paths data.
        file_path (str): The path to the file where the data will be saved.

        Returns:
        ----------
        None: This function does not return any value.
        """
        with open(file_path, 'wb') as file:
            pickle.dump(road_lane_paths, file)

    @staticmethod
    def load_road_lane_paths_pickle(file_path):
        """
        Load road lane paths data from a pickle file.

        Parameters:
        ----------
        file_path (str): The path to the file from which the data will be loaded.

        Returns:
        ----------
        dict: The loaded road lane paths data, or None if an error occurs.
        """
        try:
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
            return data
        except FileNotFoundError:
            print("File not found. Please check the path.")
            return None
        except Exception as e:
            print("An error occurred:", e)
            return None

    @staticmethod
    def calculate_width(ds, a, b, c, d):
        """
        Calculate the width of a lane at a specific distance along the road using a cubic polynomial.

        Parameters:
        ----------
        ds (float): Distance along the road from the starting point.
        a (float): Constant term of the polynomial.
        b (float): Coefficient of the linear term.
        c (float): Coefficient of the squared term.
        d (float): Coefficient of the cubic term.

        Returns:
        ----------
        float: Calculated width at distance ds.
        """
        return a + b * ds + c * (ds**2) + d * (ds**3)

    @staticmethod
    def find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_ids):
        """
        Find the two nearest endpoints for each road from the provided endpoint coordinates and road identifiers.

        Parameters:
        ----------
        x_endpoints (list of float): X-coordinates of endpoints.
        y_endpoints (list of float): Y-coordinates of endpoints.
        road_ids (list of int): Identifiers for each road corresponding to endpoints.

        Returns:
        ----------
        tuple: Contains two dictionaries, one with the nearest endpoints per road and another with junction polygons.
        """
        num_roads = len(set(road_ids))  # Number of unique roads
        unique_road_ids = set(road_ids)  # Remove duplicates, unordered
        sorted_road_ids = sorted(unique_road_ids)  # Sort the set of road IDs
        nearest_endpoints_per_road = {str(road_id): [] for road_id in sorted_road_ids}
        compte = 0

        for i in range(len(x_endpoints)):
            current_road_id = str(road_ids[i])  # Use string type for keys
            nearest_distances = sorted(
                [(j, math.sqrt((x_endpoints[i] - x_endpoints[j])**2 + (y_endpoints[i] - y_endpoints[j])**2))
                 for j in range(len(x_endpoints)) if str(road_ids[j]) != current_road_id],
                key=lambda x: x[1]
            )
            # Record the nearest two endpoints for each road, including distance
            if i == 0:
                nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[2][0], nearest_distances[2][1]))
            if nearest_distances and compte % 2 == 0 and i != 0:
                nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[0][0], nearest_distances[0][1]))
            if compte % 2 != 0:
                for n in range(len(nearest_distances)):
                    if road_ids[nearest_endpoints_per_road[current_road_id][compte-1][1]] != road_ids[nearest_distances[n][0]]:
                        nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[n][0], nearest_distances[n][1]))
                        compte = -1
                        break
            compte += 1

        # Make sure that the two endpoints selected are not the same starting endpoint
        two_nearest_endpoints_per_road = {}
        polygan_jonctions = []
        cpt = 1
        for road_id, endpoints_info in nearest_endpoints_per_road.items():
            unique_indices = set()
            selected_endpoints = []
            for info in sorted(endpoints_info, key=lambda x: x[2]):  # Sort by distance
                if info[0] not in unique_indices:
                    selected_endpoints.append(info)
                    unique_indices.add(info[0])
                if len(selected_endpoints) == 2:
                    break
            two_nearest_endpoints_per_road[road_id] = selected_endpoints
            first_elements = [endpoint[0] for endpoint in selected_endpoints]
            sorted_elements = sorted(first_elements)
            if cpt == 1:
                polygan_jonctions.append((x_endpoints[sorted_elements[0]], y_endpoints[sorted_elements[0]]))
                cpt += 1
            polygan_jonctions.append((x_endpoints[sorted_elements[1]], y_endpoints[sorted_elements[1]]))
            for first, seconds, third in selected_endpoints:
                if first == sorted_elements[1]:
                    polygan_jonctions.append((x_endpoints[seconds], y_endpoints[seconds]))

        return two_nearest_endpoints_per_road, polygan_jonctions

    @staticmethod
    def connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids):
        """
        Connect the nearest endpoints for each road, ensuring that no endpoint is connected more than once.

        Parameters:
        ----------
        two_nearest_endpoints_per_road (dict): Dictionary containing two nearest endpoints for each road.
        road_endpoint_ids (list): List of road identifiers corresponding to endpoints.

        Returns:
        ----------
        list: List of tuples representing the connections between endpoints.
        """
        connections = []
        connected_indices = set()  # To store already connected endpoints

        # Iterate through each road's two nearest endpoints
        for road_id, endpoints_info in two_nearest_endpoints_per_road.items():
            for endpoint_info in endpoints_info:
                start_index, end_index, _ = endpoint_info
                if start_index not in connected_indices and end_index not in connected_indices:
                    connections.append((start_index, end_index))
                    connected_indices.update([start_index, end_index])

        return connections

    def process_opendrive_file(self, filepath):
        """
        Process an OpenDRIVE file to extract road and lane geometry, and visualize it.

        Parameters:
        ----------
        filepath (str): The file path of the OpenDRIVE file.

        Returns:
        ----------
        dict: A dictionary containing paths for each road and lane.
        """
        tree = ET.parse(filepath)
        root = tree.getroot()
        previous_lane_coords = {}
        plt.figure(figsize=(10, 5))
        self.road_lane_paths = {}
        x_endpoints = []
        y_endpoints = []
        road_endpoint_ids = []

        road_ids_of_interest = {'0', '2', '5', '6'}

        for road in root.findall('road'):
            road_id = road.get('id')
            if road_id in road_ids_of_interest:
                print(f"Processing road ID: {road_id}")
                previous_lane_coords[int(road_id)] = {}
                self.road_lane_paths[int(road_id)] = {}
                for geometry in road.findall('.//geometry'):
                    param_poly3 = geometry.find('.//paramPoly3')

                    if param_poly3 is not None:
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
                                    if lane_type == "driving" or lane_type == "parking":
                                        width_data = []

                                        for widthElement in lane.findall('.//width'):
                                            sOffset = float(widthElement.get('sOffset'))
                                            a = float(widthElement.get('a'))
                                            b = float(widthElement.get('b'))
                                            c = float(widthElement.get('c'))
                                            d = float(widthElement.get('d'))
                                            s = -(ls_s + sOffset)

                                            lane_widths = [self.calculate_width(point + s, a, b, c, d) for point in points]
                                            width_data.append(lane_widths)

                                        lanes_data.append((lane_id, width_data))

                                        if lane_type == "driving":
                                            driving_lanes.append((lane_id, width_data))

                                driving_lanes.sort(key=lambda x: x[0])
                                positive_lanes = sorted((lane for lane in lanes_data if lane[0] > 0), key=lambda x: x[0])
                                negative_lanes = sorted((lane for lane in lanes_data if lane[0] < 0), key=lambda x: x[0], reverse=True)

                                min_lane_id, max_lane_id = driving_lanes[0][0], driving_lanes[-1][0]

                                accumulated_widths = np.zeros(len(points))
                                accumulated_widths2 = np.zeros(len(points))
                                for lanes_data in [positive_lanes, negative_lanes]:
                                    for lane_id, all_widths in lanes_data:
                                        lane_line_x = []
                                        lane_line_y = []
                                        for index, width_at_point in enumerate(all_widths[0]):
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
                                                if ((index == 0 and compte == 1) or (index == len(all_widths[0]) - 1 and compte == 1)):
                                                    x_endpoints.append(point_width_x)
                                                    y_endpoints.append(point_width_y)
                                                    road_endpoint_ids.append(road_id)

                                        plt.plot(lane_line_x, lane_line_y, label=f"Lane ID {lane_id}")
                                        previous_lane_coords[int(road_id)][lane_id] = (lane_line_x, lane_line_y)
                            compte1 += 1

        for road_id, lanes in previous_lane_coords.items():
            lane_ids = sorted(lanes.keys())
            for i in range(len(lane_ids) - 1):
                lane_id = lane_ids[i]
                lane_id_call = i + 1
                next_lane_id = lane_ids[i + 1]
                current_lane_x, current_lane_y = lanes[lane_id]
                next_lane_x, next_lane_y = lanes[next_lane_id]

                path_vertices = list(zip(current_lane_x, current_lane_y)) + list(zip(reversed(next_lane_x), reversed(next_lane_y)))
                codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
                path = Path(path_vertices, codes)
                patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
                plt.gca().add_patch(patch)

                self.road_lane_paths[int(road_id)][lane_id_call] = path

        x_endpoints = x_endpoints[::2]
        y_endpoints = y_endpoints[::2]
        road_endpoint_ids = road_endpoint_ids[::2]

        two_nearest_endpoints_per_road, polygan_jonctions = self.find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_endpoint_ids)

        connections = self.connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids)

        for connection in connections:
            plt.plot([x_endpoints[connection[0]], x_endpoints[connection[1]]],
                     [y_endpoints[connection[0]], y_endpoints[connection[1]]], 'r-')

        for road_id, nearest_endpoints in two_nearest_endpoints_per_road.items():
            for endpoint_info in nearest_endpoints:
                endpoint_index = endpoint_info[0]
                plt.scatter(x_endpoints[endpoint_index], y_endpoints[endpoint_index], c='blue')

        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title("Visualization of Roads and Lanes")
        plt.legend()
        plt.grid(True)
        plt.axis('equal')
        plt.show()

        return self.road_lane_paths

    def find_lane_by_coordinates(self, x, y):
        """
        Identify the road and lane ID that a given point (x, y) belongs to within provided road lane paths.

        Parameters:
        ----------
        road_lane_paths (dict): A dictionary mapping road IDs to their corresponding lane paths.
        x (float): X-coordinate of the point to check.
        y (float): Y-coordinate of the point to check.

        Returns:
        ----------
        tuple: Tuple of road ID and lane ID if found, otherwise returns (100, 1) to indicate no match found in the lanes (used for junctions).
        """
        for road_id, lanes in self.road_lane_paths.items():
            for lane_id, path in lanes.items():
                if path.contains_point((x, y)):
                    return road_id, lane_id
        return 100, 1  # Default return for no match, indicating location in junctions.

    def update_tracks_with_lane_info(self, csv_path):
        """
        Update a CSV file with road lane information by adding a 'road_lane' column indicating the road and lane each track point falls into.

        Parameters:
        ----------
        csv_path (str): The path to the CSV file containing tracking data.

        Returns:
        ----------
        DataFrame: The updated DataFrame with an additional 'road_lane' column.
        """
        tracks_meta_df = pd.read_csv(csv_path)

        file_path = 'frankenburg_02.pkl'
        self.road_lane_paths = self.load_road_lane_paths_pickle(file_path)

        fig, ax = plt.subplots()
        self.plot_road_lane_paths(ax, self.road_lane_paths)

        tracks_meta_df['road_lane'] = ''

        for index, row in tracks_meta_df.iterrows():
            x, y = row['xCenter'], row['yCenter']
            road_id, lane_id = self.find_lane_by_coordinates(x, y)
            tracks_meta_df.at[index, 'road_lane'] = f'{road_id}.{lane_id}'

        return tracks_meta_df
    
    @staticmethod
    def plot_road_lane_paths(ax, road_lane_paths):
        colormap = cm.get_cmap('tab20')
        road_lane_ids = [(road_id, lane_id) for road_id, lanes in road_lane_paths.items() for lane_id in lanes.keys()]
        unique_road_lane_ids = sorted(set(road_lane_ids))
        color_norm = mcolors.Normalize(vmin=0, vmax=len(unique_road_lane_ids) - 1)

        scalar_map = cm.ScalarMappable(norm=color_norm, cmap=colormap)
        
        for road_id, lanes in road_lane_paths.items():
            for lane_id, path in lanes.items():
                color = scalar_map.to_rgba(unique_road_lane_ids.index((road_id, lane_id)))
                if isinstance(path, Path):
                    patch = PathPatch(path, facecolor=color, edgecolor='none', alpha=0.5, label=f"Road ID {road_id}, Lane ID {lane_id}")
                    ax.add_patch(patch)
                else:
                    lane_line_x, lane_line_y = path
                    ax.plot(lane_line_x, lane_line_y, color=color, label=f"Road ID {road_id}, Lane ID {lane_id}")

        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.set_title("Visualization of Roads and Lanes")
        ax.legend()
        ax.grid(True)
        ax.axis('equal')

    @staticmethod
    def extract_road_id(road_lane):
        """
        Extracts the road ID from a combined 'road.lane' string format.

        Parameters:
        ----------
        road_lane (str): String containing the road and lane IDs.

        Returns:
        ----------
        int: The extracted road ID.
        """
        return int(road_lane.split('.')[0]) if '.' in road_lane else None

    @staticmethod
    def determine_turn_type(path):
        """
        Determines the type of turn (straight, left, right) based on a sequence of road IDs.

        Parameters:
        ----------
        path (list of str): List of 'road.lane' strings representing the path a vehicle has taken.

        Returns:
        ----------
        str: The determined turn type ('straight', 'left', 'right', or 'N/A' for non-determined).
        """
        path = [str(item) for item in path]

        first_road_id = int(path[0].split('.')[0])
        last_road_id = int(path[-1].split('.')[0])
        diff = first_road_id - last_road_id

        if diff in {3, -3, 6, -6}:
            return "straight"
        elif diff in {-1, -5, 2, 4}:
            return "left"
        elif diff in {1, 5, -2, -4}:
            return "right"
        return "N/A"

    def process_tracks(self, df):
        """
        Processes a DataFrame of tracking data to determine turn types based on the paths taken by tracked objects.

        Parameters:
        ----------
        df (DataFrame): DataFrame containing tracking data.

        Returns:
        ----------
        DataFrame: The DataFrame with an added 'turn_type' column indicating the type of turn made.
        """
        df.sort_values(by=['trackId', 'frame'], inplace=True)
        grouped = df.groupby('trackId')['road_lane'].apply(list).reset_index()
        grouped['unique_path'] = grouped['road_lane'].apply(lambda x: [k for i, k in enumerate(x) if i == 0 or k != x[i-1]])
        grouped['turn_type'] = grouped['unique_path'].apply(self.determine_turn_type)
        result = grouped[['trackId', 'unique_path', 'turn_type']]
        turn_type_dict = grouped.set_index('trackId')['turn_type'].to_dict()
        df['turn_type'] = df['trackId'].map(turn_type_dict)

        return df
