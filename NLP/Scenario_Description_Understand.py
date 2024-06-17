"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import openai
import json
import openai.error

### Define framework to classify scenarios in functional level
classification_framework = {
    "ego": 
    {
        "ego longitudinal activity": ["keep velocity", "acceleration", "deceleration"],
        "ego lateral activity": ["follow lane", "lane change left", "lane change right"]
    },
    "target": 
    {
        "target position": 
        {
            "same lane": ["front", "behind"],
            "adjacent lane": ["left adjacent lane", "right adjacent lane"],
            "lane next to adjacent lane": ["lane next to left adjacent lane", "lane next to right adjacent lane"]
        },
        "target activity": 
        {
            "target longitudinal activity": ["keep velocity", "acceleration", "deceleration"],
            "target lateral activity": ["follow lane", "lane change left", "lane change right"]
        }
    }
}


### Openai LLM to process human language of scenario description
def LLM_process_scenario_description(openai_key, scenario_description, classification_framework,dataset_option):
    """
    Use the LLM to understand the scenario description and assign to the classification framework

    Parameters:
    ----------
    Inputs:
        openai_key (str): key of openai api
        scenario_description (str): scenario description using human language in functional level from users 
        classification_framework (str): pre-defined framework to classify the scenarios 

    Returns:
        response of GPT [None, if error occurs]
    ----------
    """
    if dataset_option == "highD":
        # Prompt design
        prompt = f"System, you are an AI trained to understand and classify driving scenarios based on specific frameworks.Your task is to analyze the following driving scenario and classify the behavior of both the ego vehicle and the target vehicle according to the given classification framework. Please follow the framework strictly and provide precise and clear classifications. The framework is as follows:\n\n{json.dumps(classification_framework, indent=4)}\n\n"\
        "Scenario Description: \n"\
        f"'{scenario_description}'\n\n"\
        "Provide a detailed classification for both the ego vehicle and the target vehicle(s). The response should be formatted exactly as shown in this structure:\n"\
        "{\n"\
        "    'Ego Vehicle': \n"\
        "    {\n"\
        "        'Ego longitudinal activity': ['Your Classification'],\n"\
        "        'Ego lateral activity': ['Your Classification']\n"\
        "    },\n"\
        "    'Target Vehicle #1': \n"\
        "    {\n"\
        "        'Target start position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target end position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target behavior': {'target longitudinal activity': ['Your Classification'], 'target lateral activity': ['Your Classification']}\n"\
        "    }\n"\
        "    'Target Vehicle #2': \n"\
        "    {\n"\
        "        'Target start position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target end position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target behavior': {'target longitudinal activity': ['Your Classification'], 'target lateral activity': ['Your Classification']}\n"\
        "    }\n"\
        "}\n"\
        "Example:\n"\
        "If an ego vehicle is maintaining speed and following its lane, while another vehicle is initially in the left adjacent lane and is accelerating, then changing lanes to the right; finally driving on the front of ego vehicle, the classification would be:\n"\
        "{\n"\
        "    'Ego Vehicle': \n"\
        "    {\n"\
        "        'Ego longitudinal activity': ['keep velocity'],\n"\
        "        'Ego lateral activity': ['follow lane']\n"\
        "    },\n"\
        "    'Target Vehicle': \n"\
        "    {\n"\
        "        'Target start position': {'adjacent lane': ['left adjacent lane']},\n"\
        "        'Target end position': {'same lane': ['front']},\n"\
        "        'Target behavior': {'target longitudinal activity': ['acceleration'], 'target lateral activity': ['lane change right']}\n"\
        "    }\n"\
        "}\n\n"\
        "Remember to analyze carefully and provide the classification as per the structure given above."
    
    elif dataset_option == "inD": 
        # Prompt design for inD dataset
        prompt = f"System, you are an AI trained to understand and classify urban driving scenarios based on specific frameworks. Your task is to analyze the following urban driving scenario and classify the behavior of both the ego vehicle and the target vehicle according to the given classification framework. Please follow the framework strictly and provide precise and clear classifications. The framework is as follows:\n\n{json.dumps(classification_framework, indent=4)}\n\n"\
            "Scenario Description: \n"\
            f"'{scenario_description}'\n\n"\
            "Provide a detailed classification for both the ego vehicle and the target vehicle(s). The response should be formatted as follows:\n"\
            "{\n"\
            "    'Ego Vehicle': \n"\
            "    {\n"\
            "        'turn_type': 'Your Classification'\n"\
            "    },\n"\
            "    'Target Vehicle': \n"\
            "    {\n"\
            "        'turn_type': 'Your Classification'\n"\
            "    }\n"\
            "}\n\n"\
            "Example:\n"\
            "If an ego vehicle is making a right turn at an intersection while a target vehicle is approaching the intersection and proceeds straight through, the classification would be:\n"\
            "{\n"\
            "    'Ego Vehicle': \n"\
            "    {\n"\
            "        'turn_type': 'right'\n"\
            "    },\n"\
            "    'Target Vehicle': \n"\
            "    {\n"\
            "        'turn_type': 'straight'\n"\
            "    }\n"\
            "}\n\n"\
            "Remember to analyze carefully and provide the classification as per the structure given above."
        
    elif dataset_option == "exitD":
        # Prompt design for exitD dataset
        prompt = f"System, you are an AI trained to understand and classify highway driving scenarios, including entrance and exit ramps, based on specific frameworks. Your task is to analyze the following driving scenario and classify the behavior of both the ego vehicle and the target vehicle according to the given classification framework. Please follow the framework strictly and provide precise and clear classifications. The framework is as follows:\n\n{json.dumps(classification_framework, indent=4)}\n\n"\
        "Scenario Description: \n"\
        f"'{scenario_description}'\n\n"\
        "Provide a detailed classification for both the ego vehicle and the target vehicle(s). The response should be formatted exactly as shown in this structure:\n"\
        "{\n"\
        "    'Ego Vehicle': \n"\
        "    {\n"\
        "        'Ego longitudinal activity': ['Your Classification'],\n"\
        "        'Ego lateral activity': ['Your Classification'],\n"\
        "        'Ego ramp activity': ['Your Classification']\n"\
        "    },\n"\
        "    'Target Vehicle #1': \n"\
        "    {\n"\
        "        'Target start position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target end position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target behavior': {'target longitudinal activity': ['Your Classification'], 'target lateral activity': ['Your Classification'], 'target ramp activity': ['Your Classification']}\n"\
        "    }\n"\
        "    'Target Vehicle #2': \n"\
        "    {\n"\
        "        'Target start position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target end position': {'Your Classification': ['Your Classification']},\n"\
        "        'Target behavior': {'target longitudinal activity': ['Your Classification'], 'target lateral activity': ['Your Classification'], 'target ramp activity': ['Your Classification']}\n"\
        "    }\n"\
        "}\n"\
        "Example:\n"\
        "If an ego vehicle is maintaining speed and following its lane on a highway, then taking the OffRamp, while another vehicle is initially in the left adjacent lane and is accelerating, then changing lanes to the right; finally driving in front of the ego vehicle and also taking the OffRamp, the classification would be:\n"\
        "{\n"\
        "    'Ego Vehicle': \n"\
        "    {\n"\
        "        'Ego longitudinal activity': ['keep velocity'],\n"\
        "        'Ego lateral activity': ['follow lane'],\n"\
        "        'Ego ramp activity': ['OffRamp']\n"\
        "    },\n"\
        "    'Target Vehicle': \n"\
        "    {\n"\
        "        'Target start position': {'adjacent lane': ['left adjacent lane']},\n"\
        "        'Target end position': {'same lane': ['front']},\n"\
        "        'Target behavior': {'target longitudinal activity': ['acceleration'], 'target lateral activity': ['lane change right'], 'target ramp activity': ['OffRamp']}\n"\
        "    }\n"\
        "}\n\n"\
        "Remember to analyze carefully and provide the classification as per the structure given above."


    # Assign openai key
    openai.api_key = openai_key

    try:
        # Feed prompt to openai LLM
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role":"user", "content":prompt}])
        return response["choices"][0]["message"]["content"]
    except openai.error.AuthenticationError:
        print("Warning: Invalid OpenAI API key.")
        return None
    except openai.error.OpenAIError as e:
        print(f"An error occurred: {e}") 
        return None
    

