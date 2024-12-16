"""
Author: Wenbo XIAO
Date Created: 2024-10-13
Copy Right: TU Graz FTG ADAS Group
"""
import os
import json
import pandas as pd
import zipfile
from io import BytesIO

# Import custom modules
from utils.helper_original_scenario import *
from NLP.Scenario_Description_Understand import *
from scenario_mining.activity_identification import *
from scenario_mining.scenario_identification import *
from utils.prompt_engineering import *
from utils.helper_data_functions import calc_heading

import threading

# Initialize a lock for controlling access to cached activity data
activity_cache_lock = threading.Lock()

NOW_TRACK_NUM = '01'
NOW_LAT_ACT_DICT = {}
NOW_LONG_ACT_DICT = {}
NOW_INTERACT_ID_DICT = {}

def load_and_analyze_activity_data(config):
    """
    Load the dataset, analyze vehicle activity, and cache results if necessary.
    
    Parameters:
        config (dict): Configuration dictionary containing dataset path and related info.
        
    Returns:
        tuple: Contains the track number, longitudinal activity dictionary, lateral activity dictionary, interaction ID dictionary.
    """
    global NOW_TRACK_NUM, NOW_LAT_ACT_DICT, NOW_LONG_ACT_DICT, NOW_INTERACT_ID_DICT
    
    # Extract the track number from dataset_path
    dataset_path = config['dataset_path']
    track_num = os.path.basename(dataset_path).split("_")[0]

    # Load the dataset
    try:
        tracks_original = pd.read_csv(dataset_path)
        print(f"Loaded dataset with {len(tracks_original)} records.")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return None

    # Use a lock to synchronize access to the cache
    with activity_cache_lock:
        # Check if the activity data for this track is already cached
        if track_num == NOW_TRACK_NUM and NOW_LAT_ACT_DICT:
            print(f"Using cached activity data for track number {track_num}.")
            return track_num, NOW_LONG_ACT_DICT, NOW_LAT_ACT_DICT, NOW_INTERACT_ID_DICT
        else:
            try:
                # Analyze vehicle activity and update the cache
                longActDict, latActDict, interactIdDict = main_fcn_veh_activity(tracks_original)
                NOW_LAT_ACT_DICT = latActDict
                NOW_LONG_ACT_DICT = longActDict
                NOW_INTERACT_ID_DICT = interactIdDict
                NOW_TRACK_NUM = track_num
                print(f"Processed and cached activity data for track number {track_num}.")
                return track_num, longActDict, latActDict, interactIdDict
            except Exception as e:
                print(f"Error during vehicle activity analysis: {e}")
                return None


def identify_scenarios(tracks_original, key_label, longActDict, latActDict, interactIdDict):
    """
    Identify scenarios based on the classification and activity analysis.
    
    Parameters:
        tracks_original (pd.DataFrame): The dataset of vehicle tracks.
        key_label (str): Scenario classification result from LLM.
        longActDict, latActDict, interactIdDict: Activity dictionaries for longitudinal, lateral, and interaction data.
    
    Returns:
        list: Identified scenarios.
    """
    try:
        scenarioList = mainFunctionScenarioIdentification(
            tracks_original,
            key_label,
            latActDict,
            longActDict,
            interactIdDict
        )
        print(f"Identified {len(scenarioList)} scenarios in the scenario pool.")
        return scenarioList
    except Exception as e:
        print(f"Error during scenario identification: {e}")
        return None

