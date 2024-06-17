"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import streamlit as st
import time
from utils.helper_original_scenario import *
import sympy as sp
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import argparse
from loguru import logger

from src.track_visualizer import TrackVisualizer, DataError
from src.tracks_import import read_from_csv
from src.run_track_visualization import *
from scenario_mining.junctions_scenario_mining.bendplatz_01 import *
import re
import scenario_mining.junctions_scenario_mining.bendplatz_01 as bendplatz
import scenario_mining.junctions_scenario_mining.frankenburg_02 as frankenburg
import scenario_mining.junctions_scenario_mining.heckstrasse_03 as heckstrasse
import scenario_mining.junctions_scenario_mining.aseag_04 as aseag
import matplotlib.patches as patches
import numpy as np
from data import lane_markings_data

def extract_xosc_data(dataset_load, output_path, ttc_threshold, metric_option, dataset_option):
    """
    Generate OpenSCENARIO files in website (for esmini, Carla, ...)

    Parameters:
    ----------
    Inputs:
        input_path (str): path of input data 
        output_path (str): path of output data 
        metric_threshold (float): time-to-collision threshold to filter scenarios from dataset 
        metric_option (str): metric option selected by user
        dataset_option (str): dataset option selected by user
    Returns:
        ---
    ----------
    """  
    generate_xosc(dataset_load, output_path, ttc_threshold, metric_option, dataset_option)


def extract_xosc_with_preview(ego, target, output_path):
    """
    Generate OpenSCENARIO files if user previewed the seanarios (no need to search again)

    Parameters:
    ----------
    Inputs:
        ego (list): a list containing all fictive ego vehicles in format of dataframe
        target (dictionary): a dictionary containing all target vehicles, each ego
        output_path (str): path of output data 
    Returns:
        ---
    ----------
    """  
    # Initialize progress bar
    progress_bar_xosc = st.progress(0)
    idx_progress_xosc = 0
    # Generate xosc for each ego vehicle
    for fictive_ego_sampled in ego:
        sim_time = len(fictive_ego_sampled)  
        target_tracks_sampled = target[fictive_ego_sampled['id'][0]]
        output_path_file = output_path + f"\\scenario_{fictive_ego_sampled['id'][0]}.xosc"
        xosc_generation(sim_time, output_path_file, fictive_ego_sampled, target_tracks_sampled)
        # Update progress bar
        time.sleep(1)
        progress_bar_xosc.progress((idx_progress_xosc + 1)/len(ego))
        idx_progress_xosc += 1


def generate_xosc_for_self_define(output_path, fictive_ego_list_sampled, fictive_target_dicts_sampled):
    """
    generate xosc file when metric is self-defined

    Parameters:
    ----------
    Inputs:
        output_path (str): path of output data 
        fictive_ego_list_sampled (list): a list containing all fictive ego vehicles in format of dataframe
        fictive_target_dicts_sampled (dict): a dictionary containing all target vehicles, each ego
        vehicle corresponds to a list that contains several target vehicles in format of dataframe.
    Returns:
        ---
    ----------
    """  
    # Initialize progress bar
    progress_bar_xosc = st.progress(0)
    idx_progress_xosc = 0
    # Generate xosc for each ego vehicle
    for fictive_ego_sampled in fictive_ego_list_sampled:
        sim_time = len(fictive_ego_sampled)  
        target_tracks_sampled = fictive_target_dicts_sampled[fictive_ego_sampled['id'][0]]
        output_path_file = output_path + f"\\scenario_{fictive_ego_sampled['id'][0]}.xosc"
        xosc_generation(sim_time, output_path_file, fictive_ego_sampled, target_tracks_sampled)
        # Update progress bar
        time.sleep(1)
        progress_bar_xosc.progress((idx_progress_xosc + 1)/len(fictive_ego_list_sampled))
        idx_progress_xosc += 1


def extract_txt_data(input_path, output_path, metric_threshold, metric_option, dataset_option):
    """
    Generate txt files in website (for CarMaker)

    Parameters:
    ----------
    Inputs:
        input_path (str): path of input data 
        output_path (str): path of output data
        metric_threshold (float): time-to-collision threshold to filter scenarios from dataset 
        metric_option (str): metric option selected by user
        dataset_option (str): dataset option selected by user
    Returns:
        ---
    ----------
    """  
    data = pd.read_csv(input_path)
    fictive_ego_list_sampled, fictive_target_dicts_sampled = search_scenario(data, metric_threshold, metric_option, dataset_option)
    progress_bar = st.progress(0)
    idx_progress = 0

    for fictive_ego in fictive_ego_list_sampled:
        # write each scenario in txt
        fictive_ego_id = fictive_ego['id'][0]
        fictive_target_list = fictive_target_dicts_sampled[fictive_ego_id]
        scenario_time = fictive_target_list[0]['time']

        # file name for each scenario
        file_name = "\\scenario" + f"_{fictive_ego_id}" + ".txt"
        output_path_name = output_path + file_name

        df = pd.DataFrame()
        df['time'] = scenario_time
        for fictive_target_vehicle in fictive_target_list:
            curr_pos_x = fictive_target_vehicle['x']
            curr_pos_y = fictive_target_vehicle['y']
            curr_target_id = fictive_target_vehicle['id'][0]
            df[f'x_{curr_target_id}'] = curr_pos_x
            df[f'y_{curr_target_id}'] = -curr_pos_y

        csv_data = df.to_csv(index=False, header=True)
        csv_data = '#' + csv_data
        with open(output_path_name, "w") as text_file:
            text_file.write(csv_data)
        
        # update progress bar
        time.sleep(1)
        progress_bar.progress((idx_progress + 1)/len(fictive_ego_list_sampled))
        idx_progress += 1


