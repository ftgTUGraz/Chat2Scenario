import xml.etree.ElementTree as ET
import math
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd
import pickle

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

def find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_ids):
    """
    Identify the two nearest endpoints for each road based on provided coordinates.

    Parameters:
    ----------
    x_endpoints (list): List of x-coordinates for road endpoints.
    y_endpoints (list): List of y-coordinates for road endpoints.
    road_ids (list): List of road IDs corresponding to each endpoint.

    Returns:
    ----------
    tuple: Contains two elements:
        1. A dictionary mapping each road ID to a list of the two nearest endpoint indices.
        2. A list of polygon junction points derived from these nearest endpoints.
    """
    num_roads = len(set(road_ids))  # Number of roads
    unique_road_ids = set(road_ids)  # Create a set to remove duplicates, unordered
    sorted_road_ids = sorted(unique_road_ids)  # Sort the elements of the set
    nearest_endpoints_per_road = {str(road_id): [] for road_id in sorted_road_ids}

    for i in range(len(x_endpoints)):
        current_road_id = str(road_ids[i])  # Use string type as the key
        nearest_distances = sorted(
            [(j, math.sqrt((x_endpoints[i] - x_endpoints[j])**2 + (y_endpoints[i] - y_endpoints[j])**2))
            for j in range(len(x_endpoints)) if str(road_ids[j]) != current_road_id],
            key=lambda x: x[1]
        )

        # Record the two nearest endpoints for each road, including distance
        if nearest_distances:
            nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[0][0], nearest_distances[0][1]))

    # Ensure the selected two endpoints are not the same starting point
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
            polygan_jonctions.append((x_endpoints[sorted_elements[0]],y_endpoints[sorted_elements[0]]))
            cpt += 1
        polygan_jonctions.append((x_endpoints[sorted_elements[1]],y_endpoints[sorted_elements[1]]))
        for first,seconds,third in selected_endpoints:
            if first == sorted_elements[1]:
                polygan_jonctions.append((x_endpoints[seconds],y_endpoints[seconds]))


    return two_nearest_endpoints_per_road , polygan_jonctions

def connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids):

    """
    Connect nearest endpoints for each road to form a continuous path.

    Parameters:
    ----------
    two_nearest_endpoints_per_road (dict): Dictionary containing mapping from road ID to nearest endpoint indices.
    road_endpoint_ids (list): List of road IDs corresponding to each endpoint.

    Returns:
    ----------
    list: List of tuples representing connected endpoint indices.
    """
    # Collection for storing connections, formatted as: (endpoint_index, connected_endpoint_index)
    connections = []
    connected_indices = set()  # Used to store already connected endpoints
    
    # Iterate through the two nearest endpoints for each road
    for road_id, endpoints_info in two_nearest_endpoints_per_road.items():
        for endpoint_info in endpoints_info:
            start_index, end_index, _ = endpoint_info
            # Check if the endpoints have already been connected
            if start_index not in connected_indices and end_index not in connected_indices:
                connections.append((start_index, end_index))
                connected_indices.update([start_index, end_index])  # Add endpoints to the connected set
    
    return connections



