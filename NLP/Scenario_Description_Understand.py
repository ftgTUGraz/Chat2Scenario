"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import openai
import json
from typing import Optional, Dict, Any

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
def LLM_process_scenario_description(
    openai_key: str,
    scenario_description: str,
    classification_framework: Dict[str, Any],
    model: Optional[str] = "gpt-4o-mini-2024-07-18",
    base_url: Optional[str] = None
) -> Optional[str]:
    """
    Uses a Language Model (LLM) to understand a scenario description and classify it according to a provided framework.

    Parameters
    ----------
    openai_key : str
        API key for OpenAI.
    scenario_description : str
        Human-readable scenario description at the functional level from users.
    classification_framework : dict
        Pre-defined framework to classify the scenarios.
    model : str, optional
        Name of the model to use for the LLM, by default "gpt-4o-mini-2024-07-18".
    base_url : str, optional
        Base URL of the GPT-3 API, by default "https://api.openai.com/v1/".

    Returns
    -------
    Optional[str]
        The classification response from GPT, or `None` if an error occurs.
    """
    
    # Ensure classification_framework is a dictionary
    if not isinstance(classification_framework, dict):
        raise ValueError("classification_framework must be a dictionary.")

    # Prompt design using triple-quoted string for better readability
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

    client_kwargs = {
        "api_key": openai_key
    }
    print(f"Using OpenAI API key: ****************{openai_key[-4:]}")

    if base_url is not None:
        client_kwargs["base_url"] = base_url
        print(f"Using OpenAI base URL: {base_url}")

    # Assign OpenAI API key
    client = openai.OpenAI(**client_kwargs)

    print(f"Using OpenAI model: {model}")

    try:
        # Make API call to OpenAI's ChatCompletion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0  # Set temperature to 0 for deterministic output
        )
        
        # Extract and return the response content
        return response.choices[0].message.content
    
    except openai.AuthenticationError:
        print("Error: Invalid OpenAI API key provided.")
        return None
    except openai.BadRequestError:
        print("Error: Invalid request parameters provided.")
        return None
    except openai.RateLimitError:
        print("Error: Rate limit exceeded. Please try again later.")
        return None
    except openai.OpenAIError as e:
        print(f"An OpenAI error occurred: {e}")
        return None
    except KeyError:
        print("Error: Unexpected response structure from OpenAI API.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
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


def get_scenario_classification_via_LLM(
    openai_key: str,
    scenario_description: str,
    progress_bar: Optional[Any] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Obtain scenario classification from an LLM based on a provided classification framework.

    Parameters
    ----------
    openai_key : str
        OpenAI API key.
    scenario_description : str
        Scenario description using human language at the functional level from users.
    progress_bar : Any, optional
        Progress bar object (e.g., `st.progress(0)`), default is `None`.
    model : str, optional
        Name of the model to use for the LLM, default is `None` which lets the LLM use its default model.
    base_url : str, optional
        Base URL of the GPT API, default is `None` which uses OpenAI's default API endpoint.

    Returns
    -------
    dict or None
        Key labels in JSON format as a dictionary, or `None` if an error occurs.
    """
    # Update progress bar to 25% if provided
    if progress_bar is not None:
        progress_bar.progress(25)

    try:
        # Prepare arguments for LLM_process_scenario_description
        llm_kwargs = {
            "openai_key": openai_key,
            "scenario_description": scenario_description,
        }

        if classification_framework is not None:
            llm_kwargs["classification_framework"] = classification_framework
        
        # Include 'model' only if it's provided
        if model is not None:
            llm_kwargs["model"] = model
        if base_url is not None:
            llm_kwargs["base_url"] = base_url
        
        # Call the LLM processing function with appropriate arguments
        response = LLM_process_scenario_description(**llm_kwargs)
    
    except Exception as e:
        print(f"An error occurred while processing the scenario description: {e}")
        return None

    # Update progress bar to 100% if provided
    if progress_bar is not None:
        progress_bar.progress(100)

    if response is not None:
        try:
            # Extract key labels from the LLM response
            key_label = extract_json_from_response(response)
            return key_label
        except json.JSONDecodeError:
            print("Error: Failed to parse the LLM response as JSON.")
            return None
        except KeyError:
            print("Error: Unexpected response structure from the LLM.")
            return None
    else:
        print("Warning: Received no response from the LLM.")
        return None


def validate_scenario(sample, reminder_holder=None):
    """
    Validate the key label extracted from LLM response.

    Parameters:
    ----------
    Inputs:
        sample (dict): key label extracted from LLM response
        reminder_holder: st.empty() or None

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

    # ------------------------------- Check the ego vehicle --------------------------------
    # Check Ego Vehicle activities
    try: 
        ego_activities = sample.get('Ego Vehicle', {})
        if not ego_activities:
            if reminder_holder is not None:
                reminder_holder.warning(":cry: Invalid Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            else:
                print(":cry: Invalid Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
    except AttributeError:
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    # Check Ego longitudinal activities
    try:
        ego_lon_act = ego_activities.get('Ego longitudinal activity', [])
        if not ego_lon_act:
            if reminder_holder is not None:
                reminder_holder.warning(":cry: Invalid Ego longitudinal activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            else:
                print(":cry: Invalid Ego longitudinal activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
    except AttributeError:
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid Ego longitudinal activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid Ego longitudinal activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    # Check Ego lateral activities
    try: 
        ego_lat_act = ego_activities.get('Ego lateral activity', [])
        if not ego_lat_act:
            if reminder_holder is not None:
                reminder_holder.warning(":cry: Invalid Ego lateral activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            else:
                print(":cry: Invalid Ego lateral activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
    except AttributeError:
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid Ego lateral activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid Ego lateral activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    if not (isinstance(ego_lon_act, list) and isinstance(ego_lat_act, list)):
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid Ego Vehicle activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid Ego Vehicle activities. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    # Check lateral and longitudinal activity for ego
    egoLonActCheck = check_activities(ego_lon_act, model['Ego Vehicle']['longitudinal activity'])
    egoLatActCheck = check_activities(ego_lat_act, model['Ego Vehicle']['lateral activity'])
    if not egoLonActCheck:
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid longitudinal activities for Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid longitudinal activities for Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False
    if not egoLatActCheck:
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid lateral activities for Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid lateral activities for Ego Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
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
                    if reminder_holder is not None:
                        reminder_holder.warning(":cry: Invalid Target behavior. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    else:
                        print(":cry: Invalid Target behavior. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False
            except AttributeError:
                if reminder_holder is not None:
                    reminder_holder.warning(":cry: Invalid Target behavior. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                else:
                    print(":cry: Invalid Target behavior. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                return False

            # Check target longitudinal activity
            try:
                tgt_lon_act = target_behavior.get('target longitudinal activity', [])
                if not tgt_lon_act:
                    if reminder_holder is not None:
                        reminder_holder.warning(":cry: Invalid Target longitudinal activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    else:
                        print(":cry: Invalid Target longitudinal activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False
            except AttributeError:
                if reminder_holder is not None:
                    reminder_holder.warning(":cry: Invalid Target longitudinal activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                else:
                    print(":cry: Invalid Target longitudinal activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                return False

            # Check the target lateral activity
            try:              
                tgt_lat_act = target_behavior.get('target lateral activity', [])
                if not tgt_lat_act:
                    if reminder_holder is not None:
                        reminder_holder.warning(":cry: Invalid Target lateral activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    else:
                        print(":cry: Invalid Target lateral activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False
            except AttributeError:
                if reminder_holder is not None:
                    reminder_holder.warning(":cry: Invalid Target lateral activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                else:
                    print(":cry: Invalid Target lateral activity. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                return False

            if not (isinstance(tgt_lon_act, list) and isinstance(tgt_lat_act, list)):
                if reminder_holder is not None:
                    reminder_holder.warning(f"Target Vehicle activities should be lists for {target_vehicle}.")
                else:
                    print(f"Target Vehicle activities should be lists for {target_vehicle}.")
                return False

            # Check behaviors against the model
            tgtLonActCheck = check_activities(tgt_lon_act, model['Target Vehicle']['behavior']['longitudinal activity'])
            tgtLatActCheck = check_activities(tgt_lat_act, model['Target Vehicle']['behavior']['lateral activity'])

            if not tgtLonActCheck:
                if reminder_holder is not None:
                    reminder_holder.warning(f"Invalid longitudinal activities for {target_vehicle}.")
                else:
                    print(f"Invalid longitudinal activities for {target_vehicle}.")
                return False

            if not tgtLatActCheck:
                if reminder_holder is not None:
                    reminder_holder.warning(f"Invalid lateral activities for {target_vehicle}.")
                else:
                    print(f"Invalid lateral activities for {target_vehicle}.")
                return False

            # Check Target start and end positions
            for position_key in ['Target start position', 'Target end position']:
                position = details.get(position_key, {})
                if not isinstance(position, dict) or not position:
                    if reminder_holder is not None:
                        reminder_holder.warning(f"Invalid {position_key} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    else:
                        print(f"Invalid {position_key} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                    return False

                for pos_type, pos_value in position.items():
                    if pos_type in model['Target Vehicle']['position']:
                        if not check_activities(pos_value, model['Target Vehicle']['position'][pos_type]):
                            if reminder_holder is not None:
                                reminder_holder.warning(f"Invalid {position_key} in {pos_type} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                            else:
                                print(f"Invalid {position_key} in {pos_type} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                            return False
                    else:
                        if reminder_holder is not None:
                            reminder_holder.warning(f"Invalid position type: {pos_type} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                        else:
                            print(f"Invalid position type: {pos_type} for {target_vehicle}. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
                        return False
        else:
            if reminder_holder is not None:
                reminder_holder.warning(":cry: Invalid Target Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            else:
                print(":cry: Invalid Target Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
            return False
        
        tgt_idx += 1

    if index == 0:
        if reminder_holder is not None:
            reminder_holder.warning(":cry: Invalid Target Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        else:
            print(":cry: Invalid Target Vehicle. Enrich your descriptive text of scenarios. Include the lateral and longitudinal activities of both the ego and target vehicles, as well as the start and end positions of the target vehicle.")
        return False

    return True

