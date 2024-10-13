"""
Author: Wenbo XIAO
Date Created: 2024-10-13
Copy Right: TU Graz FTG ADAS Group
"""

import argparse
import os
import sys
import json
import pandas as pd
import zipfile
from io import BytesIO

# Import custom modules
# Ensure these modules are in your PYTHONPATH or the same directory as this script
from utils.helper_original_scenario import generate_xosc, convert_to_native
from scenario_mining.activity_identification import main_fcn_veh_activity
from scenario_mining.scenario_identification import (
    mainFunctionScenarioIdentification,
    find_vehicle_data_within_start_end_frame,
    calc_metric_value_for_desired_scenario_segment,
    if_scenario_within_threshold,
    xosc_generation
)
from utils.prompt_engineering import get_scenario_classification_via_LLM, validate_scenario
from NLP.Scenario_Description_Understand import *  # Ensure this module is necessary
# from GUI.Web_Sidebar import *  # Not needed in the script
# from GUI.Web_MainContent import *  # Not needed in the script

# Define a function to check the dataset format
def check_upload_csv(dataset_path, dataset_option):
    """
    Placeholder function to check if the uploaded CSV has the correct format.
    Implement the actual format checking based on dataset_option.
    """
    try:
        df = pd.read_csv(dataset_path)
        # Implement specific checks based on dataset_option
        if dataset_option == "highD":
            # Example: Check for required columns in highD
            required_columns = {'id', 'frame', 'x', 'y', 'width', 'height'}
            if not required_columns.issubset(df.columns):
                return False
        elif dataset_option == "AD4CHE":
            # Example: Check for required columns in AD4CHE
            required_columns = {'id', 'frame', 'x', 'y', 'width', 'height'}
            if not required_columns.issubset(df.columns):
                return False
        else:
            return False
        return True
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Chat2Scenario Processing Script')

    # Define required and optional arguments
    parser.add_argument('--dataset_option', type=str, choices=['highD', 'AD4CHE'], required=True,
                        help='Dataset option (e.g., highD, AD4CHE)')
    parser.add_argument('--dataset_path', type=str, required=True,
                        help='Path to the dataset CSV file')
    parser.add_argument('--metric_option', type=str, required=True,
                        help='Metric option')
    parser.add_argument('--metric_suboption', type=str, required=True,
                        help='Metric suboption')
    parser.add_argument('--metric_threshold', type=float, required=True,
                        help='Metric threshold value')
    parser.add_argument('--CA_Input', type=str, required=True,
                        help='CA Input parameter')
    parser.add_argument('--target_value', type=float, required=True,
                        help='Target value for the metric')
    parser.add_argument('--openai_key', type=str, required=True,
                        help='OpenAI API key')
    parser.add_argument('--asam_version', type=str, choices=['ASAM OpenSCENARIO V1.2.0',
                                                             'ASAM OpenSCENARIO V1.1.0',
                                                             'ASAM OpenSCENARIO V1.0.0'],
                        required=True, help='Desired ASAM OpenSCENARIO version')
    parser.add_argument('--scenario_description', type=str, required=True,
                        help='Natural language description of the desired scenario')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='Directory to save output files')

    args = parser.parse_args()

    # Extract arguments
    dataset_option = args.dataset_option
    dataset_path = args.dataset_path
    metric_option = args.metric_option
    metric_suboption = args.metric_suboption
    metric_threshold = args.metric_threshold
    CA_Input = args.CA_Input
    target_value = args.target_value
    openai_key = args.openai_key
    asam_version = args.asam_version
    scenario_description = args.scenario_description
    output_dir = args.output_dir

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory at {output_dir}")

    # Determine frame rate based on dataset_option
    frame_rate = 30 if dataset_option == "AD4CHE" else 25
    print(f"Using frame rate: {frame_rate} fps based on dataset option: {dataset_option}")

    # Check dataset format
    print("Checking dataset format...")
    if not check_upload_csv(dataset_path, dataset_option):
        print("Uploaded dataset format is NOT correct! Please check the selected dataset option or the uploaded CSV file.")
        sys.exit(1)
    else:
        print("Dataset format is correct.")

    # Load the dataset
    print("Loading dataset...")
    try:
        tracks_original = pd.read_csv(dataset_path)
        print(f"Loaded dataset with {len(tracks_original)} records.")
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        sys.exit(1)

    # Scenario Extraction
    print("Starting scenario extraction...")

    # Scenario Description using LLM
    print("Understanding scenario description using OpenAI LLM...")
    key_label = get_scenario_classification_via_LLM(openai_key, scenario_description)
    if key_label is None:
        print("Error: Failed to understand scenario description using LLM.")
        print("Please verify your OpenAI API key and the scenario description.")
        sys.exit(1)
    else:
        print(f"Scenario classification result: {key_label}")

    # Validate the scenario classification
    print("Validating scenario classification...")
    if not validate_scenario(key_label):
        print("Invalid scenario classification received. Exiting.")
        sys.exit(1)
    else:
        print("Scenario classification validated successfully.")

    # Analyze vehicle activity
    print("Analyzing vehicle activities...")
    try:
        longActDict, latActDict, interactIdDict = main_fcn_veh_activity(tracks_original)
        print("Vehicle activity analysis completed.")
    except Exception as e:
        print(f"Error during vehicle activity analysis: {e}")
        sys.exit(1)

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
        sys.exit(1)

    # Calculate metric values and filter desired scenarios
    print("Calculating metric values for each scenario...")
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
                desired_scenarios.append(scenario_i)
            print(f"Processed scenario {idx}/{len(scenarioList)}: {'Selected' if scenario_i in desired_scenarios else 'Rejected'}")
        except Exception as e:
            print(f"Error processing scenario {idx}: {e}")

    print(f"Total desired scenarios after metric filtering: {len(desired_scenarios)}")

    # Save the scenario list to a JSON file
    print("Saving desired scenarios to JSON file...")
    try:
        track_num = os.path.basename(dataset_path).split("_")[0]
        desired_scenarios_native = convert_to_native(desired_scenarios)
        output_dict = {
            'track_num': track_num,
            'scenario': {
                'scenario_description': key_label,
                'scenario_list': desired_scenarios_native,
                'metric_option': metric_option,
                'metric_suboption': metric_suboption,
                'metric_threshold': metric_threshold
            }
        }
        output_path_json = os.path.join(output_dir, f"{dataset_option}_{track_num}_scenario_list.json")
        with open(output_path_json, 'w') as f:
            json.dump(output_dict, f, indent=4)
        print(f"Desired scenarios saved to {output_path_json}")
    except Exception as e:
        print(f"Error saving scenario list to JSON: {e}")
        sys.exit(1)

    # Generate OpenSCENARIO (.xosc) files
    print("Generating OpenSCENARIO (.xosc) files for desired scenarios...")
    xosc_files = []
    for idx, desired_scenario in enumerate(desired_scenarios, start=1):
        egoVehID, tgtVehIDs, initialFrame, finalFrame = desired_scenario
        try:
            egoVehTraj = tracks_original[tracks_original['id'] == egoVehID].reset_index(drop=True)
            # Find common frames across all target vehicles
            common_frames = set(egoVehTraj['frame'])
            for tgtVehID in tgtVehIDs:
                tgtVehTraj = tracks_original[tracks_original['id'] == tgtVehID].reset_index(drop=True)
                common_frames = common_frames.intersection(set(tgtVehTraj['frame']))
            # Filter trajectories based on common frames
            egoVehTraj_common = egoVehTraj[egoVehTraj['frame'].isin(common_frames)].copy().reset_index(drop=True)
            egoVehTraj_common['time'] = (egoVehTraj_common['frame'] - egoVehTraj_common['frame'].iloc[0]) / frame_rate
            egoVehTraj_common['x'] += 0.5 * egoVehTraj_common['width']
            egoVehTraj_common['y'] += 0.5 * egoVehTraj_common['height']
            egoVehTraj_common['y'] = -egoVehTraj_common['y']

            tgtVehTrajs_common = []
            for tgtVehID in tgtVehIDs:
                tgtVehTraj = tracks_original[tracks_original['id'] == tgtVehID]
                tgtVehTraj_common = tgtVehTraj[tgtVehTraj['frame'].isin(common_frames)].copy().reset_index(drop=True)
                tgtVehTraj_common['time'] = (tgtVehTraj_common['frame'] - tgtVehTraj_common['frame'].iloc[0]) / frame_rate
                tgtVehTraj_common['x'] += 0.5 * tgtVehTraj_common['width']
                tgtVehTraj_common['y'] += 0.5 * tgtVehTraj_common['height']
                tgtVehTraj_common['y'] = -tgtVehTraj_common['y']
                tgtVehTrajs_common.append(tgtVehTraj_common)

            sim_time = len(egoVehTraj_common) / frame_rate
            ego_track = egoVehTraj_common
            tgt_tracks = tgtVehTrajs_common

            version_mapping = {
                'ASAM OpenSCENARIO V1.2.0': 2,
                'ASAM OpenSCENARIO V1.1.0': 1,
                'ASAM OpenSCENARIO V1.0.0': 0
            }
            pretty_xml_string = xosc_generation(sim_time, ego_track, tgt_tracks, version_mapping[asam_version])
            xosc_files.append(pretty_xml_string)
            print(f"Generated xOSC for scenario {idx}/{len(desired_scenarios)}")
        except Exception as e:
            print(f"Error generating xOSC for scenario {idx}: {e}")

    # Compress all xOSC files into a ZIP archive
    print("Compressing all xOSC files into a ZIP archive...")
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for index, curr_xosc in enumerate(xosc_files, start=1):
                zf.writestr(f"scenario_{index}.xosc", curr_xosc)
        zip_buffer.seek(0)
        zip_path = os.path.join(output_dir, "scenarios.zip")
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.read())
        print(f"All scenarios have been compressed into {zip_path}")
    except Exception as e:
        print(f"Error creating ZIP archive: {e}")
        sys.exit(1)

    print("Scenario extraction and file generation completed successfully.")

if __name__ == '__main__':
    main()
