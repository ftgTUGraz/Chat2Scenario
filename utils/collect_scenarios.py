import json
import os
from collections import defaultdict

# Function to process each JSON file, optionally filtering specific scenario keys
def process_json_file(filepath, scenario_keys=None):
    with open(filepath, "r") as file:
        data = json.load(file)
    
    dataset_type = data.get("dataset_type")
    track_num = data.get("track_num")
    scenarios = data.get("scenario", {}).get("desired_scenarios", {})

    # If scenario_keys is provided, filter based on those keys
    if scenario_keys:
        filtered_keys = [key for key in scenarios if any(s_key in key for s_key in scenario_keys)]
    else:
        # If no scenario_keys provided, process all scenarios
        filtered_keys = scenarios.keys()

    # Extract the relevant scenarios
    unique_scenarios = set()
    for key in filtered_keys:
        for entry in scenarios[key]:
            if len(entry) > 1:
                ego_id = entry[0]
                target_id_list = entry[1]
                start_frame = entry[2]
                end_frame = entry[3]

                # Skip scenarios with less than 30 frames
                if end_frame - start_frame < 30:
                    continue

                # Store the tuple of ego_id and target_id
                for target_id in target_id_list:
                    unique_scenarios.add((ego_id, target_id, start_frame, end_frame))
    
    # Return dataset_type, track_num, and the filtered scenarios
    return dataset_type, track_num, unique_scenarios

def read_and_combine_json_files(output_folder, combined_output_file):
    """
    Reads all JSON files from the output folder and combines the dataset_type, track_num, and ego_ids
    into a single JSON file.

    Parameters:
        output_folder (str): Folder containing the output JSON files.
        combined_output_file (str): Path to save the combined JSON file.

    Returns:
        None
    """
    combined_data = []

    # Iterate over all JSON files in the output folder
    for filename in os.listdir(output_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(output_folder, filename)
            
            # Read the JSON file
            with open(file_path, "r") as infile:
                data = json.load(infile)
            
            # Extract the required information
            dataset_type = data.get("dataset_type")
            track_num = data.get("track_num")
            ego_ids = data.get("ego_ids", [])

            # Add the extracted information to the combined list
            combined_data.append({
                "dataset_type": dataset_type,
                "track_num": track_num,
                "ego_ids": ego_ids
            })

    # Write the combined data to the output JSON file
    with open(combined_output_file, "w") as outfile:
        json.dump(combined_data, outfile, indent=4)

    print(f"Combined ego_ids written to {combined_output_file}")

# Define the input folder path
input_folder = "/home/boron/myProjects/Chat2Scenario/output"
output_folder = "/home/boron/myProjects/Chat2Scenario/output/filtered_scenarios"  # Folder where separate files will be saved

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Dictionary to store combined results for each dataset and track
combined_results = defaultdict(lambda: {"scenarios": set(), "ego_ids": set()})

# Process all files in the folder, passing the optional scenario_keys parameter
scenario_keys = ["Time To Collision", "Time Headway", 'Longitudinal jerk (LongJ)', "Deceleration to safety time (DST)"]  # Pass this as a filter, or set to None to process all
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(input_folder, filename)
        dataset_type, track_num, unique_scenarios = process_json_file(file_path, scenario_keys)
        
        # Update the combined results for the same dataset_type and track_num
        combined_results[(dataset_type, track_num)]["scenarios"].update(unique_scenarios)
        combined_results[(dataset_type, track_num)]["ego_ids"].update(ego_id for ego_id, _, _, _ in unique_scenarios)

# Save each track's processed scenarios into a separate JSON file
for (dataset_type, track_num), data in combined_results.items():
    output_data = {
        "dataset_type": dataset_type,
        "track_num": track_num,
        "ego_ids": list(data["ego_ids"]),
        "scenarios": [{"ego_id": ego_id, "target_id": target_id} for ego_id, target_id, _, _ in data["scenarios"]],
    }
    
    # Define the output file name for each track
    file_suffix = "_filtered_scenarios" if scenario_keys else "_all_scenarios"
    output_file = os.path.join(output_folder, f"{dataset_type}_track_{track_num}{file_suffix}.json")
    
    # Save the processed data to the JSON file
    with open(output_file, "w") as outfile:
        json.dump(output_data, outfile, indent=4)

    print(f"Saved {dataset_type} track {track_num} data to {output_file}")


# Define the output folder and combined output file path
combined_output_file = "/home/boron/myProjects/Chat2Scenario/output/combined_ego_ids.json"
# Call the function to combine the output files
read_and_combine_json_files(output_folder, combined_output_file)