def extract_txt_with_preview(output_path, fictive_ego_list_sampled, fictive_target_dicts_sampled):
    """
    Generate txt files if user previewed searched scenarios

    Parameters:
    ----------
    Inputs:
        output_path (str): path of output data 
        fictive_ego_list_sampled (list): a list containing all fictive ego vehicles in format of dataframe
        fictive_target_dicts_sampled (dict): a dictionary containing all target vehicles, each ego
        vehicle corresponds to a list that contains several target vehicles in format of dataframe.
    Returns:
        ---
    ----------
    """  
    progress_bar = st.progress(0)
    idx_progress = 0

    for fictive_ego in fictive_ego_list_sampled:
        # write each scenario in txt
        fictive_ego_id = fictive_ego['id'][0]
        fictive_target_list = fictive_target_dicts_sampled[fictive_ego_id]
        scenario_time = fictive_target_list[0]['time']

        # file name for each scenario
        file_name = "\\scenario" + f"_{fictive_ego_id}" + ".txt"
        output_path_name = output_path + file_name

        df = pd.DataFrame()
        df['time'] = scenario_time
        for fictive_target_vehicle in fictive_target_list:
            curr_pos_x = fictive_target_vehicle['x']
            curr_pos_y = fictive_target_vehicle['y']
            curr_target_id = fictive_target_vehicle['id'][0]
            df[f'x_{curr_target_id}'] = curr_pos_x
            df[f'y_{curr_target_id}'] = -curr_pos_y

        csv_data = df.to_csv(index=False, header=True)
        csv_data = '#' + csv_data
        with open(output_path_name, "w") as text_file:
            text_file.write(csv_data)
        
        # update progress bar
        time.sleep(1)
        progress_bar.progress((idx_progress + 1)/len(fictive_ego_list_sampled))
        idx_progress += 1


def IPG_CarMaker_text_generation(output_path, ego_track, target_tracks):
    """
    Generate text file to visualize scenarios in IPG CarMaker

    Parameters:
    ----------
    Inputs:
        output_path (path): Path of output file. (path + filename)
        ego_track (dataframe): a dataframe containing ego vehicle track
        target_tracks (list): a list containing target vehicle(s)' track(s)

    Returns:
        ---
    ----------
    """  
    ego_track = ego_track.reset_index(drop=True)
    # Prepare data for IPG CarMaker text
    time_col = ego_track['time']
    ego_id = ego_track['id'].iloc[0]
    ego_x = ego_track['x']
    ego_y = ego_track['y']

    # Convert these data into dataframe: time, x_{ego_id}, y_{ego_id}, x_{tgt_id}, y_{tgt_id}, ...
    df = pd.DataFrame()
    df['time'] = time_col
    df[f'x_{ego_id}'] = ego_x
    df[f'y_{ego_id}'] = ego_y

    # Iterate over each target vehicle track
    for target_track in target_tracks:
        target_track = target_track.reset_index(drop=True)
        tgt_id = target_track['id'].iloc[0]

        # Check if the target track has common times with the ego track
        common_times = df['time'].isin(target_track['time'])
        if not common_times.any():
            continue  # If no common times, skip this target

        # Add current target trajectory into dataframe
        tgt_x = target_track['x'] 
        tgt_y = target_track['y'] 
        df[f'x_{tgt_id}'] = tgt_x
        df[f'y_{tgt_id}'] = tgt_y

    csv_data = df.to_csv(index=False, header=True)
    csv_data = '#' + csv_data

    # Save the data
    with open(output_path, 'w') as text_file:
        text_file.write(csv_data)


def generate_txt_for_self_define(output_path, fictive_ego_list_sampled, fictive_target_dicts_sampled):
    """
    Generate txt files for self-defined metric

    Parameters:
    ----------
    Inputs:
        output_path (str): path of output data 
        fictive_ego_list_sampled (list): a list containing all fictive ego vehicles in format of dataframe
        fictive_target_dicts_sampled (dict): a dictionary containing all target vehicles, each ego
        vehicle corresponds to a list that contains several target vehicles in format of dataframe.
    Returns:
        ---
    ----------
    """  
    progress_bar = st.progress(0)
    idx_progress = 0

    for fictive_ego in fictive_ego_list_sampled:
        # write each scenario in txt
        fictive_ego_id = fictive_ego['id'][0]
        fictive_target_list = fictive_target_dicts_sampled[fictive_ego_id]
        scenario_time = fictive_target_list[0]['time']

        # file name for each scenario
        file_name = "\\scenario" + f"_{fictive_ego_id}" + ".txt"
        output_path_name = output_path + file_name

        df = pd.DataFrame()
        df['time'] = scenario_time
        for fictive_target_vehicle in fictive_target_list:
            curr_pos_x = fictive_target_vehicle['x']
            curr_pos_y = fictive_target_vehicle['y']
            curr_target_id = fictive_target_vehicle['id'][0]
            df[f'x_{curr_target_id}'] = curr_pos_x
            df[f'y_{curr_target_id}'] = -curr_pos_y

        csv_data = df.to_csv(index=False, header=True)
        csv_data = '#' + csv_data
        with open(output_path_name, "w") as text_file:
            text_file.write(csv_data)
        
        # update progress bar
        time.sleep(1)
        progress_bar.progress((idx_progress + 1)/len(fictive_ego_list_sampled))
        idx_progress += 1

    
