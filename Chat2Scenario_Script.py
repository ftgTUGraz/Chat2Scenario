import sys
import os
import concurrent.futures
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tutorials.tutorials_run_script import process_scenario

def load_config(config_path='config/config.json'):
    """
    Load configuration from JSON file.
    
    Parameters:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Successfully loaded configuration from {config_path}")
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def load_scenario_descriptions(file_path='config/config_scenario_descriptions.txt'):
    """
    Load scenario descriptions from text file.
    
    Parameters:
        file_path (str): Path to the scenario descriptions file
        
    Returns:
        list: List of scenario descriptions
    """
    try:
        with open(file_path, 'r') as f:
            # Filter out empty lines and comments
            descriptions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"Successfully loaded {len(descriptions)} scenario descriptions")
        return descriptions
    except Exception as e:
        print(f"Error loading scenario descriptions: {e}")
        return None

def threaded_process(config, metric_options):
    """
    Function to process a scenario configuration in a separate thread.
    
    Parameters:
        config (dict): Configuration dictionary for the scenario.
        metric_options (dict): Metric options to apply.
    
    Returns:
        None
    """
    process_scenario(config, metric_options, save_list=True, save_zip=False)

def main():
    """
    Main function to execute multiple scenario processing using multithreading.
    """
    # Load configuration
    config = load_config()
    if not config:
        return

    # Load scenario descriptions
    scenario_descriptions = load_scenario_descriptions()
    if not scenario_descriptions:
        return

    # Get configuration values
    track_nums = [f'{i:02}' for i in config.get('track_nums', range(18, 22))]
    max_workers = config.get('max_workers', 12)
    metric_options = config.get('metric_options', {})
    dataset_path_template = config.get('dataset_path_template', '/C:/PhD/Dataset/highD/data/{track_num}_tracks.csv')

    # Use ThreadPoolExecutor for multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        # Iterate over each track number and scenario description
        for track_num in track_nums:
            for scenario_description in scenario_descriptions:
                # Create a new config for each scenario
                scenario_config = config.copy()
                scenario_config['dataset_path'] = dataset_path_template.format(track_num=track_num)
                scenario_config['scenario_description'] = scenario_description
                
                # Submit the scenario processing task to the thread pool
                futures.append(executor.submit(threaded_process, scenario_config, metric_options))
        
        # Wait for all futures to complete and handle exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise any exception from the thread
            except Exception as exc:
                print(f"Scenario processing generated an exception: {exc}")

if __name__ == '__main__':
    main()

   