def process_opendrive_file(filepath):
    """
    Process an OpenDRIVE file to extract and visualize road and lane data.

    Parameters:
    ----------
    filepath (str): Path to the OpenDRIVE file.

    Returns:
    ----------
    dict: Dictionary containing road and lane path data.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    previous_lane_coords ={}
    plt.figure(figsize=(10, 5))
    road_lane_paths = {} 
    x_endpoints = []
    y_endpoints = []
    road_endpoint_ids = []

    # Extract a list of road IDs of interest
    road_ids_of_interest = {'0', '1', '3', '4'}

    for road in root.findall('road'):
        road_id = road.get('id')
        if road_id in road_ids_of_interest:
            print(f"Processing road ID: {road_id}")
            previous_lane_coords[int(road_id)] = {}
            road_lane_paths[int(road_id)] = {}
            for geometry in road.findall('.//geometry'):
                param_poly3 = geometry.find('.//paramPoly3')

                if param_poly3 is not None:
                    # Additional processing when encountering paramPoly3 type with more than two lanes in a road
                    # Use FrenetToGlobal_jonctions.py script when encountering paramPoly3 type with two lanes in a road
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

                    for laneSection in road.findall('.//laneSection'):
                        ls_s = float(laneSection.get('s'))
                        lanes_data = []
                        driving_lanes = []

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
                                    s = sOffset + ls_s

                                    lane_widths = [calculate_width(point + s, a, b, c, d) for point in points]
                                    width_data.append(lane_widths)

                                lanes_data.append((lane_id, width_data))

                                if lane_type == "driving":
                                    driving_lanes.append((lane_id, width_data))

                        # Sort lanes by ID, negative IDs decreasing, positive IDs increasing
                        driving_lanes.sort(key=lambda x: x[0])
                        positive_lanes = sorted((lane for lane in lanes_data if lane[0] > 0), key=lambda x: x[0])
    
                        negative_lanes = sorted((lane for lane in lanes_data if lane[0] < 0), key=lambda x: x[0], reverse=True)

                        min_lane_id, max_lane_id = driving_lanes[0][0], driving_lanes[-1][0]

                        # Process sorted lane data
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
                                        if (index==0 or index == len(all_widths[0])-1 ):
                                            x_endpoints.append(point_width_x)
                                            y_endpoints.append(point_width_y)
                                            road_endpoint_ids.append(road_id)

                                plt.plot(lane_line_x, lane_line_y, label=f"Lane ID {lane_id}")
                                
                                previous_lane_coords[int(road_id)][lane_id] = (lane_line_x, lane_line_y)


    # Create polygon patches
    for road_id, lanes in previous_lane_coords.items():
        lane_ids = sorted(lanes.keys())
        for i in range(len(lane_ids) - 1):
            lane_id = lane_ids[i]
            # Artificially set the minimum lane number as 1
            lane_id_call = i + 1
            next_lane_id = lane_ids[i + 1]
            current_lane_x, current_lane_y = lanes[lane_id]
            next_lane_x, next_lane_y = lanes[next_lane_id]

            # Create polygon paths
            path_vertices = list(zip(current_lane_x, current_lane_y)) + list(zip(reversed(next_lane_x), reversed(next_lane_y)))
            codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
            path = Path(path_vertices, codes)
            patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
            plt.gca().add_patch(patch)

            road_lane_paths[int(road_id)][lane_id_call] = path

    # Calculate the two nearest endpoints for each road with other roads
    two_nearest_endpoints_per_road , polygan_jonctions = find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_endpoint_ids)

    # Create connections
    connections = connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids)

    # Draw connection points
    for connection in connections:
        plt.plot([x_endpoints[connection[0]], x_endpoints[connection[1]]],
                [y_endpoints[connection[0]], y_endpoints[connection[1]]], 'r-')

    # Draw connection points
    for road_id, nearest_endpoints in two_nearest_endpoints_per_road.items():
        for endpoint_info in nearest_endpoints:
            endpoint_index = endpoint_info[0]
            plt.scatter(x_endpoints[endpoint_index], y_endpoints[endpoint_index], c='blue')

    # Create polygon for junctions
    # Create a list of polygon vertices, ensuring it is two-dimensional
    path_vertices = polygan_jonctions
    codes = [Path.MOVETO] + [Path.LINETO] * (len(path_vertices) - 2) + [Path.CLOSEPOLY]
    path = Path(path_vertices, codes)
    patch = PathPatch(path, facecolor='gray', edgecolor='none', alpha=0.5)
    plt.gca().add_patch(patch)
    road_lane_paths[100] = {}
    road_lane_paths[100][1] = path



    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Visualization of Roads and Lanes")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

    return road_lane_paths

def find_lane_by_coordinates(road_lane_paths, x, y):

    """
    Determine the road and lane ID at a given coordinate.

    Parameters:
    ----------
    road_lane_paths (dict): Dictionary containing paths for each road and lane.
    x (float): X-coordinate.
    y (float): Y-coordinate.

    Returns:
    ----------
    tuple: Contains road ID and lane ID if found, otherwise (-1, 1).
    """

    """ Given a point (x, y), determine the road and lane ID it belongs to. """
    for road_id, lanes in road_lane_paths.items():
        for lane_id, path in lanes.items():
            if path.contains_point((x, y)):
                return road_id, lane_id
    return -1, 1  # Return -1, 1 if no matching lane is found, which typically indicates the point is within a junction.

def update_tracks_with_lane_info(csv_path):

    """
    Extracts the road ID from a combined 'road.lane' string.

    Parameters:
    ----------
    road_lane (str): String in the format 'road.lane'.

    Returns:
    ----------
    int: Extracted road ID or None if the format is incorrect.
    """
    # Read the CSV file
    tracks_meta_df = pd.read_csv(csv_path)

    # Process the OpenDRIVE file to get road and lane path data
    #road_lane_paths = process_opendrive_file(opendrive_file_path)
    #save_road_lane_paths_pickle(road_lane_paths, 'bendplatz_01.pkl')
    file_path = 'bendplatz_01.pkl'
    road_lane_paths = load_road_lane_paths_pickle(file_path)    

    # Add a new column for road-lane information
    tracks_meta_df['road_lane'] = ''

    # Process each row in the DataFrame
    for index, row in tracks_meta_df.iterrows():
        x, y = row['xCenter'], row['yCenter']
        road_id, lane_id = find_lane_by_coordinates(road_lane_paths, x, y)
        tracks_meta_df.at[index, 'road_lane'] = f'{road_id}.{lane_id}'

    # Optionally, save the modified DataFrame to a new CSV file
    #updated_csv_path = csv_path.replace('.csv', '_updated.csv')
    #tracks_meta_df.to_csv(updated_csv_path, index=False)

    # Return the updated DataFrame
    return tracks_meta_df

def extract_road_id(road_lane):
    """
    Determines the type of turn based on road IDs before and after a specific segment.

    Parameters:
    ----------
    path (list): List of road.lane strings representing a vehicle's path.

    Returns:
    ----------
    str: Type of turn ('straight', 'right', 'left', or 'N/A' if not applicable).
    """
    """ Extracts the road ID from a 'road.lane' string. """
    return int(road_lane.split('.')[0]) if '.' in road_lane else None

def determine_turn_type(path):
    """
    Determines the type of turn based on road IDs before and after a specific segment.

    Parameters:
    ----------
    path (list): List of road.lane strings representing a vehicle's path.

    Returns:
    ----------
    str: Type of turn ('straight', 'right', 'left', or 'N/A' if not applicable).
    """
    """ Determines the turning type based on road IDs before and after '100.1'. """
    # Convert path elements to strings for consistent comparison
    path = [str(item) for item in path]
    
    if '100.1' not in path:
        return "N/A"
    if len(path) < 3:
        return "N/A"

    # Extract road IDs and determine turn type
    first_road_id = int(path[0].split('.')[0])
    last_road_id = int(path[-1].split('.')[0])
    diff = first_road_id - last_road_id

    if diff == 0 or abs(diff) % 3 == 0:
        return "straight"
    elif (diff > 0 and diff != 4) or diff == -4:
        return "right"
    elif (diff < 0 and diff != -4) or diff == 4:
        return "left"
    return "N/A"



def process_tracks(df):
    """
    Process tracks to determine the type of turn at junctions based on road lane paths.

    Parameters:
    ----------
    df (DataFrame): DataFrame containing track data.

    Returns:
    ----------
    DataFrame: DataFrame with updated turn type information.
    """
    #df = pd.read_csv(file_path)
    df.sort_values(by=['trackId', 'frame'], inplace=True)
    grouped = df.groupby('trackId')['road_lane'].apply(list).reset_index()
    grouped['unique_path'] = grouped['road_lane'].apply(lambda x: [k for i, k in enumerate(x) if i == 0 or k != x[i-1]])
    grouped['turn_type'] = grouped['unique_path'].apply(determine_turn_type)
    result = grouped[['trackId', 'unique_path', 'turn_type']]
    #result.to_csv('07_processed_tracks.csv', index=False)

    grouped['turn_type'] = grouped['unique_path'].apply(determine_turn_type)
    turn_type_dict = grouped.set_index('trackId')['turn_type'].to_dict()
    df['turn_type'] = df['trackId'].map(turn_type_dict)

    return df
    