def process_equation(equation_input):
    """
    process equation input from user

    Parameters:
    ----------
    Inputs:
        equation_input: equation input by user in python format
    Returns:
    ----------
    """  
    parased_equation_code = ""
    try:
        # Define the symbolic variables for the drone dataset
        time, frame, id, x, y, width, height, xVelocity, yVelocity, \
        xAcceleration, yAcceleration, frontSightDistance, backSightDistance, \
        dhw, thw, ttc, precedingXVelocity, precedingId, followingId, \
        leftPrecedingId, leftAlongsideId, leftFollowingId, rightPrecedingId, \
        rightAlongsideId, rightFollowingId, laneId, angle, orientation, \
        yaw_rate, ego_offset = sp.symbols(
            'time frame id x y width height xVelocity yVelocity\
                  xAcceleration yAcceleration frontSightDistance backSightDistance\
                      dhw thw ttc precedingXVelocity precedingId followingId\
                          leftPrecedingId leftAlongsideId leftFollowingId rightPrecedingId\
                              rightAlongsideId rightFollowingId laneId angle orientation\
                                  yaw_rate ego_offset'
        )

        # Parse the equation using SymPy
        parsed_equation = sp.sympify(equation_input)

        # Display the parsed equation
        st.write(parsed_equation)
        parased_equation_code = st.code(f"Parsed Equation: {parsed_equation}")
    except Exception as e:
        st.error(f"Error processing the equation: {str(e)}")

    return parased_equation_code
    

def find_ax_limit(fictive_ego, fictive_targets,dataset_option):
    """
    find the limitation to fix figure axis 

    Args:
        fictive_ego (dataframe): a dataframe containing ego track
        fictive_targets (list): a list containing multiple dataframes of targets track
    
    Output:
        x_min (float): x minimum
        x_max (float): x maximum
        y_min (float): y minimum
        y_max (float): y maximum
    """
    if dataset_option == "highD":
        ego_x_min = min(fictive_ego['x'])
        ego_x_max = max(fictive_ego['x'])
        ego_y_min = min(fictive_ego['y'])
        ego_y_max = max(fictive_ego['y'])

        fictive_target_x_min = float('inf')
        fictive_target_x_max = float('-inf')
        fictive_target_y_min = float('inf')
        fictive_target_y_max = float('-inf')

        for fictive_target in fictive_targets:
            curr_x_min = min(fictive_target['x'])
            if curr_x_min < fictive_target_x_min:
                fictive_target_x_min = curr_x_min

            curr_x_max = max(fictive_target['x'])
            if curr_x_max > fictive_target_x_max:
                fictive_target_x_max = curr_x_max

            curr_y_min = min(fictive_target['y'])
            if curr_y_min < fictive_target_y_min:
                fictive_target_y_min = curr_y_min

            curr_y_max = max(fictive_target['y'])
            if curr_y_max > fictive_target_y_max:
                curr_y_max = fictive_target_y_max

        x_min = min(ego_x_min, fictive_target_x_min)
        x_max = max(ego_x_max, fictive_target_x_max)
        y_min = min(ego_y_min, fictive_target_y_min)
        y_max = max(ego_y_max, fictive_target_y_max)

    elif dataset_option == "inD":  
        ego_x_min = min(fictive_ego['xCenter'])
        ego_x_max = max(fictive_ego['xCenter'])
        ego_y_min = min(fictive_ego['yCenter'])
        ego_y_max = max(fictive_ego['yCenter'])

        tgt_x_min = min(min(fictive_target['xCenter']) for fictive_target in fictive_targets)
        tgt_x_max = max(max(fictive_target['xCenter']) for fictive_target in fictive_targets)
        tgt_y_min = min(min(fictive_target['yCenter']) for fictive_target in fictive_targets)
        tgt_y_max = max(max(fictive_target['yCenter']) for fictive_target in fictive_targets)

        x_min = min(ego_x_min, tgt_x_min)
        x_max = max(ego_x_max, tgt_x_max)
        y_min = min(ego_y_min, tgt_y_min)
        y_max = max(ego_y_max, tgt_y_max)
        
    return x_min, x_max, y_min, y_max


def check_preview_condition(reminder_holder, dataset_load, metric_option, metric_threshold, my_key, scenario_description):
    """
    Judge if all conditions are met for previewing searched scenarios

    Args:
        reminder_holder: st.empty() for warning message
        dataset_load (str): path of dataset
        metric_option (str): metric selected by user [TTC, THW, DHW, Self-define]  
        metric_threshold (float): metric threshold defined by user 
        my_key (str): openai key 
        scenario_description (str): functional scenarios input by users
    
    Output:
        meet_preview_conditions (bool): if meet preview conditions
    """
    meet_preview_conditions = False

    meet_dataset_load = True
    if dataset_load is None:
        meet_dataset_load = False
        reminder_holder.warning(":warning: Please **upload dataset**!")
    meet_metric_option = True
    if metric_option is None:
        meet_metric_option = False
        reminder_holder.warning(":warning: Please **select a metric**!")
    meet_metric_threshold = True
    if math.isnan(metric_threshold[0]):
        meet_metric_threshold = False
        reminder_holder.warning(":warning: Please **specify metric threshold**!")
    meet_my_key = True
    if my_key == "":
        meet_my_key = False
        reminder_holder.warning(":warning: Please **input your openai api key**!")
    meet_scenario_description = True
    if scenario_description == "":
        meet_scenario_description = False
        reminder_holder.warning(":warning: Please **input your scenario description**!")
    
    if meet_dataset_load and meet_metric_option and meet_metric_threshold and meet_my_key and scenario_description:
        meet_preview_conditions = True
    
    return meet_preview_conditions