def process_metric_options(tracks_original, config, scenarioList, metric_options, frame_rate):
    """
    Process each metric option and filter scenarios that match the thresholds.
    
    Parameters:
        config (dict): Configuration dictionary with CA input, target value, and scenario description.
        scenarioList (list): List of identified scenarios.
        metric_options (dict): Dictionary of metric options and suboptions.
        frame_rate (int): Frame rate of the dataset.
    
    Returns:
        dict: Dictionary of desired scenarios for each metric option.
    """
    desired_scenarios_dict = {}
    CA_Input = config['CA_Input']
    target_value = config['target_value']
    
    for metric_option, suboptions in metric_options.items():
        for metric_suboption, metric_threshold_text in suboptions.items():
            print(f"\nProcessing Metric Option: {metric_option}, Suboption: {metric_suboption}, Threshold: {metric_threshold_text}")

            # Parse metric_threshold
            if metric_threshold_text:
                try:
                    min_value, max_value = map(float, metric_threshold_text.split(' - '))
                    metric_threshold = (min_value, max_value)
                except ValueError:
                    print(f"Invalid metric threshold format for {metric_option} - {metric_suboption}. Skipping.")
                    continue
            else:
                print(f"No metric threshold provided for {metric_option} - {metric_suboption}. Skipping.")
                continue

            # Calculate metric values and filter desired scenarios
            desired_scenarios = []
            for idx, scenario_i in enumerate(scenarioList, start=1):
                egoId, targetIds, initialFrame, finalFrame = scenario_i
                try:
                    egoVehData, tgtVehsData = find_vehicle_data_within_start_end_frame(
                        tracks_original,
                        egoId,
                        targetIds,
                        initialFrame,
                        finalFrame
                    )
                    metric_value_res = calc_metric_value_for_desired_scenario_segment(
                        egoVehData,
                        tgtVehsData,
                        metric_option,
                        metric_suboption,
                        CA_Input,
                        tracks_original,
                        frame_rate,
                        target_value
                    )
                    if if_scenario_within_threshold(metric_value_res, metric_threshold):
                        if scenario_i not in desired_scenarios:
                            desired_scenarios.append(scenario_i)
                except Exception as e:
                    print(f"Error processing scenario {idx}: {e}")

            print(f"Total desired scenarios for {metric_option} - {metric_suboption}: {len(desired_scenarios)}")
            key = f"{metric_suboption}_{metric_threshold_text}"
            desired_scenarios_dict[key] = desired_scenarios
    
    return desired_scenarios_dict

def save_scenario_list_to_file(config, desired_scenarios_dict, key_label, output_dir, track_num):
    """
    Save the desired scenarios to a JSON file.

    Parameters:
        config (dict): The configuration used for the process.
        desired_scenarios_dict (dict): The filtered scenarios dictionary.
        key_label (str): Scenario classification result.
        output_dir (str): The directory where the output JSON file will be saved.
        track_num (str): The track number for the dataset.
    
    Returns:
        None
    """
    try:
        desired_scenarios_native = convert_to_native(desired_scenarios_dict)
        output_dict = {
            'dataset_type': config['dataset_option'],
            'track_num': track_num,
            'scenario': {
                'scenario_description': key_label,
                'desired_scenarios': desired_scenarios_native,
            }
        }
        output_path_json = os.path.join(output_dir, f"{config['dataset_option']}_{track_num}_scenario_list.json")
        json_index = 0
        base_output_path = os.path.splitext(output_path_json)[0]
        while os.path.exists(output_path_json):
            output_path_json = f"{base_output_path}_{json_index}.json"
            json_index += 1
        with open(output_path_json, 'w') as f:
            json.dump(output_dict, f, indent=4)
        print(f"Desired scenarios saved to {output_path_json}")
    except Exception as e:
        print(f"Error saving scenario list to JSON: {e}")

