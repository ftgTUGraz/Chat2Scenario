"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import os
import re
import openai
import pdb

def extract_metric_name(self_define_metric_name, reminder_holder):
    """
    extract metric name from the string input by user

    Parameters:
    ----------
    Inputs:
        self_define_metric_name (str): name of the self-defined metric
        reminder_holder (st.empty()): holder for writing reminding message
    Returns:
        metric_name (str): code generating prompt to calculate metric value 
    ----------
    """
    metric_name = ""
    match = re.search(r'^\s*([^\(]+)', self_define_metric_name)
    if match:
        metric_name = match.group(1).strip()
    else:
        reminder_holder.warning("Metric name format could be wrong! Please check it!")
    
    return metric_name


def metric_equation_prompt(self_define_metric_name, self_define_metric, metric_name, frame_rate):
    """
    Generate code according to metric equation prompt

    Parameters:
    ----------
    Inputs:
        self_define_metric_name (str): name of the self-defined metric
        self_define_metric (str): equation description of self-deinfed metric
        metric_name (str): metric name without bracket
        frame_rate (int): frame rate of the recorded video (per second)
    Returns:
        prompt (str): code generating prompt to calculate metric value 
    ----------
    """
    Step_1 = "# Step 1. Adopt a persona:\n"
    prompt_1 = "Now, you are an excellent programmer. Finish the tasks using Python code. (The generated text should be executable by 'exec()' without any modification!)\n\n"

    Step_2 = "# Step 2. Read data:\n"
    prompt_2 = f"Use pandas to read csv file: tracks = pd.read_csv(dataset_load). (Note here 'dataset_load' is already defined elsewhere.)\n\n"
    
    Step_3 = "# Step 3. Data format clarification:\n"
    prompt_3 = " This file contains all relevant information of each trajectory, including ego vehicle and surrounding vehicles:\n\
        'frame' is the current frame number.\n\
        'id' is the unique id of vehicle.\n\
        'x' is bounding box center position in x axis of coordinate.\n\
        'y' is bounding box center position in y axis of coordinate.\n\
        'width' is the bounding box width of vehicle.\n\
        'height' is the bounding box height of vehicle.\n\
        'xVelocity' is the vehicle velocity along x axis of coordinate.\n\
        'yVelocity' is the vehicle velocity along y axis of coordinate.\n\
        'xAcceleration' is the vehicle acceleration along x axis of coordinate.\n\
        'yAcceleration' is the vehicle acceleration along y axis of coordinate.\n\
        'frontSightDistance' is the distance between bounding box center to the trajectory end along the driving direction.\n\
        'backSightDistance' is the distance between bounding box center to the trajectory begining along the driving direction.\n\
        'dhw' is distance headway, indicating the distance between current vehicle and the leading vehicle, if no leading vehicle then this value is set to 0.\n\
        'thw' is time headway, indicating the time of current vehicle need to reach the position of the leading vehicle, if no leading vehicle then this value is set to 0.\n\
        'ttc' is Time-to-Collision with the leading vehicle, if no leading vehicle then this value is set to 0. \n\
        'precedingXVelocity' is the velocity of the leading vehicle along the x-axis of coordinate, if no leading vehicle then this value is set to 0.\n\
        'procedingId' is the leading vehicle id with the same lane, if does not exist, this value is set to 0.\n\
        'followingId' is the following vehicle id with the same lane, if does not exist, this value is set to 0.\n\
        'leftPrecedingId' is the leading vehicle id in the left adjacent lane, if does not exist, this value is set to 0.\n\
        'leftAlongsideId' is the neighboring vehicle id in the left adjacent lane, if does not exist, this value is set to 0.\n\
        'leftFollowingId' is the following vehicle id in the left adjacent lane, if does not exist, this value is set to 0.\n\
        'rightPrecedingId' is the leading vehicle id in the right adjacent lane, if does not exist, this value is set to 0.\n\
        'rightAlongsideId' is the neighboring vehicle id in the right adjacent lane, if does not exist, this value is set to 0.\n\
        'rightFollowingId' is the following vehicle id in the right adjacent lane, if does not exist, this value is set to 0.\n\
        'laneId' is the Id of the current lane.\n\n"

    Step_4 = "# Step 4. Define a function to calculate desired metric:\n"
    prompt_4 = f"{self_define_metric_name} can be can be calculated with the following equation:\n\
        {self_define_metric}\n\
        Use float() to return the calculated {self_define_metric_name}\n\n"
    
    Step_5 = f"# Step 5. Calculate {self_define_metric_name}\n"
    prompt_5 = f"Follow the following steps to implement this step:\n\
    1) The original data were recorded in 30Hz. Downsample the data from 30Hz to 1Hz and store the sampled data into a dataframe called 'sampled_data'. (Only keep the frame number that are multiples of {frame_rate})\n\
    2) Tranversal each row of 'sampled_data' to calculate {self_define_metric_name} using for-loop e.g., for index, ego_row in sampled_data.iterrows()\n\
        (1) get target vehicle id from 'precedingId' and store in 'target_id'\n\
        (2) get current frame from 'frame' and store in 'curr_frame'\n\
        (3) find the corresponding row of target vehicle 'target_row', which has the same id with 'target_id' and the same frame with 'curr_frame'.\n\
        (4) use if-else to set a judgement to avoid empty 'target_row'. If 'target_row' is empty, 'nan' should be assigned.\n\
        (5) get all needed parameters of {self_define_metric_name} from 'ego_row' and 'target_row'\n\
        (6) callback function defined in step 4 to calculate {self_define_metric_name} (Name the calculated result as {metric_name}) \n\
        (7) add {metric_name} to 'sampled_data'\n\n"
    
    prompt = Step_1 + prompt_1 + Step_2 + prompt_2 + Step_3 + prompt_3 + Step_4 + prompt_4 + Step_5 + prompt_5

    return prompt


