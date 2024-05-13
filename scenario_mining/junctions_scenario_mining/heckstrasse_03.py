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
    a, b, c, d (float): Polynomial coefficients for constant, linear, squared, and cubic terms respectively.

    Returns:
    ----------
    float: The calculated width at distance ds.
    """
    return a + b * ds + c * (ds**2) + d * (ds**3)

def find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_ids):
    """
    Identify two nearest endpoints per road using their coordinates and road identifiers.

    Parameters:
    ----------
    x_endpoints, y_endpoints (list of float): Lists of x and y coordinates.
    road_ids (list of int): Road identifiers for each endpoint.

    Returns:
    ----------
    tuple: A tuple containing two dictionaries detailing the nearest endpoints per road and junction coordinates.
    """
    num_roads = len(set(road_ids))  # Number of roads
    unique_road_ids = set(road_ids)  # Create a set to remove duplicates, unordered
    sorted_road_ids = sorted(unique_road_ids)  # Sort elements in the set
    nearest_endpoints_per_road = {str(road_id): [] for road_id in sorted_road_ids}

    for i in range(len(x_endpoints)):
        current_road_id = str(road_ids[i])  # Use string type as key
        nearest_distances = sorted(
            [(j, math.sqrt((x_endpoints[i] - x_endpoints[j])**2 + (y_endpoints[i] - y_endpoints[j])**2))
            for j in range(len(x_endpoints)) if str(road_ids[j]) != current_road_id],
            key=lambda x: x[1]
        )
        if current_road_id == '1' and i==3 :
            nearest_distances[0] = (6,math.sqrt((x_endpoints[i] - x_endpoints[6])**2 + (y_endpoints[i] - y_endpoints[6])**2))

        # Record the two nearest endpoints per road, including the distance
        if nearest_distances:
            nearest_endpoints_per_road[current_road_id].append((i, nearest_distances[0][0], nearest_distances[0][1]))

    # Ensure the selected two endpoints are not the same starting endpoint
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
    Connect the nearest endpoints for each road based on previously identified nearest points.

    Parameters:
    ----------
    two_nearest_endpoints_per_road (dict): Dictionary detailing the nearest endpoints per road.
    road_endpoint_ids (list of int): List of endpoint identifiers corresponding to roads.

    Returns:
    ----------
    list: A list of tuples representing connections between endpoints.
    """
    # Set to store connections: (endpoint_index, connected_endpoint_index)
    connections = []
    connected_indices = set()  # Set to store already connected endpoints
    
    # Iterate over the two nearest endpoints for each road
    for road_id, endpoints_info in two_nearest_endpoints_per_road.items():
        for endpoint_info in endpoints_info:
            start_index, end_index, _ = endpoint_info
            # Check if the endpoint has already been connected
            if start_index not in connected_indices and end_index not in connected_indices:
                connections.append((start_index, end_index))
                connected_indices.update([start_index, end_index])  # Add endpoints to the connected set
    
    return connections