### Process the GPT response
def extract_json_from_response(response):
    """
    Extract key labels from GPT response

    Parameters:
    ----------
    Inputs:
        response (str): response of GPT containing the key lables of scenarios

    Returns:
        key labels in the format of json
    ----------
    """
    start_index = response.find('{')
    end_index = response.rfind('}') + 1  # +1 to include the closing brace
    json_string = response[start_index:end_index]
    json_string = json_string.replace("'", '"')  # Replace single quotes with double quotes for valid JSON
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def get_scenario_classification_via_LLM(openai_key, scenario_description, progress_bar,dataset_option):
    """
    get scenario classification from LLM

    Parameters:
    ----------
    Inputs:
        openai_key (str): openai api key 
        scenario_description (str): scenario description using human language in functional level from users 
        progress_bar (st.progress(0)): progress bar in 0%

    Returns:
        key labels in the format of json [None, if error occures]
    ----------
    """
    # Get response from LLM
    progress_bar.progress(25)
    response = LLM_process_scenario_description(openai_key, scenario_description, classification_framework,dataset_option)
    progress_bar.progress(100)
    if response is not None:
        # Extract key labels
        key_label = extract_json_from_response(response)
        return key_label
    else:
        return None


def validate_scenario(sample, reminder_holder):
    """
    Validate the key label extracted from LLM response.

    Parameters:
    ----------
    Inputs:
        sample (dict): key label extracted from LLM response
        reminder_holder: st.empty()

    Returns:
        bool: True if key_label is valid, False otherwise
    ----------
    """
    # Standard model
    model = {
        'Ego Vehicle': {
            'longitudinal activity': ['keep velocity', 'acceleration', 'deceleration'],
            'lateral activity': ['follow lane', 'lane change left', 'lane change right']
        },
        'Target Vehicle': {
            'position': {
                'same lane': ['front', 'behind'],
                'adjacent lane': ['left adjacent lane', 'right adjacent lane'],
                'lane next to adjacent lane': ['lane next to left adjacent lane', 'lane next to right adjacent lane']
            },
            'behavior': {
                'longitudinal activity': ['keep velocity', 'acceleration', 'deceleration'],
                'lateral activity': ['follow lane', 'lane change left', 'lane change right']
            }
        }
    }

    # Helper function to check activities
    def check_activities(activities, model_activities):
        if not isinstance(activities, list):
            return False
        return all(activity in model_activities for activity in activities)

    # ------------------------------- Check the ego vehicke --------------------------------
    # Check Ego Vehicle activities
    try: 
        ego_activities = sample.get('Ego Vehicle', {})
        if not ego_activities:
            reminder_holder.warning(":cry: Invalid Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
    except AttributeError:
        reminder_holder.warning(":cry: Invalid Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False
    
    # Check Ego longitudinal activities
    try:
        ego_lon_act = ego_activities.get('Ego longitudinal activity', [])
        if not ego_lon_act:
            reminder_holder.warning(":cry: Invalid Ego longitudinal activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
    except AttributeError:
        reminder_holder.warning(":cry: Invalid Ego longitudinal activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    # Check Ego lateral activities
    try: 
        ego_lat_act = ego_activities.get('Ego lateral activity', [])
        if not ego_lat_act:
            reminder_holder.warning(":cry: Invalid Ego lateral activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
    except AttributeError:
        reminder_holder.warning(":cry: Invalid Ego lateral activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    if not (isinstance(ego_lon_act, list) and isinstance(ego_lat_act, list)):
        reminder_holder.warning(":cry: Invalid Ego Vehicle activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    # Check latereal and longitudinal activity for ego
    egoLonActCheck = check_activities(ego_lon_act, model['Ego Vehicle']['longitudinal activity'])
    egoLatActCheck = check_activities(ego_lat_act, model['Ego Vehicle']['lateral activity'])
    if not egoLonActCheck:
        reminder_holder.warning(":cry: Invalid longitudinal activities for Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False
    if not egoLatActCheck:
        reminder_holder.warning(":cry: Invalid lateral activities for Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False


    # --------------------------Check the target vehicle------------------------------
    # Check Target Vehicle activities and positions
    tgt_idx = 1
    # for target_vehicle, details in sample.items():
    for index, (target_vehicle, details) in enumerate(sample.items()):
        if index == 0:
            continue  
        curr_tgt_veh = "Target Vehicle #" + str(tgt_idx)
        if curr_tgt_veh in target_vehicle:
            # Check Target behavior
            try:
                target_behavior = details.get('Target behavior', {})
                if not target_behavior:
                    reminder_holder.warning(":cry: Invalid Target behavior. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False
            except AttributeError:
                reminder_holder.warning(":cry: Invalid Target behavior. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                return False
            
            # Check target lon act
            try:
                tgt_lon_act = target_behavior.get('target longitudinal activity', [])
                if not tgt_lon_act:
                    reminder_holder.warning(":cry: Invalid Target longitudinal activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False
            except AttributeError:
                reminder_holder.warning(":cry: Invalid Target longitudinal activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                return False

            # Check the target lat act
            try:              
                tgt_lat_act = target_behavior.get('target lateral activity', [])
                if not tgt_lat_act:
                    reminder_holder.warning(":cry: Invalid Target lateral activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False
            except AttributeError:
                reminder_holder.warning(":cry: Invalid Target lateral activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                return False

            if not (isinstance(tgt_lon_act, list) and isinstance(tgt_lat_act, list)):
                reminder_holder.warning(f"Target Vehicle activities should be lists for {target_vehicle}.")
                return False

            tgtLonActCheck = check_activities(tgt_lon_act, model['Target Vehicle']['behavior']['longitudinal activity'])
            tgtLatActCheck = check_activities(tgt_lat_act, model['Target Vehicle']['behavior']['lateral activity'])

            if not tgtLonActCheck:
                reminder_holder.warning(f"Invalid longitudinal activities for {target_vehicle}")
                return False

            if not tgtLatActCheck:
                reminder_holder.warning(f"Invalid lateral activities for {target_vehicle}")
                return False

            # Check Target start and end positions
            for position_key in ['Target start position', 'Target end position']:
                position = details.get(position_key, {})
                if not isinstance(position, dict) or not position:
                    reminder_holder.warning(f"Invalid {position_key} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    # print(f"{position_key} should be a dictionary for {target_vehicle}.")
                    return False

                for pos_type, pos_value in position.items():
                    if pos_type in model['Target Vehicle']['position']:
                        if not check_activities(pos_value, model['Target Vehicle']['position'][pos_type]):
                            reminder_holder.warning(f"Invalid {position_key} in {pos_type} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                            return False
                    else:
                        reminder_holder.warning(f"Invalid position type: {pos_type} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                        return False
        else:
            reminder_holder.warning(":cry: Invalid Target Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
        
        tgt_idx += 1

    if index == 0:
        reminder_holder.warning(":cry: Invalid Target Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    return True