def excute_chatGPT_generated_code(self_define_metric_name, reminder_holder, dataset_load, self_define_metric, my_key, frame_rate):
    """
    Excute chatgpt generated python code

    Parameters:
    ----------
    Inputs:
        self_define_metric_name (str): name of the self-defined metric
        reminder_holder (st.empty()): holder for warning message 
        dataset_load (str): path of dataset
        self_define_metric (str): equation description of self-deinfed metric
        my_key (str): OpenAI API key
        frame_rate (int): frame rate of video (per second)
    Returns:
        variables["sampled_data"] (df): code generating prompt to calculate metric value 
        metric_name (str): name of the self-defined metric
    ----------
    """
    # equation code generation based on prompt
    metric_name = extract_metric_name(self_define_metric_name, reminder_holder)
    equation_prompt = metric_equation_prompt(self_define_metric_name, self_define_metric, metric_name, frame_rate)
    reminder_holder.warning("Start generate code using ChatGPT ......")
    equation_code = generate_text_with_openai(my_key, equation_prompt)
    print(equation_code)
    
    variables = {"dataset_load": dataset_load}
    # execute code to search scenarios
    try:
        reminder_holder.warning("Start execute generated code, please be patient ......")
        exec(equation_code, variables)
    except Exception as e:
        reminder_holder.warning(f"Error executing the generated code: {e}")
    
    return variables["sampled_data"], metric_name


def generate_text_with_openai(openai_key, prompt):
    """
    Generate text with openai based on prompt

    Parameters:
    ----------
    Inputs:
        openai_key (str): OpenAI API key
        prompt (str): prompt feeded to open ai model to generate text
    Returns:
        res (python code): 
    ----------
    """
    openai.api_key = openai_key
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            # model="gpt-4-1106-preview",
            messages=[
                {"role":"system", "content":"Generate Python Code Script."},
                {"role":"user", "content":prompt}])
    full_response = response["choices"][0]["message"]["content"]

    return full_response