def process_opendrive_file(filepath):
    """
    Process an OpenDRIVE file to visualize roads and lanes, and calculate connections between nearest road endpoints.

    Parameters:
    ----------
    filepath (str): Path to the OpenDRIVE file.

    Returns:
    ----------
    dict: A dictionary of road lane paths, which includes the visualization path objects.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    previous_lane_coords ={}
    plt.figure(figsize=(10, 5))
    road_lane_paths = {} 
    x_endpoints = []
    y_endpoints = []
    road_endpoint_ids = []

    # Extract the list of road IDs of interest
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
                    # To be completed when encountering param_poly3 type and more than two lanes in one road
                    # For param_poly3 type and two lanes in one road, FrenetToGlobal_jonctions.py can be used
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

                            # Sort lanes by ID, decreasing for negative IDs, increasing for positive IDs
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
                                            if ((index==0 and compte ==1) or (index == len(all_widths[0])-1 and compte ==1)):
                                                x_endpoints.append(point_width_x)
                                                y_endpoints.append(point_width_y)
                                                road_endpoint_ids.append(road_id)

                                    plt.plot(lane_line_x, lane_line_y, label=f"Lane ID {lane_id}")
                                    
                                    previous_lane_coords[int(road_id)][lane_id] = (lane_line_x, lane_line_y)
                        compte1 += 1


    # Create polygon patches
    for road_id, lanes in previous_lane_coords.items():
        lane_ids = sorted(lanes.keys())
        for i in range(len(lane_ids) - 1):
            lane_id = lane_ids[i]
            # Manually set the minimum lane number as 1
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
      
    # Calculate the two nearest endpoints for each road to other roads
    two_nearest_endpoints_per_road , polygan_jonctions = find_two_nearest_endpoints_per_road(x_endpoints, y_endpoints, road_endpoint_ids)

    # Create connections
    connections = connect_nearest_endpoints(two_nearest_endpoints_per_road, road_endpoint_ids)

    # Plot connections
    for connection in connections:
        plt.plot([x_endpoints[connection[0]], x_endpoints[connection[1]]],
                [y_endpoints[connection[0]], y_endpoints[connection[1]]], 'r-')

    # Plot endpoints used for connections
    for road_id, nearest_endpoints in two_nearest_endpoints_per_road.items():
        for endpoint_info in nearest_endpoints:
            endpoint_index = endpoint_info[0]
            plt.scatter(x_endpoints[endpoint_index], y_endpoints[endpoint_index], c='blue')
    '''
    # Create polygan for jonctions
    # Create a list of polygon vertices, make sure it is two-dimensional
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
    """
    Given a point (x, y), determine the road and lane ID it belongs to based on the road lane paths.

    Parameters:
    ----------
    road_lane_paths (dict): Dictionary of road lane paths.
    x (float): X coordinate of the point.
    y (float): Y coordinate of the point.

    Returns:
    ----------
    tuple: A tuple containing the road ID and lane ID that the point belongs to.
    """
    for road_id, lanes in road_lane_paths.items():
        for lane_id, path in lanes.items():
            if path.contains_point((x, y)):
                return road_id, lane_id
    return 100, 1  # If no matching lane is found, return -1,1, indicating in the junctions

def update_tracks_with_lane_info(csv_path):
    """
    Update a CSV file of tracks with lane information using the road lane paths from an OpenDRIVE file.

    Parameters:
    ----------
    csv_path (str): Path to the CSV file of tracks.

    Returns:
    ----------
    DataFrame: Updated pandas DataFrame with road lane information for each track.
    """
    # Read the CSV file
    tracks_meta_df = pd.read_csv(csv_path)

    # Process the OpenDRIVE file
    #road_lane_paths = process_opendrive_file(opendrive_file_path)

    #save_road_lane_paths_pickle(road_lane_paths, 'heckstrasse_03.pkl')
    file_path = 'heckstrasse_03.pkl'
    road_lane_paths = load_road_lane_paths_pickle(file_path)   


    # Add a column
    tracks_meta_df['road_lane'] = ''

    # Process DataFrame row by row
    for index, row in tracks_meta_df.iterrows():
        x, y = row['xCenter'], row['yCenter']
        road_id, lane_id = find_lane_by_coordinates(road_lane_paths, x, y)
        tracks_meta_df.at[index, 'road_lane'] = f'{road_id}.{lane_id}'

    # Save the modified DataFrame
    #updated_csv_path = csv_path.replace('.csv', '_updated.csv')
    #tracks_meta_df.to_csv(updated_csv_path, index=False)

    # Return the path of the updated DataFrame
    return tracks_meta_df

def extract_road_id(road_lane):
    """
    Extracts the road ID from a 'road.lane' string format.

    Parameters:
    ----------
    road_lane (str): The 'road.lane' string from which to extract the road ID.

    Returns:
    ----------
    int: The extracted road ID, or None if the format is incorrect.
    """
    return int(road_lane.split('.')[0]) if '.' in road_lane else None
def determine_turn_type(path):
    """
    Determines the turning type based on specific pairs of road IDs before and after a junction.

    Parameters:
    ----------
    path (list of str): List of 'road.lane' strings representing a path of travel.

    Returns:
    ----------
    str: The type of turn (e.g., 'left', 'right', 'straight'), or 'N/A' if no valid type is determined.
    """
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
    """
    Process track data from a DataFrame to identify the turn type for each track based on road lane paths.

    Parameters:
    ----------
    df (DataFrame): The DataFrame containing track and road lane data.

    Returns:
    ----------
    DataFrame: The DataFrame with added information about turn types for each track.
    """
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
    
