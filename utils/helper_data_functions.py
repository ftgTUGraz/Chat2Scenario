"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import pandas as pd
import numpy as np
from scenariogeneration import xosc
import math

def get_data_from_frames(folder_path, csv_prefix, start_frame, end_frame, left_lane_ids, right_lane_ids):

    recording_meta_path = folder_path + f"{csv_prefix}_recordingMeta.csv"
    tracks_meta_path = folder_path + f"{csv_prefix}_tracksMeta.csv"
    tracks_path = folder_path + f"{csv_prefix}_tracks.csv"

    # Load the data from the CSV files
    recording_meta = pd.read_csv(recording_meta_path)
    tracks_meta = pd.read_csv(tracks_meta_path)
    tracks = pd.read_csv(tracks_path)

    # Extract desired frames
    tracks_filtered = tracks[(tracks["frame"] >= start_frame) & (tracks["frame"] <= end_frame)]

    lane_ids = left_lane_ids + right_lane_ids
    # Traffic participants moving to left
    tracks_filtered = tracks_filtered[tracks_filtered['laneId'].isin(lane_ids)]


    return recording_meta, tracks_meta, tracks_filtered


def get_data_from_id(tracks_filtered):

    # Get all information for each unique id from tracks_filtered
    unique_ids = []
    id_information = {}

    # Loop through the unique id values
    for unique_id in tracks_filtered["id"].unique():
        # Filter the DataFrame for the current id
        data_for_id = tracks_filtered[tracks_filtered["id"] == unique_id]
        # Store the information for the current id in the id_information dictionary
        id_information[unique_id] = data_for_id.to_dict(orient="list")
        unique_ids.append(unique_id)
    
    return id_information, unique_ids


def get_data_for_scenario(id_information, id):
    id_info = id_information.get(id, {})
    data_dict = {}

    # Store "frame" directly in the data_dict
    data_dict["frame"] = id_info.get("frame", [])

    # Extract other data from id_info with default values using a for loop
    for key in ["x", "y", "xVelocity", "yVelocity", "width", "height", "orientation", "laneId"]:
        data_dict[key] = id_info.get(key, [])

    id_xV, id_yV = id_info.get("xVelocity", []), id_info.get("yVelocity", [])
    data_dict["sumV"] = [np.sqrt(vx ** 2 + vy ** 2) for vx, vy in zip(id_xV, id_yV)]

    # Calculate mean_width_id and mean_height_id using a function
    id_width, id_height = id_info.get("width", []), id_info.get("height", [])
    data_dict["mean_width"] = sum(id_width) / len(id_width) if id_width else None
    data_dict["mean_height"] = sum(id_height) / len(id_height) if id_height else None
    return data_dict

def traj_repair(id_, id_orientaiton, framerate, start_frame):

    time_list = []
    position_list = []

    if min(id_["frame"]) == 0:
        
        for i in id_["frame"]:
            t = i/framerate
            time_list.append(t)
            
        for i in range(len(id_["frame"])):
            position_list.append(xosc.WorldPosition(id_["x"][i], -id_["y"][i], 0, id_orientaiton[i]+math.pi, 0, 0))

    elif min(id_["frame"]) > 0: # repair late appear: stand still
        if not time_list and not position_list:
            time_list.append(0)
            position_list.append(xosc.WorldPosition(id_["x"][0], -id_["y"][0], 0, id_orientaiton[0]+math.pi, 0, 0))

        for i in id_["frame"]:
            t = (i - start_frame)/30
            time_list.append(t)

        for i in range(len(id_["frame"])):
            position_list.append(xosc.WorldPosition(id_["x"][i], -id_["y"][i], 0, id_orientaiton[i]+math.pi, 0, 0))

    return time_list, position_list


def init_state_estimate(init_frame, init_x, init_y, init_speed, init_orientation, framerate):

    missing_time = init_frame/framerate
    missing_dist = missing_time*init_speed
    init_x_estimate = init_x + missing_dist # plus or minus depends on the reaility
    init_y_estimate = init_y
    init_orientation_estimate = init_orientation + math.pi

    return init_x_estimate, init_y_estimate, init_speed, init_orientation_estimate

def calculate_initial_state(id_,framerate,left_lane_ids,right_lane_ids):
    init_frame = id_["frame"][0]
    init_x = id_["x"][0]
    init_y = -id_["y"][0]
    init_speed = id_["sumV"][0]
    init_orientation = id_["orientation"][0]
    init_laneId = id_["laneId"][0]


    if min(id_["frame"]) > 0:
        init_x, init_y, init_speed, init_orientation = init_state_estimate(init_frame, init_x, init_y, init_speed, init_orientation,  framerate)
    return {
        'init_frame': init_frame,
        'init_x': init_x,
        'init_y': init_y,
        'init_speed': init_speed,
        'init_orientation': init_orientation,
        'init_laneId': init_laneId
    }

def create_init(init,init_state,entityname):

    step_time = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1)
    init_speed_act = xosc.AbsoluteSpeedAction(init_state["init_speed"], step_time)
    init_pos = xosc.TeleportAction(xosc.WorldPosition(init_state["init_x"], init_state["init_y"], 0, init_state["init_orientation"], 0, 0))
    init.add_init_action(entityname, init_speed_act)
    init.add_init_action(entityname, init_pos)

def create_name(entityname):
    return f"{entityname}_manGroup", f"{entityname}_man", f"{entityname}_event", f"{entityname}_action"

def create_xosc(entityname):
    manGroupName,manName,eventName,actionname = create_name(entityname)
    manGroup = xosc.ManeuverGroup(manGroupName)
    man = xosc.Maneuver(manName)
    event = xosc.Event(eventName, xosc.Priority.parallel)
    trigger = xosc.ValueTrigger("start_event", 0, xosc.ConditionEdge.none, xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan))
    return manGroup,man,event,trigger
    
