import sys
import os
import concurrent.futures
import json
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tutorials.tutorials_run_script import process_scenario

def load_config(config_path):
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

def load_scenario_descriptions(file_path):
    """
    Load scenario descriptions from text file.
    
    Parameters:
        file_path (str): Path to the scenario descriptions file
        
    Returns:
        list: List of scenario descriptions
    """
    try:
        with open(file_path, 'r') as f:
            descriptions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"Successfully loaded {len(descriptions)} scenario descriptions")
        return descriptions
    except Exception as e:
        print(f"Error loading scenario descriptions: {e}")
        return None

def threaded_process(config, metric_options):
    """
    Function to process a scenario configuration in a separate thread.
    """
    process_scenario(config, metric_options, save_list=True, save_zip=False)

def main(args):
    """
    Main function to execute multiple scenario processing using multithreading.
    """
    # Load configuration
    config = load_config(args.config)
    if not config:
        return

    # Override configuration with command line arguments if provided
    if args.openai_key:
        config['openai_key'] = args.openai_key
    if args.model:
        config['model'] = args.model
    if args.base_url:
        config['base_url'] = args.base_url
    if args.output_dir:
        config['output_dir'] = args.output_dir
    if args.track_nums:
        config['track_nums'] = args.track_nums
    if args.max_workers:
        config['max_workers'] = args.max_workers

    # Load scenario descriptions
    scenario_descriptions = load_scenario_descriptions(args.scenarios)
    if not scenario_descriptions:
        return

    # Get configuration values
    track_nums = [f'{i:02}' for i in config.get('track_nums', range(18, 22))]
    max_workers = config.get('max_workers', 12)
    metric_options = config.get('metric_options', {})
    dataset_path_template = config.get('dataset_path_template')

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
                future.result()
            except Exception as exc:
                print(f"Scenario processing generated an exception: {exc}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat2Scenario Script')
    
    # Required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument('--config', type=str, required=True,
                      help='Path to configuration file')
    required.add_argument('--scenarios', type=str, required=True,
                      help='Path to scenario descriptions file')
    
    # Optional arguments
    parser.add_argument('--track-nums', type=int, nargs='+',
                      help='Track numbers to process (overrides config file)')
    parser.add_argument('--openai-key', type=str,
                      help='OpenAI API key (overrides config file)')
    parser.add_argument('--model', type=str,
                      help='OpenAI model to use (overrides config file)')
    parser.add_argument('--base-url', type=str,
                      help='OpenAI API base URL (overrides config file)')
    parser.add_argument('--output-dir', type=str,
                      help='Output directory (overrides config file)')
    parser.add_argument('--max-workers', type=int,
                      help='Maximum number of worker threads (overrides config file)')
    
    args = parser.parse_args()
    main(args)

   