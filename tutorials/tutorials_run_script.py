
def main():
    """
    Main function to execute multiple scenario processing based on predefined configurations.
    """
    # Define multiple configurations as a list of dictionaries, this is a config template
    # some of the config options will be modified during for loop iterations
    config = {
            'name': 'Scenario 0',
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
    metric_options = {
        'Distance-Scale': 
        {'Distance Headway (DHW)': '1 - 50'},
        # 'Jerk-Scale': 
        # {'Longitudinal jerk (LongJ)': '1 - 15',
        #  'Lateral jerk (LatJ)': '1 - 15'},
        'Time-Scale': 
        {'Time To Collision (TTC)': '1 - 15',
         'Time Headway (THW)': '1 - 5'},
    }
    
    # Iterate over each configuration and process the scenario
    for track_num in track_nums:
        for scenario_description in scenario_descriptions:
            config['dataset_path'] = f'/home/boron/myProjects/crconverter/data/highD/data/{track_num}_tracks.csv'
            config['scenario_description'] = scenario_description
            # process_scenario(config, metric_options)

if __name__ == '__main__':
    main()
