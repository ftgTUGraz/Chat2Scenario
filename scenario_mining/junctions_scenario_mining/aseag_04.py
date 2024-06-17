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

class AseagProcessor:
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
    def calculate_width(ds, a, b, c, d):
        """
        Calculate the width based on polynomial coefficients and distance along the road.

        Parameters:
        ----------
        ds (float): Distance along the road.
        a (float): Constant term of the polynomial.
        b (float): Coefficient of the linear term.
        c (float): Coefficient of the squared term.
        d (float): Coefficient of the cubic term.

        Returns:
        ----------
        float: Calculated width at distance ds.
        """
        return a + b * ds + c * (ds ** 2) + d * (ds ** 3)

    @staticmethod
    def find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_ids):
        """
        Finds the two nearest endpoints for each road based on x and y coordinates.

        Parameters:
        ----------
        x_endpoints (list of float): List of x coordinates for endpoints.
        y_endpoints (list of float): List of y coordinates for endpoints.
        road_ids (list of int): List of road identifiers corresponding to each endpoint.

        Returns:
        ----------
        dict: A dictionary mapping each road ID to its two nearest endpoints.
        tuple: A list of coordinates for the polygon junctions.
        """
        num_roads = len(set(road_ids))
        unique_road_ids = set(road_ids)
        sorted_road_ids = sorted(unique_road_ids)
        nearest_endpoints_per_road = {str(road_id): [] for road_id in sorted_road_ids}

        for i in range(len(x_endpoints)):
            current_road_id = str(road_ids[i])
            nearest_distances = sorted(
                [(j, math.sqrt((x_endpoints[i] - x_endpoints[j]) ** 2 + (y_endpoints[i] - y_endpoints[j]) ** 2))
                 for j in range(len(x_endpoints)) if str(road_ids[j]) != current_road_id],
                key=lambda x: x[1]
            )
            if current_road_id == '5' and i == 53:
                nearest_distances[0] = (23, math.sqrt((x_endpoints[i] - x_endpoints[23]) ** 2 + (y_endpoints[i] - y_endpoints[23]) ** 2))

            if nearest_distances and i != 24 and i != 23 and i != 56:
                nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[0][0], nearest_distances[0][1]))

        two_nearest_endpoints_per_road = {}
        polygan_jonctions = []
        cpt = 1
        for road_id, endpoints_info in nearest_endpoints_per_road.items():
            unique_indices = set()
            selected_endpoints = []
            for info in sorted(endpoints_info, key=lambda x: x[2]):
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
        Create connections between the nearest endpoints of different roads.

        Parameters:
        ----------
        two_nearest_endpoints_per_road (dict): Dictionary containing the nearest endpoints for each road.
        road_endpoint_ids (list): List of road endpoint identifiers.

        Returns:
        ----------
        list: A list of tuples, each representing a connection between two endpoints.
        """
        connections = []
        connected_indices = set()

        for road_id, endpoints_info in two_nearest_endpoints_per_road.items():
            for endpoint_info in endpoints_info:
                start_index, end_index, _ = endpoint_info
                if start_index not in connected_indices and end_index not in connected_indices:
                    connections.append((start_index, end_index))
                    connected_indices.update([start_index, end_index])

        return connections

    @staticmethod
    def plot_polygon_from_indices(road_lane_paths, x_endpoints, y_endpoints, indices, color='orange', label='Polygon'):
        """
        Plot a polygon based on provided endpoint indices.

        Parameters:
        ----------
        road_lane_paths (dict): Dictionary storing paths for different road lanes.
        x_endpoints (list of float): List of x coordinates for endpoints.
        y_endpoints (list of float): List of y coordinates for endpoints.
        indices (list of int): List of indices that define the polygon vertices.
        color (str): Color of the polygon face.
        label (str): Label for the polygon in the plot.

        Returns:
        ----------
        None: This function does not return any value.
        """
        x_coords = [x_endpoints[i] for i in indices]
        y_coords = [y_endpoints[i] for i in indices]
        path_vertices = list(zip(x_coords, y_coords))
        codes = [Path.MOVETO] + [Path.LINETO] * (len(indices) - 2) + [Path.CLOSEPOLY]
        path = Path(path_vertices, codes)
        patch = PathPatch(path, facecolor=color, edgecolor='black', alpha=0.5, label=label)
        plt.gca().add_patch(patch)
        road_lane_paths[6][100] = path

    @staticmethod
    def plot_custom_polygon(road_lane_paths, x_endpoints, y_endpoints, indices, color='orange', label='Custom Polygon'):
        """
        Plot a custom polygon using specified indices, adding midpoints for visual complexity.

        Parameters:
        ----------
        road_lane_paths (dict): Dictionary storing paths for different road lanes.
        x_endpoints (list of float): List of x coordinates for endpoints.
        y_endpoints (list of float): List of y coordinates for endpoints.
        indices (list of int): List of indices that define the polygon vertices.
        color (str): Color of the polygon face.
        label (str): Label for the polygon in the plot.

        Returns:
        ----------
        None: This function does not return any value.
        """
        midpoint_52_25 = ((x_endpoints[52] + x_endpoints[25]) / 2, (y_endpoints[52] + y_endpoints[25]) / 2)
        midpoint_54_51 = ((x_endpoints[54] + x_endpoints[51]) / 2, (y_endpoints[54] + y_endpoints[51]) / 2)

        coords = [
            (x_endpoints[52], y_endpoints[52]),
            midpoint_52_25,
            midpoint_54_51,
            (x_endpoints[54], y_endpoints[54]),
            (x_endpoints[52], y_endpoints[52])
        ]

        path_vertices = coords
        codes = [Path.MOVETO] + [Path.LINETO] * (len(coords) - 2) + [Path.CLOSEPOLY]
        path = Path(path_vertices, codes)
        patch = PathPatch(path, facecolor=color, edgecolor='black', alpha=0.5, label=label)
        plt.gca().add_patch(patch)

        road_lane_paths[5][100] = path

    @staticmethod
    def plot_custom_polygon2(road_lane_paths, x_endpoints, y_endpoints, indices, color='orange', label='Custom Polygon'):
        """
        Plot a custom polygon using specified indices, including midpoints for enhanced definition.

        Parameters:
        ----------
        road_lane_paths (dict): Dictionary storing paths for different road lanes.
        x_endpoints (list of float): List of x coordinates for endpoints.
        y_endpoints (list of float): List of y coordinates for endpoints.
        indices (list of int): List of indices that define the polygon vertices.
        color (str): Color of the polygon face.
        label (str): Label for the polygon in the plot.

        Returns:
        ----------
        None: This function does not return any value.
        """
        midpoint_25_52 = ((x_endpoints[25] + x_endpoints[52]) / 2, (y_endpoints[25] + y_endpoints[52]) / 2)
        midpoint_54_51 = ((x_endpoints[54] + x_endpoints[51]) / 2, (y_endpoints[54] + y_endpoints[51]) / 2)

        coords = [
            (x_endpoints[25], y_endpoints[25]),
            midpoint_25_52,
            midpoint_54_51,
            (x_endpoints[51], y_endpoints[51]),
            (x_endpoints[25], y_endpoints[25])
        ]

        path_vertices = coords
        codes = [Path.MOVETO] + [Path.LINETO] * (len(coords) - 2) + [Path.CLOSEPOLY]
        path = Path(path_vertices, codes)
        patch = PathPatch(path, facecolor=color, edgecolor='black', alpha=0.5, label=label)
        plt.gca().add_patch(patch)

        road_lane_paths[0][100] = path

    def process_opendrive_file(self, filepath):
        """
        Process an OpenDRIVE file to extract and visualize road and lane information.

        Parameters:
        ----------
        filepath (str): Path to the OpenDRIVE file.

        Returns:
        ----------
        dict: A dictionary storing paths for different road lanes as per the OpenDRIVE specifications.
        """
        tree = ET.parse(filepath)
        root = tree.getroot()
        previous_lane_coords = {}
        plt.figure(figsize=(10, 5))
        self.road_lane_paths = {}
        x_endpoints = []
        y_endpoints = []
        road_endpoint_ids = []

        road_ids_of_interest = {'0', '5', '6'}

        for road in root.findall('road'):
            road_id = road.get('id')
            if road_id in road_ids_of_interest:
                print(f"Processing road ID: {road_id}")
                previous_lane_coords[int(road_id)] = {}
                self.road_lane_paths[int(road_id)] = {}
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

                    paramPoly3 = geometry.find('paramPoly3')
                    if paramPoly3 is not None:
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
                        u_values = aU + bU * t_values + cU * t_values ** 2 + dU * t_values ** 3
                        v_values = aV + bV * t_values + cV * t_values ** 2 + dV * t_values ** 3

                        lane_line_x = x + u_values * np.cos(hdg) - v_values * np.sin(hdg)
                        lane_line_y = y + u_values * np.sin(hdg) + v_values * np.cos(hdg)
                        plt.plot(lane_line_x, lane_line_y, 'k--', label=f'ParamPoly3 Road ID {road_id}')
                        type = 'paramPoly3'
                        geometry_data.append((s_start, length, t_values, lane_line_x, lane_line_y, hdg, u_values, v_values, x, y, type))

                    elif geometry.find('line') is not None:
                        print("This is a straight line geometry.")
                        points = np.linspace(0, length, num=1000)
                        lane_line_x = x + points * np.cos(hdg)
                        lane_line_y = y + points * np.sin(hdg)
                        plt.plot(lane_line_x, lane_line_y, 'k--', label=f'Straight Line Road ID {road_id}')
                        type = 'line'
                        geometry_data.append((s_start, length, points, lane_line_x, lane_line_y, hdg, 0, 0, x, y, type))

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
                        geometry_data.append((s_start, length, t_values, lane_line_x, lane_line_y, hdg, 0, 0, x, y, type))

                    elif geometry.find('arc') is not None:
                        print("This is an arc geometry.")
                        arc = geometry.find('arc')
                        curvature = float(arc.get('curvature'))
                        points = np.linspace(0, length, num=1000)
                        
                        radius = 1 / curvature if curvature != 0 else float('inf')
                        theta = hdg + curvature * points
                        lane_line_x = x + radius * (np.sin(theta) - np.sin(hdg))
                        lane_line_y = y - radius * (np.cos(theta) - np.cos(hdg))

                        plt.plot(lane_line_x, lane_line_y, 'k--', label=f'Arc Road ID {road_id}')
                        type = 'arc'
                        geometry_data.append((s_start, length, theta, lane_line_x, lane_line_y, hdg, 0, 0, x, y, type))

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
                            if lane_type == "driving" or lane_type == "restricted" or lane_type == "parking":
                                lane_id = int(lane.get('id'))
                                width_data = []
                                compte_width = 1
                                for widthElement in lane.findall('.//width'):
                                    if compte_width != 1:
                                        break
                                    total_s = float(widthElement.get('sOffset')) + ls_s
                                    a = float(widthElement.get('a'))
                                    b = float(widthElement.get('b'))
                                    c = float(widthElement.get('c'))
                                    d = float(widthElement.get('d'))
                                    compte_width += 1

                                    for (g_s_start, g_length, g_t_values, g_x, g_y, g_hdg, u_values, v_values, x, y, type) in geometry_data:
                                        ds = total_s - g_s_start
                                        lane_widths = [self.calculate_width(point - ds, a, b, c, d) for point in g_t_values]
                                        width_data.append(lane_widths)
                                        lanes_data.append((lane_id, width_data, g_hdg, x, y, g_t_values, type))

                                if lane_type == "driving" or lane_type == "parking":
                                    driving_lanes.append((lane_id, width_data))

                        driving_lanes.sort(key=lambda x: x[0])
                        positive_lanes = sorted((lane for lane in lanes_data if lane[0] > 0), key=lambda x: x[0])
                        negative_lanes = sorted((lane for lane in lanes_data if lane[0] < 0), key=lambda x: x[0], reverse=True)
                        min_lane_id, max_lane_id = driving_lanes[0][0], driving_lanes[-1][0]

                        num_geometries = len(geometry_data)
                        num_points_per_geometry = 1000

                        accumulated_widths = [[0 for _ in range(num_points_per_geometry)] for _ in range(num_geometries)]
                        accumulated_widths2 = [[0 for _ in range(num_points_per_geometry)] for _ in range(num_geometries)]
                        geometry_index = 0

                        for lanes_data in [positive_lanes, negative_lanes]:
                            last_lane_id = lanes_data[0][0]
                            index_geometry_id = -1
                            for lane_id, all_widths, g_hdg, x, y, points, type in lanes_data:
                                if last_lane_id == lane_id:
                                    index_geometry_id += 1
                                elif last_lane_id != lane_id:
                                    index_geometry_id = 0
                                    last_lane_id = lane_id
                                lane_line_x = []
                                lane_line_y = []
                                curvature = float(arc.get('curvature'))
                                for index, width_at_point in enumerate(all_widths[0]):
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
                                        if ((index == 0 and compte == 1) or (index == len(all_widths[0]) - 1 and compte == 1)):
                                            x_endpoints.append(point_width_x)
                                            y_endpoints.append(point_width_y)
                                            road_endpoint_ids.append(road_id)

                                plt.plot(lane_line_x, lane_line_y, label=f"Lane ID {lane_id}")
                                if int(road_id) not in previous_lane_coords:
                                    previous_lane_coords[int(road_id)] = {}
                                if lane_id not in previous_lane_coords[int(road_id)]:
                                    previous_lane_coords[int(road_id)][lane_id] = {}
                                if geometry_index not in previous_lane_coords[int(road_id)][lane_id]:
                                    previous_lane_coords[int(road_id)][lane_id][geometry_index] = (None, None)

                                previous_lane_coords[int(road_id)][lane_id][geometry_index] = (lane_line_x, lane_line_y)
                                geometry_index += 1
                    compte1 += 1

        for road_id, lanes in previous_lane_coords.items():
            lane_ids = sorted(lanes.keys())
            for i in range(len(lane_ids) - 1):
                lane_id = lane_ids[i]
                next_lane_id = lane_ids[i + 1]
                all_current_lane_coords = []
                all_next_lane_coords = []

                for geometry_index in sorted(lanes[lane_id].keys()):
                    coords = lanes[lane_id][geometry_index]
                    all_current_lane_coords.extend(zip(coords[0], coords[1]))

                for geometry_index in sorted(lanes[next_lane_id].keys()):
                    coords = lanes[next_lane_id][geometry_index]
                    all_next_lane_coords.extend(zip(coords[0], coords[1]))

                path_vertices = all_current_lane_coords + list(reversed(all_next_lane_coords))
                codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
                path = Path(path_vertices, codes)
                patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
                plt.gca().add_patch(patch)

                lane_id_call = i + 1
                self.road_lane_paths[int(road_id)][lane_id_call] = path

        self.plot_polygon_from_indices(self.road_lane_paths, x_endpoints, y_endpoints, [25, 59, 57, 52, 25], color='orange', label='Custom Polygon')
        self.plot_custom_polygon(self.road_lane_paths, x_endpoints, y_endpoints, [52, 25, 21, 53, 52], color='red', label='Custom Polygon')
        self.plot_custom_polygon2(self.road_lane_paths, x_endpoints, y_endpoints, indices=[25, 52, 54, 51], color='blue', label='Custom Polygon 2')

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
        Given coordinates (x, y), determine the corresponding road and lane ID from the road lane paths.

        Parameters:
        ----------
        road_lane_paths (dict): Dictionary containing the paths for different road lanes.
        x (float): X coordinate of the point.
        y (float): Y coordinate of the point.

        Returns:
        ----------
        tuple: Returns a tuple of (road_id, lane_id) if the point is within a path, otherwise returns (100, 1) indicating no match found, often implying the point is at junctions.
        """
        for road_id, lanes in self.road_lane_paths.items():
            for lane_id, path in lanes.items():
                if path.contains_point((x, y)):
                    return road_id, lane_id
        return 100, 1

    def update_tracks_with_lane_info(self, csv_path):
        """
        Update a CSV file with lane information based on coordinates extracted from OpenDRIVE data.

        Parameters:
        ----------
        csv_path (str): File path for the CSV to be updated.

        Returns:
        ----------
        DataFrame: Updated pandas DataFrame with new column 'road_lane' indicating the lane info.
        """
        tracks_meta_df = pd.read_csv(csv_path)

        file_path = 'aseag_04.pkl'
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
    def determine_turn_type(path):
        """
        Determines the type of turn a vehicle makes based on a sequence of road IDs.

        Parameters:
        ----------
        path (list of str): List containing concatenated road and lane IDs representing the vehicle's path.

        Returns:
        ----------
        str: Returns the type of turn ('straight', 'left', 'right') or 'N/A' if not determinable.
        """
        path = [str(item) for item in path]

        if len(path) < 2:
            return "N/A"

        first_road_id = int(path[0].split('.')[0])
        last_road_id = int(path[-1].split('.')[0])

        if first_road_id is None or last_road_id is None:
            return "N/A"

        if (first_road_id, last_road_id) in [(0, 5), (5, 0)]:
            return "straight"
        elif (first_road_id, last_road_id) in [(0, 6)]:
            return "left"
        elif (first_road_id, last_road_id) in [(5, 6), (6, 0)]:
            return "right"
        elif (first_road_id, last_road_id) in [(6, 5)]:
            return "left"

        return "N/A"

    def process_tracks(self, df):
        """
        Processes a DataFrame of vehicle tracks to determine the type of turn taken based on road lanes.

        Parameters:
        ----------
        df (DataFrame): DataFrame containing vehicle tracks with columns 'trackId' and 'road_lane'.

        Returns:
        ----------
        DataFrame: Updated DataFrame with an additional column 'turn_type' showing the type of turn each trackId makes.
        """
        df.sort_values(by=['trackId', 'frame'], inplace=True)
        grouped = df.groupby('trackId')['road_lane'].apply(list).reset_index()
        grouped['unique_path'] = grouped['road_lane'].apply(lambda x: [k for i, k in enumerate(x) if i == 0 or k != x[i - 1]])
        grouped['turn_type'] = grouped['unique_path'].apply(self.determine_turn_type)
        result = grouped[['trackId', 'unique_path', 'turn_type']]

        grouped['turn_type'] = grouped['unique_path'].apply(self.determine_turn_type)
        turn_type_dict = grouped.set_index('trackId')['turn_type'].to_dict()
        df['turn_type'] = df['trackId'].map(turn_type_dict)

        return df