def check_extract_condition(dataset_load, selected_opts, metric_threshold):
    """
    Check if meet extract conditions

    Args:
        dataset_load (str): dataset uploaded by user 
        selected_opts (str): format option (xosc/txt)
        output_path (str): download path
        metric_threshold (tuple): (min, max)
        
    Output:
        extract (bool): True: ready to extract; False: not ready
    """
    extract = None

    if dataset_load is None and len(selected_opts) > 0:
        extract = False
        st.warning(":warning: Please make sure **upload dataset** before extracting scenarios!")
    elif dataset_load is not None and len(selected_opts) == 0:
        extract = False
        st.warning(":warning: Please make sure **select format** before extracting scenarios!")
    elif dataset_load is None and len(selected_opts) == 0:
        extract = False
        st.warning(":warning: Please make sure **upload dataset** and **select format** before extracting scenarios!")
    elif math.isnan(metric_threshold[0]) or math.isnan(metric_threshold[1]):
        extract = False
        st.warning(":warning: Please specify **metric threshold**!")
    elif dataset_load and len(selected_opts) > 0 and  metric_threshold is not None:
        extract = True
    
    return extract


def check_preview_tuned_scenario(dataset_load, metric_opts, metric_threshold, scenario_lib):
    """
    Check if meet conditions to preview tuned scenarios

    Args:
        dataset_load (str): dataset uploaded by user 
        selected_opts (str): metric option
        metric_threshold (tuple): (min, max)
        scenario_lib (st.session_state.my_data): searched scenarios
    Output:
        True/False (bool): a bool value to 
    """
    if dataset_load is None:
        st.warning(":warning: Please upload **dataset**!")
        return False
    if metric_opts is None:
        st.warning(":warning: Please specify one **metric option**!")
        return False
    if math.isnan(metric_threshold[0]) or math.isnan(metric_threshold[1]):
        st.warning(":warning: Please specify **metric threshold**!")
        return False
    # check scenario library
    if len(scenario_lib['fictive_ego_list_sampled']) == 0 or len(scenario_lib['fictive_target_dicts_sampled']) == 0:
        st.warning(":warning: Please click **Preview searched scenario** or **Extract original scenario** button first!")
        return False
    
    return True

def plot_vehicle(ax, x, y,width ,length , orientation, color='blue'):
    """
    Plots a vehicle as a rotated rectangle on the given axis.
    
    Parameters:
    - ax: The matplotlib axis to plot on.
    - x, y: The center coordinates of the rectangle.
    - width, length: The width and length of the rectangle.
    - orientation: The orientation angle in degrees.
    - color: The color of the rectangle.
    """
    # Convert orientation from degrees to radians
    orientation_rad = np.radians(orientation)
    
    # Calculate the corners of the rectangle before rotation
    dx = width / 2
    dy = length / 2
    '''
    corners = np.array([
        [-dx, -dy],
        [ dx, -dy],
        [ dx,  dy],
        [-dx,  dy]
    ])
    '''
    corners = np.array([
        [-dy, -dx],
        [-dy,  dx],
        [ dy,  dx],
        [ dy, -dx]
    ])
    rotation_matrix = np.array([
        [np.cos(orientation_rad), np.sin(orientation_rad)],
        [-np.sin(orientation_rad), np.cos(orientation_rad)]
    ])
    # Rotate the corners
    rotated_corners = corners.dot(rotation_matrix)
    
    # Translate the rotated corners to the center position
    translated_corners = rotated_corners + [x, y]
    
    # Create a polygon from the rotated and translated corners
    polygon = patches.Polygon(translated_corners, closed=True, color=color, alpha=0.5)
    
    # Add the polygon to the axis
    ax.add_patch(polygon)

