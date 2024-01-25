"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import openai
import json

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
def LLM_process_scenario_description(openai_key, scenario_description, classification_framework):
    """
    Use the LLM to understand the scenario description and assign to the classification framework

    Parameters:
    ----------
    Inputs:
        openai_key (str): key of openai api
        scenario_description (str): scenario description using human language in functional level from users 
        classification_framework (str): pre-defined framework to classify the scenarios 

    Returns:
        response of GPT
    ----------
    """

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

    # Assign openai key
    openai.api_key = openai_key

    # Feed prompt to openai LLM
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role":"user", "content":prompt}])
    
    # Return response from GPT
    return response["choices"][0]["message"]["content"]


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


def get_scenario_classification_via_LLM(openai_key, scenario_description, progress_bar):
    """
    get scenario classification from LLM

    Parameters:
    ----------
    Inputs:
        openai_key (str): openai api key 
        scenario_description (str): scenario description using human language in functional level from users 
        progress_bar (st.progress(0)): progress bar in 0%

    Returns:
        key labels in the format of json
    ----------
    """
    # Get response from LLM
    progress_bar.progress(25)
    response = LLM_process_scenario_description(openai_key, scenario_description, classification_framework)
    progress_bar.progress(100)
    # Extract key labels
    key_label = extract_json_from_response(response)

    return key_label


# length of key_label can be used to judge how many target vehicles are contained