def process_and_save_scenarios(desired_scenarios, oriTracksDf, selected_ver, output_dir="output", file_name_prefix="scenario"):
    """
    Processes the desired scenarios, generates XOSC files, and saves them as a ZIP file.

    Parameters:
        desired_scenarios (list): List of desired scenarios to process.
        oriTracksDf (pd.DataFrame): Original dataset containing vehicle trajectories.
        selected_ver (str): The version of OpenSCENARIO to use for XOSC file generation.
        output_dir (str): Directory where the ZIP file will be saved.
        file_name_prefix (str): Prefix for the generated files inside the ZIP.

    Returns:
        str: The path to the created ZIP file.
    """

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xosc_files = []
    
    # Initialize index for progress tracking and XOSC file naming
    xosc_index = 1
    scenario_list = []
    for scenario in desired_scenarios.items():
        scenario_list.extend(scenario[1])

    if len(scenario_list) == 0:
        print("No scenarios to process. Skipping scenario generation.")
        return None
    
    for desired_scenario in scenario_list:

        # Get the ego vehicle information
        egoVehID = desired_scenario[0]
        egoVehTraj = oriTracksDf[oriTracksDf['id'] == egoVehID].reset_index(drop=True)

        # Find intersection of frames with the current target vehicle
        common_frames = set(egoVehTraj['frame'])
        tgtVehIDs = desired_scenario[1]
        tgtVehTrajs_common = []
        for tgtVehID in tgtVehIDs:
            tgtVehTraj = oriTracksDf[oriTracksDf['id'] == tgtVehID].reset_index(drop=True)
            common_frames = common_frames.intersection(set(tgtVehTraj['frame']))

        # Now common_frames contains only frames that are common across all target vehicles and the ego vehicle
        egoVehTraj_common = egoVehTraj[egoVehTraj['frame'].isin(common_frames)].copy().reset_index(drop=True)

        # **Check if `egoVehTraj_common` is empty**
        if egoVehTraj_common.empty:
            print(f"Warning: No common frames found for ego vehicle {egoVehID} and targets {tgtVehIDs}. Skipping scenario.")
            continue

        # Ego vehicle trajectory post-processing: 1) add time; 2) move position; 3) flip y 
        ego_time = (egoVehTraj_common['frame'] - egoVehTraj_common['frame'].iloc[0]) / 25
        egoVehTraj_common['time'] = ego_time
        egoVehTraj_common['x'] = egoVehTraj_common['x'] + 0.5 * egoVehTraj_common['width']
        egoVehTraj_common['y'] = egoVehTraj_common['y'] + 0.5 * egoVehTraj_common['height']
        egoVehTraj_common['y'] = -egoVehTraj_common['y']

        # Get common trajectory data for all target vehicles
        for tgtVehID in tgtVehIDs:
            tgtVehTraj = oriTracksDf[oriTracksDf['id'] == tgtVehID].reset_index(drop=True)
            tgtVehTraj_common = tgtVehTraj[tgtVehTraj['frame'].isin(common_frames)].copy().reset_index(drop=True)

            # **Check if `tgtVehTraj_common` is empty**
            if tgtVehTraj_common.empty:
                print(f"Warning: No common frames found for target vehicle {tgtVehID}. Skipping this target.")
                continue

            # Target vehicle trajectory post-processing: 1) add "time"; 2) move position; 3) flip y value  
            tgt_time = (tgtVehTraj_common['frame'] - tgtVehTraj_common['frame'].iloc[0]) / 25
            tgtVehTraj_common['time'] = tgt_time
            tgtVehTraj_common['x'] = tgtVehTraj_common['x'] + 0.5 * tgtVehTraj_common['width']
            tgtVehTraj_common['y'] = tgtVehTraj_common['y'] + 0.5 * tgtVehTraj_common['height']
            tgtVehTraj_common['y'] = -tgtVehTraj_common['y']
            tgtVehTrajs_common.append(tgtVehTraj_common)

        # Create input for "xosc_generation"
        sim_time = len(egoVehTraj_common) / 25
        ego_track = egoVehTraj_common
        tgt_tracks = tgtVehTrajs_common

        # Calculate ego vehicle heading
        heading = calc_heading(oriTracksDf, ego_track)

        # XOSC generation based on selected OpenSCENARIO version
        version_mapping = {'ASAM OpenSCENARIO V1.2.0': 2, 'ASAM OpenSCENARIO V1.1.0': 1, 'ASAM OpenSCENARIO V1.0.0': 0}
        pretty_xml_string = xosc_generation(sim_time, ego_track, tgt_tracks, version_mapping[selected_ver], heading)
        xosc_files.append(pretty_xml_string)

        xosc_index += 1

    # Create the ZIP file with the generated XOSC files
    if len(xosc_files) == 0:
        return None
    zip_path = save_scenarios_to_zip(xosc_files, output_dir, "track_number")  # Replace "track_number" with the actual value
    print(f"Scenarios successfully saved in ZIP file: {zip_path}")
    return zip_path