def preview_scenario(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, anmation_holder, dataset_option, file_path):
    """
    Function to preview scenario (integrated version)

    Args:
        fictive_ego_list_sampled (list): dataset uploaded by user 
        fictive_target_dicts_sampled (dict): metric option
        reminder_holder (st.empty()): reminder holder for warning message 
        anmation_holder (st.empty()): animation holder for searched scenarios 
        dataset_option (str): 
    Output:
        ---
    """
    frame_rate = None
    if dataset_option == "AD4CHE":
        frame_rate = 30
    else:
        frame_rate = 25


    if dataset_option == "inD":
        match = re.search(r'\d+', file_path)
        if match:
            index = int(match.group(0))
            if 0 <= index <= 6:
                processor = aseag.AseagProcessor()
                pkl_file = 'aseag_04.pkl'
            elif 7 <= index <= 17:
                processor = bendplatz.BendplatzProcessor()
                pkl_file = 'bendplatz_01.pkl'
            elif 18 <= index <= 29:
                processor = frankenburg.FrankenbergProcessor()
                pkl_file = 'frankenburg_02.pkl'
            elif 30 <= index <= 32:
                processor = heckstrasse.HeckstrasseProcessor()
                pkl_file = 'heckstrasse_03.pkl'
            else:
                reminder_holder.warning("No valid index found, or out of range. No operation performed.")
                return

            road_lane_paths = processor.load_road_lane_paths_pickle(pkl_file)
        else:
            reminder_holder.warning("No valid index found, or out of range. No operation performed.")
            return 

    tracks_df = pd.read_csv(file_path)

    def animate(i):
        """
        Animation function
        """
        ax.clear()
        ax.grid(True)  # Turn off the background grids
        ax.set_aspect('equal')  # Set equal aspect ratio

        ## ego
        # ego dimension
        # plot the playground
        if dataset_option == "inD":
            processor.plot_road_lane_paths(ax, road_lane_paths)
        elif dataset_option == "highD":
            match = re.search(r'\d+', file_path)
            if match:
                index = int(match.group(0))
                if index in lane_markings_data:
                    upper_lane_markings, lower_lane_markings = lane_markings_data[index]
                    for y in upper_lane_markings:
                        ax.axhline(y=y, color='magenta', linestyle='--')
                    for y in lower_lane_markings:
                        ax.axhline(y=y, color='orange', linestyle='--')
                    ax.set_xlabel('X Position (m)')
                    ax.set_ylabel('Y Position (m)')
                    ax.set_title('Highway Lane Markings')
                    ax.set_xlim(0, 480)
                    ax.set_ylim(40, 0)
                    ax.grid(True)
                else:
                    reminder_holder.warning(f"No lane markings found for index {index}. No operation performed.")
                    return


        if dataset_option == "highD":
            ego_width = fictive_ego_common['width'][i]
            ego_height = fictive_ego_common['height'][i]
            # trajectory
            ax.plot(fictive_ego_common['x'][:i], fictive_ego_common['y'][:i], color = 'red', marker='.', label='fictive ego')
            ego_x = fictive_ego_common['x'][i]
            ego_y = fictive_ego_common['y'][i]
            ego_orientation = 0
            rect = plt.Rectangle((ego_x - ego_width / 2, ego_y - ego_height / 2), ego_width, ego_height, angle=ego_orientation, color='r', alpha=0.5)
            ax.add_patch(rect)
        elif dataset_option == "inD": 
            ego_width = fictive_ego_common['width'][i]
            ego_length = fictive_ego_common['length'][i]
            ax.plot(fictive_ego_common['xCenter'][:i], fictive_ego_common['yCenter'][:i], color = 'red', marker='.', label='fictive ego')
            ego_x = fictive_ego_common['xCenter'][i]
            ego_y = fictive_ego_common['yCenter'][i]
            ego_orientation = fictive_ego_common['heading'][i] 
            plot_vehicle(ax, ego_x, ego_y, ego_width, ego_length, ego_orientation, color='red') 
        # fit orientation to dataset
        elif dataset_option == "AD4CHE":
            ego_orientation = fictive_ego_common['orientation'][i]
            ego_dx = 0.5 * np.cos(np.radians(ego_orientation))  # Adjust arrow length
            ego_dy = 0.5 * np.sin(np.radians(ego_orientation))  # Adjust arrow length
            ax.arrow(ego_x, ego_y, ego_dx, ego_dy, head_width=0.2, head_length=0.2, fc='r', ec='r')
            target_orientation = 0
            rect = plt.Rectangle((ego_x - ego_width / 2, ego_y - ego_height / 2), ego_width, ego_height, angle=ego_orientation, color='r', alpha=0.5)
            ax.add_patch(rect)

        ## target
        for target_common in fictive_targets_common:
            # target dimension
            if dataset_option == "highD":
                target_width = target_common['width'][i]
                target_height = target_common['height'][i]
                target_x = target_common['x'][i]
                target_y = target_common['y'][i]
                target_orientation = 0
                rect = plt.Rectangle((target_x - target_width / 2, target_y - target_height / 2), target_width, target_height, angle=target_orientation, color='b', alpha=0.5)
                ax.add_patch(rect)
            elif dataset_option == "inD": 
                target_width = target_common['width'][i]
                target_length = target_common['length'][i]
                ax.plot(target_common['xCenter'][:i], target_common['yCenter'][:i], color = 'blue', marker='.', label='fictive target')
                target_x = target_common['xCenter'][i]
                target_y = target_common['yCenter'][i]
                target_orientation = target_common['heading'][i] 
                plot_vehicle(ax, target_x, target_y, target_width, target_length, target_orientation, color='red') 
            # fit orientation to dataset
            elif dataset_option == "AD4CHE":
                target_orientation = target_common['orientation'][i]
                target_dx = 0.5 * np.cos(np.radians(target_orientation))
                target_dy = 0.5 * np.sin(np.radians(target_orientation))
                ax.arrow(target_x, target_y, target_dx, target_dy, head_width=0.2, fc='r', ec='r')
                target_orientation = 0
                rect = plt.Rectangle((target_x - target_width / 2, target_y - target_height / 2), target_width, target_height, angle=target_orientation, color='b', alpha=0.5)
                ax.add_patch(rect)
            '''
            # Plot a rectangle to represent the vehicle dimensions
            rect = plt.Rectangle((target_x - target_width / 2, target_y - target_height / 2), target_width, target_height, angle=target_orientation, color='b', alpha=0.5)
            ax.add_patch(rect)
            '''

        # Set axis limits based on the trajectory data
        ax.set_xlim(x_min - 5, x_max + 5)
        ax.set_ylim(y_min - 5, y_max + 5)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        current_time = (fictive_ego_common['frame'][i]-fictive_ego_common['frame'][0])/frame_rate
        ax.set_title(f'Time: {current_time}s')
        ax.legend(loc='upper right', bbox_to_anchor=(1, 3))

    ## start preview process
    index = 1
    for fictive_ego in fictive_ego_list_sampled:
        #egoId = fictive_ego['id'][0]
        # print(f'Ego {egoId} start/end frame before alignment:')
        # print(fictive_ego['frame'][0])
        # print(fictive_ego['frame'].iloc[-1])
        # skip if ego is empty
        if fictive_ego.empty:
            continue
        reminder_holder.warning(f'Previewing {index}-th scenario.')
        if dataset_option == "highD":
            fictive_targets = fictive_target_dicts_sampled[fictive_ego['id'][0]]
        elif dataset_option == "inD":   
            fictive_targets = fictive_target_dicts_sampled[fictive_ego['trackId'][0]] 
        #for fictive_target in fictive_targets:
        #    tgtId = fictive_target['id'][0]
            # print(f'Target {tgtId} start/end frame before alignment:')
            # print(fictive_target['frame'][0])
            # print(fictive_target['frame'].iloc[-1])

        # Find intersection of frames with the current target vehicle
        common_frames = set(fictive_ego['frame'])
        tgtVehTraj_common = []
        for fictive_target in fictive_targets:
            common_frames = common_frames.intersection(set(fictive_target['frame']))
        
        if len(common_frames) == 0:
            continue

        # Now common_frames contains only frames that are common across all target vehicles and the ego vehicle
        fictive_ego_common = fictive_ego[fictive_ego['frame'].isin(common_frames)].copy().reset_index(drop=True)
        # print('Ego start/end frame after alignment:')
        # print(fictive_ego_common['frame'][0])
        # print(fictive_ego_common['frame'].iloc[-1])

        # Get common trajectory data for all target vehicles
        fictive_targets_common = []
        for fictive_target in fictive_targets:
            fictive_target_common = fictive_target[fictive_target['frame'].isin(common_frames)].copy().reset_index(drop=True)
            # print('Target start/end frame after alignment:')
            # print(fictive_target_common['frame'][0])
            # print(fictive_target_common['frame'].iloc[-1])
            fictive_targets_common.append(fictive_target_common)


        x_min, x_max, y_min, y_max = find_ax_limit(fictive_ego_common, fictive_targets_common,dataset_option)
        fig, ax = plt.subplots(figsize=(7,3))
        ani = animation.FuncAnimation(fig, animate, frames=len(fictive_ego_common), repeat=True, interval=1000)
        ani.save("animation.gif", writer='pillow', fps=25)
        anmation_holder.image("animation.gif")
        plt.close(fig)
        index += 1


