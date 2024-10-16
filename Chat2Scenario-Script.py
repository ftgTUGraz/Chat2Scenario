"""
Author: Wenbo XIAO
Date Created: 2024-10-13
Copy Right: TU Graz FTG ADAS Group
"""
import os
import json
import pandas as pd

# Import custom modules
from utils.helper_original_scenario import *
from NLP.Scenario_Description_Understand import *
from scenario_mining.activity_identification import *
from scenario_mining.scenario_identification import *
from utils.prompt_engineering import *
from utils.helper_data_functions import calc_heading

NOW_TRACK_NUM = '01'
NOW_LAT_ACT_DICT = {}
NOW_LONG_ACT_DICT = {}
NOW_INTERACT_ID_DICT = {}

def process_scenario(config, metric_options):
    """
    Process a single scenario based on the provided configuration and metric options.

    Parameters:
        config (dict): Configuration dictionary containing all necessary parameters.
        metric_options (dict): Dictionary containing metric options, suboptions, and thresholds.

    Returns:
        None
    """
    global NOW_TRACK_NUM, NOW_LAT_ACT_DICT, NOW_LONG_ACT_DICT, NOW_INTERACT_ID_DICT

    # Extract configuration parameters
    dataset_option = config['dataset_option']
    dataset_path = config['dataset_path']
    CA_Input = config['CA_Input']
    target_value = config['target_value']
    openai_key = config['openai_key']
    asam_version = config['asam_version']
    scenario_description = config['scenario_description']
    output_dir = config.get('output_dir', 'output')  # Default to 'output' if not specified

    # Extract track number from dataset_path
    track_num = os.path.basename(dataset_path).split("_")[0]

    # Initialize a dictionary to hold desired scenarios for each metric option
    desired_scenarios_dict = {}

    print(f"\nProcessing configuration: {config.get('name', 'Unnamed Configuration')}")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory at {output_dir}")

    # Determine frame rate based on dataset_option
    frame_rate = 30 if dataset_option == "AD4CHE" else 25
    print(f"Using frame rate: {frame_rate} fps based on dataset option: {dataset_option}")

    # Load the dataset
    print("Loading dataset...")
    try:
        tracks_original = pd.read_csv(dataset_path)
        print(f"Loaded dataset with {len(tracks_original)} records.")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    # Scenario Extraction
    print("Starting scenario extraction...")

    # Scenario Description using LLM
    print("Understanding scenario description using OpenAI LLM...")
    key_label = get_scenario_classification_via_LLM(openai_key, scenario_description)
    if key_label is None:
        print("Error: Failed to understand scenario description using LLM.")
        print("Please verify your OpenAI API key and the scenario description.")
        return
    else:
        print(f"Scenario classification result: {key_label}")

    # Validate the scenario classification
    print("Validating scenario classification...")
    if not validate_scenario(key_label):
        print("Invalid scenario classification received. Skipping this configuration.")
        return
    else:
        print("Scenario classification validated successfully.")

    # Analyze vehicle activity
    print("Analyzing vehicle activities...")
    try:
        if track_num == NOW_TRACK_NUM and len(NOW_LAT_ACT_DICT) > 0:
            latActDict = NOW_LAT_ACT_DICT
            longActDict = NOW_LONG_ACT_DICT
            interactIdDict = NOW_INTERACT_ID_DICT
            print(f"Using cached activity data for track number {track_num}.")
        else:
            longActDict, latActDict, interactIdDict = main_fcn_veh_activity(tracks_original)
            # Update global variables
            NOW_LAT_ACT_DICT = latActDict
            NOW_LONG_ACT_DICT = longActDict
            NOW_INTERACT_ID_DICT = interactIdDict
            NOW_TRACK_NUM = track_num
            print(f"Processed and cached activity data for track number {track_num}.")

    except Exception as e:
        print(f"Error during vehicle activity analysis: {e}")
        return

    # Identify scenarios based on classification and activity analysis
    print("Identifying relevant scenarios from the dataset...")
    try:
        scenarioList = mainFunctionScenarioIdentification(
            tracks_original,
            key_label,
            latActDict,
            longActDict,
            interactIdDict
        )
        print(f"Identified {len(scenarioList)} scenarios in the scenario pool.")
    except Exception as e:
        print(f"Error during scenario identification: {e}")
        return

    # Iterate through each metric option and suboption
    for metric_option, suboptions in metric_options.items():
        for metric_suboption, metric_threshold_text in suboptions.items():
            print(f"\nProcessing Metric Option: {metric_option}, Suboption: {metric_suboption}, Threshold: {metric_threshold_text}")

            # Parse metric_threshold
            if metric_threshold_text is not None:
                try:
                    min_value, max_value = map(float, metric_threshold_text.split(' - '))
                    metric_threshold = (min_value, max_value)
                except ValueError:
                    print(f"Invalid metric threshold format for {metric_option} - {metric_suboption}. Please use 'min - max'. Skipping.")
                    continue
            else:
                print(f"No metric threshold provided for {metric_option} - {metric_suboption}. Skipping.")
                continue

            # Calculate metric values and filter desired scenarios
            print("Calculating metric values for each scenario...")
            desired_scenarios = []
            for idx, scenario_i in enumerate(scenarioList, start=1):
                egoId, targetIds, initialFrame, finalFrame = scenario_i
                try:
                    print('Finding vehicle data')
                    egoVehData, tgtVehsData = find_vehicle_data_within_start_end_frame(
                        tracks_original,
                        egoId,
                        targetIds,
                        initialFrame,
                        finalFrame
                    )
                    print('Calculating metric value')
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
                    print('Metric value comparing...')
                    if if_scenario_within_threshold(metric_value_res, metric_threshold):
                        if scenario_i not in desired_scenarios:
                            desired_scenarios.append(scenario_i)
                    print(f"Processed scenario {idx}/{len(scenarioList)}: {'Selected' if scenario_i in desired_scenarios else 'Rejected'}")
                except Exception as e:
                    print(f"Error processing scenario {idx}: {e}")

            print(f"Total desired scenarios for {metric_option} - {metric_suboption}: {len(desired_scenarios)}")

            # Use 'metric_option_suboption_threshold' as the key
            key = f"{metric_suboption}_{metric_threshold_text}"
            desired_scenarios_dict[key] = desired_scenarios

    if not desired_scenarios_dict:
        print("No desired scenarios found for any metric options. Skipping file generation.")
        return
    else:
        print("\nAll desired scenarios collected for various metric options.")

    # Save the scenario list to a JSON file
    print("Saving desired scenarios to JSON file...")
    try:
        desired_scenarios_native = convert_to_native(desired_scenarios_dict)
        output_dict = {
            'dataset_type': dataset_option,
            'track_num': track_num,
            'scenario': {
                'scenario_description': key_label,
                'desired_scenarios': desired_scenarios_native,
            }
        }
        output_path_json = os.path.join(output_dir, f"{dataset_option}_{track_num}_scenario_list.json")
        # While this file already exists, add a number to the end of the file name until it doesn't exist
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
        return

