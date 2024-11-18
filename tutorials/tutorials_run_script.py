import sys
import os
import concurrent.futures

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Chat2Scenario_Script import process_scenario

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
    # Define multiple configurations as a list of dictionaries
    config_template = {
        'name': 'Scenario 0',
        'asam_version': 'ASAM OpenSCENARIO V1.2.0',
        'dataset_option': 'highD',
        'dataset_path': '',  # This will be updated dynamically for each track_num
        'metric_option': 'Time-Scale',
        'metric_suboption': 'Time To Collision (TTC)',
        'metric_threshold': '1 - 3',
        'CA_Input': None,
        'target_value': None,
        'openai_key': 'sk-mThvSyi9PidmgxJR6722978b1c0c43Bb8d2fE7Bb7672F363', # modify this to your OpenAI API key
        'model': 'gpt-4o-mini', # None to use default model
        'base_url': 'https://free.gpt.ge/v1/', # None to use default base URL
        # 'model': None,
        # 'base_url': None,
        'scenario_description': '',  # This will be updated dynamically
        'output_dir': './output/'
    }

    scenario_descriptions = [
        "1. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead changes lanes to the left adjacent lane.",
        "2. The ego vehicle is accelerating in the ego lane, and the target vehicle ahead changes lanes to the left adjacent lane.",
        "3. The ego vehicle is decelerating in the ego lane, and the target vehicle ahead changes lanes to the left adjacent lane.",
        "4. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead changes lanes to the left adjacent lane while accelerating.",
        "5. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead changes lanes to the left adjacent lane while decelerating.",
        "6. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead changes lanes to the right adjacent lane.",
        "7. The ego vehicle is accelerating in the ego lane, and the target vehicle ahead changes lanes to the right adjacent lane.",
        "8. The ego vehicle is decelerating in the ego lane, and the target vehicle ahead changes lanes to the right adjacent lane.",
        "9. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead changes lanes to the right adjacent lane while accelerating.",
        "10. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead changes lanes to the right adjacent lane while decelerating.",
        "11. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left lane next to the left adjacent lane changes lanes to the left adjacent lane.",
        "12. The ego vehicle is accelerating in the ego lane, and the target vehicle from the left lane next to the left adjacent lane changes lanes to the left adjacent lane.",
        "13. The ego vehicle is decelerating in the ego lane, and the target vehicle from the left lane next to the left adjacent lane changes lanes to the left adjacent lane.",
        "14. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left lane next to the left adjacent lane changes lanes to the left adjacent lane while accelerating.",
        "15. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left lane next to the left adjacent lane changes lanes to the left adjacent lane while decelerating.",
        "16. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right lane next to the right adjacent lane changes lanes to the right adjacent lane.",
        "17. The ego vehicle is accelerating in the ego lane, and the target vehicle from the right lane next to the right adjacent lane changes lanes to the right adjacent lane.",
        "18. The ego vehicle is decelerating in the ego lane, and the target vehicle from the right lane next to the right adjacent lane changes lanes to the right adjacent lane.",
        "19. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right lane next to the right adjacent lane changes lanes to the right adjacent lane while accelerating.",
        "20. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right lane next to the right adjacent lane changes lanes to the right adjacent lane while decelerating.",
        "21. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle.",
        "22. The ego vehicle is accelerating in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle.",
        "23. The ego vehicle is decelerating in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle.",
        "24. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle while accelerating.",
        "25. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle while decelerating.",
        "26. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle.",
        "27. The ego vehicle is accelerating in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle.",
        "28. The ego vehicle is decelerating in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle.",
        "29. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle while accelerating.",
        "30. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle while decelerating.",
        "31. The ego vehicle is driving straight in the ego lane, and the target vehicle behind accelerates.",
        "32. The ego vehicle is accelerating in the ego lane, and the target vehicle behind accelerates.",
        "33. The ego vehicle is decelerating in the ego lane, and the target vehicle behind accelerates.",
        "34. The ego vehicle is driving straight in the ego lane, and the target vehicle behind accelerates more aggressively.",
        "35. The ego vehicle is driving straight in the ego lane, and the target vehicle behind accelerates after decelerating.",
        "36. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead decelerates.",
        "37. The ego vehicle is accelerating in the ego lane, and the target vehicle ahead decelerates.",
        "38. The ego vehicle is decelerating in the ego lane, and the target vehicle ahead decelerates.",
        "39. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead decelerates rapidly.",
        "40. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead decelerates after accelerating.",
        "41. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead maintains its speed.",
        "42. The ego vehicle is accelerating in the ego lane, and the target vehicle ahead maintains its speed.",
        "43. The ego vehicle is decelerating in the ego lane, and the target vehicle ahead maintains its speed.",
        "44. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead maintains its speed while accelerating.",
        "45. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead maintains its speed while decelerating.",
        "46. The ego vehicle is driving straight in the ego lane, and the target vehicle behind maintains its speed.",
        "47. The ego vehicle is driving straight in the ego lane, and the target vehicle to the left maintains its speed.",
        "48. The ego vehicle is driving straight in the ego lane, and the target vehicle to the right maintains its speed.",
        "49. The ego vehicle changes lanes into the left adjacent lane in front of the target vehicle, which then accelerates.",
        "50. The ego vehicle changes lanes into the right adjacent lane in front of the target vehicle, which then accelerates.",
        "51. The ego vehicle changes lanes into the left adjacent lane in front of the target vehicle, which maintains its speed.",
        "52. The ego vehicle changes lanes into the right adjacent lane in front of the target vehicle, which maintains its speed.",
        "53. The ego vehicle changes lanes into the right adjacent lane behind the target vehicle, which decelerates.",
        "54. The ego vehicle changes lanes into the left adjacent lane behind the target vehicle, which decelerates.",
        "55. The ego vehicle changes lanes into the right adjacent lane behind the target vehicle, which maintains its speed.",
        "56. The ego vehicle changes lanes into the left adjacent lane behind the target vehicle, which maintains its speed.",
        "57. The ego vehicle and the target vehicle ahead both change lanes to the left simultaneously.",
        "58. The ego vehicle and the target vehicle ahead both change lanes to the right simultaneously.",
        "59. The ego vehicle and the target vehicle behind both change lanes to the left simultaneously.",
        "60. The ego vehicle and the target vehicle behind both change lanes to the right simultaneously.",
        "61. The ego vehicle changes lanes to the left lane, and the target vehicle ahead in the ego lane decelerates.",
        "62. The ego vehicle changes lanes to the right lane, and the target vehicle ahead in the ego lane decelerates.",
        "63. The ego vehicle changes lanes to the left lane, and the target vehicle ahead in the ego lane maintains its speed.",
        "64. The ego vehicle changes lanes to the right lane, and the target vehicle ahead in the ego lane maintains its speed.",
        "65. The ego vehicle changes lanes to the left lane, and the target vehicle behind in the ego lane accelerates to close the gap.",
        "66. The ego vehicle changes lanes to the right lane, and the target vehicle behind in the ego lane accelerates to close the gap.",
        "67. The ego vehicle changes lanes to the left lane, and the target vehicle behind in the ego lane maintains its speed.",
        "68. The ego vehicle changes lanes to the right lane, and the target vehicle behind in the ego lane maintains its speed.",
        "69. The ego vehicle closely follows the target vehicle as it changes lanes to the left.",
        "70. The ego vehicle closely follows the target vehicle as it changes lanes to the right.",
        "71. The ego vehicle changes lanes to the right lane, and a vehicle in the right lane changes to the ego lane behind the ego vehicle.",
        "72. The ego vehicle changes lanes to the left lane, and a vehicle in the left lane changes to the ego lane behind the ego vehicle.",
        "73. The ego vehicle changes lanes to the right lane, and a vehicle in the right lane changes to the ego lane ahead of the ego vehicle.",
        "74. The ego vehicle changes lanes to the left lane, and a vehicle in the left lane changes to the ego lane ahead of the ego vehicle."
    ] 

    # generate tracknums from 01 - 60
    track_nums = [f'{i:02}' for i in range(18,22)]

    metric_options = {
        'Jerk-Scale': 
        {'Longitudinal jerk (LongJ)': '1.5 - 100'},
        'Time-Scale': 
        {'Time To Collision (TTC)': '0.01 - 2',
         'Time Headway (THW)' : '0.01 - 0.3',},
        'Acceleration-Scale': 
        {"Deceleration to safety time (DST)" : '6 - 100'},
    }

    # for track_num in track_nums:
    #     for scenario_description in scenario_descriptions:
    #         # Update config with dynamic fields
    #         config = config_template.copy()
    #         config['dataset_path'] = f'/home/boron/myProjects/crconverter/data/highD/data/{track_num}_tracks.csv'
    #         config['scenario_description'] = scenario_description
            
    #         # Process the scenario
    #         process_scenario(config, metric_options, save_list=True, save_zip=True)


    # Use ThreadPoolExecutor for multithreading
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = []
        
        # Iterate over each track number and scenario description
        for track_num in track_nums:
            for scenario_description in scenario_descriptions:
                # Update config with dynamic fields
                config = config_template.copy()
                config['dataset_path'] = f'/home/boron/myProjects/crconverter/data/highD/data/{track_num}_tracks.csv'
                config['scenario_description'] = scenario_description
                
                # Submit the scenario processing task to the thread pool
                futures.append(executor.submit(threaded_process, config, metric_options))
        
        # Wait for all futures to complete and handle exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise any exception from the thread
            except Exception as exc:
                print(f"Scenario processing generated an exception: {exc}")