def preview_scenario_new(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, anmation_holder, dataset_option):
    """
    Function to preview scenario (integrated version)

    Args:
        fictive_ego_list_sampled (list): dataset uploaded by user 
        fictive_target_dicts_sampled (dict): metric option
        reminder_holder (st.empty()): reminder holder for warning message 
        anmation_holder (st.empty()): animation holder for searched scenarios 
        dataset_option (str): 
    Output:
        ---
    """
    clear_csv('./data/08_tracks.csv')
    clear_csv('./data/08_tracksMeta.csv')
    first_write = True  # Flag to indicate the first write
    
    
    ## start preview process
    index = 1
    for fictive_ego in fictive_ego_list_sampled:
        combined_df = pd.DataFrame()  # Combined DataFrame to store all data
        fictive_ego_common = pd.DataFrame()  # Initialize fictive_ego_common as an empty DataFrame
    
        # skip if ego is empty
        if fictive_ego.empty:
            continue
        reminder_holder.warning(f'Previewing {index}-th scenario.')
        if dataset_option == "highD":
            fictive_targets = fictive_target_dicts_sampled[fictive_ego['id'][0]]
        elif dataset_option == "inD":   
            fictive_targets = fictive_target_dicts_sampled[fictive_ego['trackId'][0]] 
        common_frames = set(fictive_ego['frame'])
        tgtVehTraj_common = []
        for fictive_target in fictive_targets:
            common_frames = common_frames.intersection(set(fictive_target['frame']))
        
        if len(common_frames) == 0:
            continue

        fictive_ego_common = fictive_ego[fictive_ego['frame'].isin(common_frames)].copy().reset_index(drop=True)
        
        fictive_targets_common = []
        for fictive_target in fictive_targets:
            fictive_target_common = fictive_target[fictive_target['frame'].isin(common_frames)].copy().reset_index(drop=True)

            fictive_targets_common.append(fictive_target_common)
        
        # Save data to CSV
        #save_to_csv(fictive_ego_common, fictive_targets_common, './data/08_tracks.csv', first_write)
        combined_df = pd.concat([combined_df, save_to_csv(fictive_ego_common, fictive_targets_common, './data/08_tracks.csv', first_write)], ignore_index=True)
        save_to_tracksMeta_csv(combined_df,'./08_tracksMeta.csv')
        
        #meta_info = read_recording_meta('./data/08_tracksMeta.csv')
        #static_info = read_tracks_meta('./data/08_tracksMeta.csv')
        #tracks = read_tracks_new(combined_df, meta_info, True)
        main()
        clear_csv('./data/08_tracks.csv')
        clear_csv('./data/08_tracksMeta.csv')

