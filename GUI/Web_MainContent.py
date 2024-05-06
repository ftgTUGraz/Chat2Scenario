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


def preview_scenario(fictive_ego_list_sampled, fictive_target_dicts_sampled, reminder_holder, anmation_holder, dataset_option):
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

    def animate(i):
        """
        Animation function
        """
        ax.clear()
        ax.grid(True)  # Turn off the background grids
        ax.set_aspect('equal')  # Set equal aspect ratio

        ## ego
        # ego dimension
        ego_width = fictive_ego_common['width'][i]
        ego_height = fictive_ego_common['height'][i]
        # trajectory
        ax.plot(fictive_ego_common['x'][:i], fictive_ego_common['y'][:i], color = 'red', marker='.', label='fictive ego')
        ego_x = fictive_ego_common['x'][i]
        ego_y = fictive_ego_common['y'][i]
        # fit orientation to dataset
        if dataset_option == "AD4CHE":
            ego_orientation = fictive_ego_common['orientation'][i]
            ego_dx = 0.5 * np.cos(np.radians(ego_orientation))  # Adjust arrow length
            ego_dy = 0.5 * np.sin(np.radians(ego_orientation))  # Adjust arrow length
            ax.arrow(ego_x, ego_y, ego_dx, ego_dy, head_width=0.2, head_length=0.2, fc='r', ec='r')
        else:
            ego_orientation = 0

        # Plot a rectangle to represent the vehicle dimensions
        rect = plt.Rectangle((ego_x - ego_width / 2, ego_y - ego_height / 2), ego_width, ego_height, angle=ego_orientation, color='r', alpha=0.5)
        ax.add_patch(rect)

        ## target
        for target_common in fictive_targets_common:
            # target dimension
            target_width = target_common['width'][i]
            target_height = target_common['height'][i]
            target_x = target_common['x'][i]
            target_y = target_common['y'][i]

            # fit orientation to dataset
            if dataset_option == "AD4CHE":
                target_orientation = target_common['orientation'][i]
                target_dx = 0.5 * np.cos(np.radians(target_orientation))
                target_dy = 0.5 * np.sin(np.radians(target_orientation))
                ax.arrow(target_x, target_y, target_dx, target_dy, head_width=0.2, fc='r', ec='r')
            else:
                target_orientation = 0

            # Plot a rectangle to represent the vehicle dimensions
            rect = plt.Rectangle((target_x - target_width / 2, target_y - target_height / 2), target_width, target_height, angle=target_orientation, color='b', alpha=0.5)
            ax.add_patch(rect)

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
        ani = animation.FuncAnimation(fig, animate, frames=len(fictive_ego_common), repeat=True)
        ani.save("animation.gif", writer='pillow', fps=5)
        anmation_holder.image("animation.gif")
        plt.close(fig)
        index += 1


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