def save_scenarios_to_zip(xosc_files, output_dir, track_num, file_name_prefix="scenario"):
    """
    Save a list of scenarios into a ZIP file and write the ZIP file to the output directory.
    If the ZIP file already exists, append a unique suffix to avoid name conflicts.
    
    Parameters:
        xosc_files (list): A list of generated `.xosc` file contents.
        output_dir (str): The directory where the output ZIP file will be saved.
        track_num (str): The track number for the dataset.
        file_name_prefix (str): The prefix for the filenames in the ZIP file.
    
    Returns:
        zip_path (str): The path to the created ZIP file.
    """
    # Initial ZIP file name
    zip_file_name = f"{file_name_prefix}_{track_num}_scenarios.zip"
    zip_path = os.path.join(output_dir, zip_file_name)
    
    # Handle name conflicts: If the file already exists, append a unique number
    file_counter = 1
    while os.path.exists(zip_path):
        zip_file_name = f"{file_name_prefix}_{track_num}_scenarios_{file_counter}.zip"
        zip_path = os.path.join(output_dir, zip_file_name)
        file_counter += 1

    # Create a ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for index, curr_xosc in enumerate(xosc_files):
            xosc_filename = f"{file_name_prefix}_{index}.xosc"
            zf.writestr(xosc_filename, curr_xosc)
    
    print(f"Scenarios saved to {zip_path}")
    return zip_path

def process_scenario(config, metric_options, save_list = True, save_zip = False):
    """
    Main function to process a scenario based on the provided configuration and metric options.
    
    Parameters:
        config (dict): Configuration dictionary containing dataset path and other parameters.
        metric_options (dict): Dictionary containing metric options, suboptions, and thresholds.
        save_list (bool): Whether to save the desired scenarios to a JSON file.
        save_zip (bool): Whether to save the desired scenarios to a ZIP file.
    
    Returns:
        None
    """

    # Scenario description using LLM
    print("Understanding scenario description using OpenAI LLM...")
    key_label = get_scenario_classification_via_LLM(
        openai_key = config['openai_key'],
        scenario_description = config['scenario_description'],
        model = config['model'],
        base_url = config['base_url']
    )
    if not key_label:
        print("Failed to understand scenario description using LLM.")
        return
    else:
        print(f"Scenario description: {key_label}")

    # Load and analyze activity data
    track_num, longActDict, latActDict, interactIdDict = load_and_analyze_activity_data(config)
    if not track_num:
        return

    # Load dataset
    tracks_original = pd.read_csv(config['dataset_path'])

    # Identify scenarios
    scenarioList = identify_scenarios(tracks_original, key_label, longActDict, latActDict, interactIdDict)
    if not scenarioList:
        return

    # Process metric options
    frame_rate = 30 if config['dataset_option'] == "AD4CHE" else 25
    desired_scenarios_dict = process_metric_options(tracks_original, config, scenarioList, metric_options, frame_rate)

    output_dir = config.get('output_dir', 'output')

    # Save scenarios to file
    if save_list:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_scenario_list_to_file(config, desired_scenarios_dict, key_label, output_dir, track_num)
    
    # Generate the `.xosc` scenario files (for the sake of this example, we assume `xosc_generation` generates an XML string)
    if save_zip:
        selected_ver = config.get('asam_verion', 'ASAM OpenSCENARIO V1.2.0')
        zip_path = process_and_save_scenarios(desired_scenarios_dict, tracks_original, selected_ver, output_dir, "scenario")
        print(f"Scenarios saved to {zip_path}")
    
    print("Done.")