def main():
    """
    Main function to execute multiple scenario processing based on predefined configurations.
    """
    # Define multiple configurations as a list of dictionaries
    config = {
            'name': 'Scenario 2',
            'dataset_option': 'highD',
            'dataset_path': '/home/boron/myProjects/crconverter/data/highD/data/01_tracks.csv',
            'metric_option': 'Time-Scale',
            'metric_suboption': 'Time To Collision (TTC)',
            'metric_threshold': '1 - 15',
            'CA_Input': None,
            'target_value': None,
            'openai_key': None,
            'scenario_description': 'Ego vehicle is kepping its lane, target vehile is changing lane fron left to ego lane, and in front of ego vehilce, in the meanwhile, target vehicle is decelerating',
            'output_dir': './output/'
        }

    track_nums = ['01',]
    scenario_descriptions = [
        'Ego vehicle is kepping its lane, target vehile is decelerating and in front of ego vehilce',
    ]    
    metric_options = {
        'Distance-Scale': 
        {'Distance Headway (DHW)': '1 - 50'},
        # 'Jerk-Scale': 
        # {'Longitudinal jerk (LongJ)': '1 - 15',
        #  'Lateral jerk (LatJ)': '1 - 15'},
        'Time-Scale': 
        {'Time To Collision (TTC)': '1 - 15',
         'Time Headway (THW)': '1 - 15'},
    }
    
    # Iterate over each configuration and process the scenario
    for track_num in track_nums:
        for scenario_description in scenario_descriptions:
            config['dataset_path'] = f'/home/boron/myProjects/crconverter/data/highD/data/{track_num}_tracks.csv'
            config['scenario_description'] = scenario_description
            process_scenario(config, metric_options)

if __name__ == '__main__':
    main()