if __name__ == '__main__':
    main()

    #     "21. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle.",
#     "22. The ego vehicle is accelerating in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle.",
#     "23. The ego vehicle is decelerating in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle.",
#     "24. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle while accelerating.",
#     "25. The ego vehicle is driving straight in the ego lane, and the target vehicle from the left adjacent lane merges in front of the ego vehicle while decelerating.",
#     "26. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle.",
#     "27. The ego vehicle is accelerating in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle.",
#     "28. The ego vehicle is decelerating in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle.",
#     "29. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle while accelerating.",
#     "30. The ego vehicle is driving straight in the ego lane, and the target vehicle from the right adjacent lane merges in front of the ego vehicle while decelerating.",
#     "31. The ego vehicle is driving straight in the ego lane, and the target vehicle behind accelerates.",
#     "32. The ego vehicle is accelerating in the ego lane, and the target vehicle behind accelerates.",
#     "33. The ego vehicle is decelerating in the ego lane, and the target vehicle behind accelerates.",
#     "34. The ego vehicle is driving straight in the ego lane, and the target vehicle behind accelerates more aggressively.",
#     "35. The ego vehicle is driving straight in the ego lane, and the target vehicle behind accelerates after decelerating.",
#     "36. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead decelerates.",
#     "37. The ego vehicle is accelerating in the ego lane, and the target vehicle ahead decelerates.",
#     "38. The ego vehicle is decelerating in the ego lane, and the target vehicle ahead decelerates.",
#     "39. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead decelerates rapidly.",
#     "40. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead decelerates after accelerating.",
#     "41. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead maintains its speed.",
#     "42. The ego vehicle is accelerating in the ego lane, and the target vehicle ahead maintains its speed.",
#     "43. The ego vehicle is decelerating in the ego lane, and the target vehicle ahead maintains its speed.",
#     "44. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead maintains its speed while accelerating.",
#     "45. The ego vehicle is driving straight in the ego lane, and the target vehicle ahead maintains its speed while decelerating.",
#     "46. The ego vehicle is driving straight in the ego lane, and the target vehicle behind maintains its speed.",
#     "49. The ego vehicle changes lanes into the left adjacent lane in front of the target vehicle, which then accelerates.",
#     "50. The ego vehicle changes lanes into the right adjacent lane in front of the target vehicle, which then accelerates.",
#     "51. The ego vehicle changes lanes into the left adjacent lane in front of the target vehicle, which maintains its speed.",
#     "52. The ego vehicle changes lanes into the right adjacent lane in front of the target vehicle, which maintains its speed.",
#     "53. The ego vehicle changes lanes into the right adjacent lane behind the target vehicle, which decelerates.",
#     "54. The ego vehicle changes lanes into the left adjacent lane behind the target vehicle, which decelerates.",
#     "55. The ego vehicle changes lanes into the right adjacent lane behind the target vehicle, which maintains its speed.",
#     "56. The ego vehicle changes lanes into the left adjacent lane behind the target vehicle, which maintains its speed."
# ]