'''
def read_tracks_new(combined_df: pd.DataFrame, recording_meta: dict, include_px_coordinates: bool=False) -> List[dict]:
    """
    Read tracks from a csv file
    :param tracks_file: Path of a tracks csv file
    :param recording_meta: Loaded meta of the corresponding recording
    :param include_px_coordinates: Set to true, if the tracks are used for the visualizer
    :return: A list of tracks represented as dictionary each
    """
    # To extract every track, group the rows by the track id
    n_max_overlapping_lanelets = 5

    def semi_colon_int_list_to_list(semi_colon_list):
        output_list = [np.nan] * n_max_overlapping_lanelets
        if semi_colon_list:
            if ";" in semi_colon_list:
                for i, v in enumerate(semi_colon_list.split(";")):
                    output_list[i] = int(v)
                # output_list = [int(v) for v in semi_colon_list.split(";")]
            else:
                output_list[0] = int(semi_colon_list)
        return output_list

    def semi_colon_float_list_to_list(semi_colon_list):
        output_list = [np.nan] * n_max_overlapping_lanelets
        if semi_colon_list:
            if ";" in semi_colon_list:
                for i, v in enumerate(semi_colon_list.split(";")):
                    output_list[i] = float(v)
                # output_list = [int(v) for v in semi_colon_list.split(";")]
            else:
                output_list[0] = float(semi_colon_list)
        return output_list
    
    raw_tracks = pandas.read_csv(tracks_file,
                                 converters={"leftAlongsideId": semi_colon_int_list_to_list,
                                             "rightAlongsideId": semi_colon_int_list_to_list,
                                             "laneletId": semi_colon_int_list_to_list,
                                             "latLaneCenterOffset": semi_colon_float_list_to_list,
                                             "lonLaneletPos": semi_colon_float_list_to_list,
                                             "laneletLength": semi_colon_float_list_to_list,
                                             "laneWidth": semi_colon_float_list_to_list}
                                 ).groupby(["trackId"], sort=True)

    
        # 定义转换函数
    def semi_colon_int_list_to_list(s):
        return [int(x) for x in s.split(';')]

    def semi_colon_float_list_to_list(s):
        return [float(x) for x in s.split(';')]


    raw_tracks = combined_df

    # 列出需要转换的列
    columns_to_convert_int = ["leftAlongsideId", "rightAlongsideId", "laneletId"]
    columns_to_convert_float = ["latLaneCenterOffset", "lonLaneletPos", "laneletLength", "laneWidth"]

    # 应用转换函数
    for column in columns_to_convert_int:
        if column in raw_tracks.columns:
            raw_tracks[column] = raw_tracks[column].apply(semi_colon_int_list_to_list)

    for column in columns_to_convert_float:
        if column in raw_tracks.columns:
            raw_tracks[column] = raw_tracks[column].apply(semi_colon_float_list_to_list)

    # 按 trackId 分组
    raw_tracks = raw_tracks.groupby(["trackId"], sort=True)

    ortho_px_to_meter = recording_meta["orthoPxToMeter"]

    # Convert groups of rows to tracks
    tracks = []
    for track_id, track_rows in raw_tracks:
        track = track_rows.to_dict(orient="list")

        # Convert lists to numpy arrays
        for key, value in track.items():
            if key in ["trackId", "recordingId"]:
                track[key] = value[0]
            elif key in ["leftAlongsideId", "rightAlongsideId"]:
                continue
            else:
                track[key] = np.array(value)

        track["center"] = np.stack([track["xCenter"], track["yCenter"]], axis=-1)
        if np.count_nonzero(track["length"]) and np.count_nonzero(track["width"]):
            # Only calculate bounding box of objects with a width and length (e.g. cars)
            track["bbox"] = get_rotated_bbox(track["xCenter"], track["yCenter"],
                                             track["length"], track["width"],
                                             np.deg2rad(track["heading"]))
        else:
            track["bbox"] = None

        if include_px_coordinates:
            # As the tracks are given in utm coordinates, transform these to pixel coordinates for visualization
            track["xCenterVis"] = track["xCenter"] / ortho_px_to_meter
            track["yCenterVis"] = -track["yCenter"] / ortho_px_to_meter
            track["centerVis"] = np.stack([track["xCenterVis"], track["yCenterVis"]], axis=-1)
            track["widthVis"] = track["width"] / ortho_px_to_meter
            track["lengthVis"] = track["length"] / ortho_px_to_meter
            track["headingVis"] = track["heading"] * -1
            track["headingVis"][track["headingVis"] < 0] += 360
            if np.count_nonzero(track["length"]) and np.count_nonzero(track["width"]):
                # Only calculate bounding box of objects with a width and length (e.g. cars)
                track["bboxVis"] = get_rotated_bbox(track["xCenterVis"], track["yCenterVis"],
                                                    track["lengthVis"], track["widthVis"],
                                                    np.deg2rad(track["headingVis"]))
            else:
                track["bboxVis"] = None

        tracks.append(track)
    return tracks
'''

def clear_csv(file_path):
    """
    Clear the content of the CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
    """
    with open(file_path, 'w') as file:
        pass

def save_to_csv(fictive_ego_common, fictive_targets_common, file_path, first_write=False):
    """
    Save ego and target data to CSV file.

    Args:
        fictive_ego_common (DataFrame): Aligned ego data.
        fictive_targets_common (list of DataFrame): Aligned target data.
        file_path (str): Path to the CSV file.
        first_write (bool): If True, write the header; otherwise, append without header.
    """
    columns_to_save = [
        'recordingId', 'trackId', 'frame', 'trackLifetime', 'xCenter', 'yCenter', 
        'heading', 'width', 'length', 'xVelocity', 'yVelocity', 'xAcceleration', 
        'yAcceleration', 'lonVelocity', 'latVelocity', 'lonAcceleration', 'latAcceleration'
    ]
    combined_df = pd.DataFrame(columns=columns_to_save)
    
    # Determine the write mode and whether to include header
    mode = 'w' if first_write else 'a'
    header = first_write
    
    # Write the ego data
    fictive_ego_common[columns_to_save].to_csv(file_path, index=False, mode=mode, header=header)
    combined_df = pd.concat([combined_df, fictive_ego_common[columns_to_save]], ignore_index=True)
   
    # Append the target data without header
    for target_common in fictive_targets_common:
        target_common[columns_to_save].to_csv(file_path, index=False, mode='a', header=False)
        combined_df = pd.concat([combined_df, target_common[columns_to_save]], ignore_index=True)

    return combined_df

def save_to_tracksMeta_csv(combined_df, reference_meta_path):
    """
    Save track meta information to CSV file.

    Args:
        combined_df (DataFrame): Combined DataFrame of all saved data.
        reference_meta_path (str): Path to the reference tracksMeta CSV file.
    """
    file_path_new = './data/08_tracksMeta.csv'
    
    # Read the reference tracksMeta CSV file to get class information
    if os.path.exists(reference_meta_path):
        reference_meta_df = pd.read_csv(reference_meta_path)
    else:
        raise FileNotFoundError(f"The reference meta file {reference_meta_path} does not exist.")
    
    # Initialize tracksMeta DataFrame
    columns_meta = ['recordingId', 'trackId', 'initialFrame', 'finalFrame', 'numFrames', 'width', 'length', 'class']
    tracksMeta_df = pd.DataFrame(columns=columns_meta)
    
    # Iterate over unique trackId in combined_df
    for track_id in combined_df['trackId'].unique():
        track_data = combined_df[combined_df['trackId'] == track_id]
        recording_id = track_data['recordingId'].iloc[0]
        initial_frame = track_data['frame'].min()
        final_frame = track_data['frame'].max()
        num_frames = final_frame - initial_frame + 1
        width = track_data['width'].iloc[0]
        length = track_data['length'].iloc[0]
        
        # Get class from reference_meta_df
        if 'class' in reference_meta_df.columns:
            obj_class = reference_meta_df[reference_meta_df['trackId'] == track_id]['class'].values[0]
        else:
            obj_class = 'unknown'
        
        track_meta = {
            'recordingId': recording_id,
            'trackId': track_id,
            'initialFrame': initial_frame,
            'finalFrame': final_frame,
            'numFrames': num_frames,
            'width': width,
            'length': length,
            'class': obj_class
        }
        
        #tracksMeta_df = tracksMeta_df.append(track_meta, ignore_index=True)
        if isinstance(track_meta, dict):
            track_meta = pd.DataFrame([track_meta])

        # 使用 concat 方法进行拼接
        tracksMeta_df = pd.concat([tracksMeta_df, track_meta], ignore_index=True)
    
    # Write tracksMeta_df to CSV file
    if not os.path.exists(file_path_new):
        tracksMeta_df.to_csv(file_path_new, index=False, mode='w')
    else:
        # Only write header if the file is being created for the first time
        write_header = not os.path.exists(file_path_new) or os.path.getsize(file_path_new) == 0
        tracksMeta_df.to_csv(file_path_new, index=False, mode='a', header=write_header)


def compare_strings_ignore_whitespace(str1, str2):
    """
    Compare two strings without considering whitespace

    Args:
        str1 (string): string to be compared
        str2 (string): string to be compared
    Output:
        True/False (bool):  
    """
    # Remove whitespace from both strings and then compare
    str1_cleaned = str1.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
    str2_cleaned = str2.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
    
    return str1_cleaned == str2_cleaned


def check_upload_csv(dataset_load, dataset_option):
    """
    Function to preview scenario (integrated version)

    Args:
        dataset_load (list): dataset uploaded by user 
        dataset_option (str): dataset option selected by user
    Output:
        True/False (bool): if dataset format is correct
    """

    # expected format of DJI
    DJI_format = ["frame", "id", "x", "y", "width", "height", "xVelocity", "yVelocity",\
                    "xAcceleration", "yAcceleration", "frontSightDistance",\
                        "backSightDistance", "dhw", "thw", "ttc", "precedingXVelocity",\
                            "precedingId", "followingId", "leftPrecedingId", "leftAlongsideId",\
                                "leftFollowingId", "rightPrecedingId", "rightAlongsideId", "rightFollowingId",\
                                    "laneId", "angle", "orientation", "yaw_rate", "ego_offset"]
    
    # expected format of Aachen
    Aachen_format = ["frame", "id", "x", "y", "width", "height", "xVelocity", "yVelocity",\
                    "xAcceleration", "yAcceleration", "frontSightDistance",\
                        "backSightDistance", "dhw", "thw", "ttc", "precedingXVelocity",\
                            "precedingId", "followingId", "leftPrecedingId", "leftAlongsideId",\
                                "leftFollowingId", "rightPrecedingId", "rightAlongsideId", "rightFollowingId",\
                                    "laneId"]
    # expected format of Ind Aachen 
    Aachen_Ind_format = ["recordingId", "trackId", "frame", "trackLifetime", "xCenter", "yCenter", "heading",\
                          "width", "length", "xVelocity", "yVelocity", "xAcceleration", "yAcceleration",\
                             "lonVelocity", "latVelocity", "lonAcceleration", "latAcceleration"]


    # try to read csv, warning if error 
    try:
        df = pd.read_csv(dataset_load)
        columns = df.columns
        column_names = columns.tolist()
    except FileNotFoundError:
        st.warning(f"File not found: {dataset_load}")
        exit()
    
    # assign correct format according to dataset option
    expected_format = []
    if dataset_option == "AD4CHE":
        expected_format = DJI_format
    if dataset_option == "highD" or dataset_option == "roundD" or dataset_option == "exitD" or dataset_option == "uniD":
        expected_format = Aachen_format
    elif dataset_option == "inD":
        expected_format = Aachen_Ind_format
    
    # compare current and expected format
    curr_format = column_names
    if len(curr_format) != len(expected_format):
        dataset_load.seek(0)
        return False
    else:
        for x, y in zip(expected_format, curr_format):
            res = compare_strings_ignore_whitespace(x, y)
            if not res:
                dataset_load.seek(0)
                return False
        
    # Reset the file pointer to the beginning of the file
    dataset_load.seek(0)
    return True