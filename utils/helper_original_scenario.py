"""
Author: Yongqi Zhao
Date Created: 2023-11-28
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
import pandas as pd
from scenariogeneration import xosc, prettyprint
import os
import numpy as np
import streamlit as st
import time
from Metric.Acceleration_Scale import *
from Metric.Distance_Scale import *
from Metric.Jerk_Scale import *
from Metric.Time_Scale import *
from scipy import stats
from xml.dom import minidom
from io import BytesIO
import xml.etree.ElementTree as ET

def create_act():

    starttrigger = xosc.ValueTrigger(
        "starttrigger",
        0,
        xosc.ConditionEdge.none,
        xosc.SimulationTimeCondition(0, xosc.Rule.greaterOrEqual),
    )
    act = xosc.Act("my_act", starttrigger)

    return act


def create_story(entityname):

    # parameter declaration for story
    storyparam = xosc.ParameterDeclarations()
    storyparam.add_parameter(
        xosc.Parameter("$owner", xosc.ParameterType.string, entityname)
    )
    story = xosc.Story("mystory", storyparam)
    
    return story


def create_roadnetwork(roadfile_path= "../xodr/highD_01_highway.xodr"):

    # road = xosc.RoadNetwork(roadfile="../xodr/DJI_0001.xodr", scenegraph="../models/e6mini.osgb")
    road = xosc.RoadNetwork(roadfile=roadfile_path)

    return road


def create_catalog(catalogname="VehicleCatalog", path="../xosc/Catalogs/Vehicles"):

    catalog = xosc.Catalog()
    catalog.add_catalog(catalogname, path)

    return catalog


def create_parameter_declearations(name="$HostVehicle", value="car_white"):

    paramdec = xosc.ParameterDeclarations()
    paramdec.add_parameter(xosc.Parameter(name, xosc.ParameterType.string, value))

    return paramdec


def get_data(folder_path, csv_prefix):
    """
    Read data from csv.

    Args:
        folder_path (type): Description of the first argument.
        csv_prefix (type): Description of the second argument.

    Returns:
        recording_meta: Description of the return value.
        tracks_meta:
        tracks:

    Example:
        folder_path = r'C:\PhD\Dataset\DJI_AD4CHE\AD4CHE_V1.0\AD4CHE_Data_V1.0\DJI_0001'
        csv_prefix = "\\01"
    """

    recording_meta_path = folder_path + f"{csv_prefix}_recordingMeta.csv"
    tracks_meta_path = folder_path + f"{csv_prefix}_tracksMeta.csv"
    tracks_path = folder_path + f"{csv_prefix}_tracks.csv"

    # Load the data from the CSV files
    recording_meta = pd.read_csv(recording_meta_path)
    tracks_meta = pd.read_csv(tracks_meta_path)
    tracks = pd.read_csv(tracks_path)

    return recording_meta, tracks_meta, tracks


def add_everything(object_track, entities, cataref, init, act):
    """
    create entity

    Args:
        object_track (dataframe): format of csv   
        entities, cataref, init, act: defined previously
    """

    # create entities
    entityname = "obj_"+str(object_track.iloc[0]['id'])
    entities.add_scenario_object(entityname, cataref)

    # create init
    step_time = xosc.TransitionDynamics(
        xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1)
    init_speed_act = xosc.AbsoluteSpeedAction(np.sqrt(
        object_track.iloc[0]['xVelocity']**2+object_track.iloc[0]['yVelocity']**2), step_time)
    if 'orientation' in object_track.columns:
        object_track_orientation = object_track.iloc[0]['orientation']
    else:
        object_track_orientation = 0
    init_pos = xosc.TeleportAction(xosc.WorldPosition(
        object_track.iloc[0]['x'], object_track.iloc[0]['y'], 0, object_track_orientation, 0, 0))
    init.add_init_action(entityname, init_speed_act)
    init.add_init_action(entityname, init_pos)

    # create maneuer group
    manGroupName = entityname + "_manGroup"
    manGroup = xosc.ManeuverGroup(manGroupName)
    # create maneuver
    manName = entityname + "_man"
    man = xosc.Maneuver(manName)
    # create event
    eventName = entityname + "_event"
    event = xosc.Event(eventName, xosc.Priority.parallel)
    # create start trigger for event
    trigger = xosc.ValueTrigger("start", 0, xosc.ConditionEdge.none,
                                xosc.SimulationTimeCondition(0, xosc.Rule.greaterOrEqual))
    # create action
    actionname = entityname + "_action"

    # create time_list and position_list with existing states
    time_list = object_track['time'].tolist()
    position_list = []

    for i in range(len(object_track['frame'])):
        if 'orientation' in object_track.columns:
            object_track_orientation = object_track.iloc[i]['orientation']
        else:
            object_track_orientation = 0
        position_list.append(xosc.WorldPosition(
            object_track.iloc[i]['x'], object_track.iloc[i]['y'], 0, object_track_orientation, 0, 0))

    polyline = xosc.Polyline(time_list, position_list)

    # define trajectory according to polyline: true means trajectory closed at the end
    traj = xosc.Trajectory("my_trajectory", False)
    traj.add_shape(polyline)

    trajaction = xosc.FollowTrajectoryAction(traj, xosc.FollowingMode.position)

    # add everything into Act
    event.add_action(actionname, trajaction)
    event.add_trigger(trigger)
    man.add_event(event)
    manGroup.add_actor(entityname)
    manGroup.add_maneuver(man)
    act.add_maneuver_group(manGroup)


def xosc_generation(sim_time, output_path, ego_track, target_tracks_sampled):
    """
    create xosc file

    Args:
        sim_time (double): Duration of simulation time.
        output_path (path): Path of output file.
        ego_track (dataframe): Fictive ego vehicle track
        target_tracks_sampled (list): Fictive target vehicle track
    """

    # parameter + catalog + roadnetwork (independent on the number of entities)
    paramdec = create_parameter_declearations()
    catalog = create_catalog()
    road = create_roadnetwork()

    # utilize the default vehicle catalog
    cataref = xosc.CatalogReference("VehicleCatalog", "$HostVehicle")
    # initialize entities
    entities = xosc.Entities()
    # initialize init
    init = xosc.Init()
    # stop trigger for storyboard
    storyboard_stoptrigger = xosc.ValueTrigger(
        "stop_simulation",
        0,
        xosc.ConditionEdge.none,
        xosc.SimulationTimeCondition(sim_time, xosc.Rule.greaterOrEqual),
        "stop",
    )
    # create story
    story = create_story("mystory")
    # create act
    act = create_act()

    # ego
    add_everything(ego_track, entities, cataref, init, act)

    # target
    bb = xosc.BoundingBox(1.8, 4.5, 1.5, 1.3, 0, 0.8)
    fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
    ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
    red_veh = xosc.Vehicle(
        "car_red", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10
    )

    red_veh.add_property_file("../models/car_red.osgb")
    red_veh.add_property("model_id", "2")

    for target_track_sampled in target_tracks_sampled:
        add_everything(target_track_sampled, entities, red_veh, init, act)

    # add act to story
    story.add_act(act)

    # add init, story, and stoptrigger into storyboard
    storyboard = xosc.StoryBoard(init, stoptrigger=storyboard_stoptrigger)
    storyboard.add_story(story)

    # create scenario
    sce = xosc.Scenario(
        name="myScenario",
        author="Chat2Scenario",
        parameters=paramdec,
        entities=entities,
        storyboard=storyboard,
        roadnetwork=road,
        catalog=catalog
    )
    
    # convert scenario to xml
    root_element = sce.get_element()
    xml_string = ET.tostring(root_element, encoding='unicode', method='xml')
    # prettify the xml string
    dom = minidom.parseString(xml_string)
    pretty_xml_string = dom.toprettyxml()
    # sce.write_xml(output_path)
    return pretty_xml_string


def create_time_pos_list(object_track, offset_frame):
    """
    create time position list

    Args:
        sim_time (double): Duration of simulation time.
        output_path (path): Path of output file.
    """
    time = []
    id = []
    x = []
    y = []
    orie = []
    width = []
    height = []
    xVel = []
    yVel = []
    ttc = []
    procedingId = []

    for i in object_track['frame']:
        t = (i - offset_frame)/30
        time.append(t)

    for i in range(len(object_track['frame'])):
        id.append(object_track.iloc[i]['id'])
        x.append(object_track.iloc[i]['x'])
        y.append(-object_track.iloc[i]['y'])
        orie.append(object_track.iloc[i]['orientation'])
        width.append(object_track.iloc[i]['width'])
        height.append(object_track.iloc[i]['height'])
        xVel.append(object_track.iloc[i]['xVelocity'])
        yVel.append(object_track.iloc[i]['yVelocity'])
        ttc.append(object_track.iloc[i]['ttc'])
        procedingId.append(object_track.iloc[i]['precedingId'])

    time_pos_list = {
        'time': time,
        'id': id,
        'x': x,
        'y': y,
        'orientation': orie,
        'width': width,
        'height': height,
        'xVel': xVel,
        'yVel': yVel,
        'ttc': ttc,
        'procedingId': procedingId
    }

    return pd.DataFrame(time_pos_list)


def check_data_match(dataset_option, dataset_load, reminder_holder):
    """
    Check if selected and uploaded datasets are matched

    Parameters:
    ----------
    Inputs:
        None
    Returns:
        
    -------
    """
    
    # expected dji format of "xx_tracks.csv"
    expected_dji_columns = ['frame', 'id', 'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity',
       'xAcceleration', 'yAcceleration', 'frontSightDistance',
       'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
       'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId',
       'leftFollowingId', 'rightPrecedingId', 'rightAlongsideId',
       'rightFollowingId', 'laneId', 'angle', 'orientation', 'yaw_rate ',
       'ego_offset']
    
    # expected Aachen format of "xx_tracks.csv"
    expected_aachen_column = ['frame', 'id', 'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity',
       'xAcceleration', 'yAcceleration', 'frontSightDistance',
       'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
       'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId',
       'leftFollowingId', 'rightPrecedingId', 'rightAlongsideId',
       'rightFollowingId', 'laneId']

    # if dji dataset
    if dataset_option == "AD4CHE":
        if dataset_load is None:
            reminder_holder.warning(":warning: Please upload dataset!")
        else:
            dji = pd.read_csv(dataset_load)
            if all(col in dji.columns for col in expected_dji_columns):
                return True
            else:
                reminder_holder.warning(":warning: Uploaded CSV file does not match to selected dataset!")
                return False

    # if aachen dataset
    elif dataset_option != "AD4CHE":
        if dataset_load is None:
            reminder_holder.warning(":warning: Please upload dataset!")
        else:
            aachen = pd.read_csv(dataset_load)
            if all(col in aachen.columns for col in expected_aachen_column):
                return True
            else:
                reminder_holder.warning(":warning: Uploaded CSV file does not match to selected dataset!")
                return False


def preview_number_of_searched_scenarios(dataset_load, metric_option, metric_suboption, reminder_holder, framerate, CA, target_value):
    """
    preview the number of searched scenarios before formally searching (computation time warning)

    Parameters:
    ----------
    Inputs:
        dataset_load (str or df): depends on the user metric selection
        metric_option (str): metric classification selected by user
        metric_suboption (str): concrete metric selected by user
        reminder_holder (st.empty()): empty holder for warning message
        metric_name (str): empty if metric is "ttc,dhw,thw"; depends on user input if "self-define"
        framerate (int): recording 
        CA_Input (list): a list contains tuples to express conflict area
        target_value (float): TTC target value
    Returns:
        searching_flag (bool): False/True to determine if continue the searching process
        tracks_sample (df): a dataframe containing the uploaded csv with downsample
        search_index_curr (str): index for searching desired scenario
        tracks_curr (df): a dataframe containing the uploaded csv
    ----------
    """
    reminder_holder.warning(f':thinking_face: Start to calculate {metric_suboption} for relevant vehicles...')

    # initialize variables
    search_index_curr = None
    tracks_curr = pd.read_csv(dataset_load)

    if metric_option == "Acceleration-Scale":
        if metric_suboption == "Deceleration to safety time (DST)":
            tracks_sample = DST(tracks_curr, framerate)
            search_index_curr = 'DST'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Required longitudinal acceleration (RLoA)":
            tracks_sample = RLoA(tracks_curr, framerate)
            search_index_curr = 'RLoA'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Required lateral acceleration (RLaA)":
            tracks_sample = RLaA(tracks_curr, framerate)
            search_index_curr = 'RLaA'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Required acceleration (RA)":
            tracks_sample = RA(tracks_curr, framerate)
            search_index_curr = 'RA'
            return True, tracks_sample, search_index_curr, tracks_curr
    elif metric_option == "Distance-Scale":
        if metric_suboption == "Proportion of Stopping Distance (PSD)":
            tracks_sample = PSD(tracks_curr, CA, framerate)
            search_index_curr = 'PSD'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Distance Headway (DHW)":
            tracks_sample = tracks_curr[tracks_curr['frame'] % framerate == 0].copy()
            search_index_curr = 'dhw'
            return True, tracks_sample, search_index_curr, tracks_curr
    elif metric_option == "Jerk-Scale":
        if metric_suboption == "Longitudinal jerk (LongJ)":
            tracks_sample = LongJ(tracks_curr, framerate)
            search_index_curr = 'xJerk'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Lateral jerk (LatJ)":
            tracks_sample = LatJ(tracks_curr, framerate)
            search_index_curr = 'yJerk'
            return True, tracks_sample, search_index_curr, tracks_curr
    elif metric_option == "Time-Scale":
        if metric_suboption == "Encroachment Time (ET)":
            tracks_sample = ET(tracks_curr, CA, framerate)
            search_index_curr = 'et'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Post-encroachment Time (PET)":
            tracks_sample = PET(tracks_curr, CA, framerate)
            search_index_curr = 'pet'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Potential Time To Collision (PTTC)":
            tracks_sample = PTTC(tracks_curr, framerate)
            search_index_curr = 'pttc'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time Exposed TTC (TET)":
            tracks_sample = TET(tracks_curr, framerate, target_value)
            search_index_curr = 'tet'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time Integrated TTC (TIT)":
            tracks_sample = TIT(tracks_curr, framerate, target_value)
            search_index_curr = 'tit'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time To Closest Encounter (TTCE)":
            tracks_sample = TTCE(tracks_curr, framerate)
            search_index_curr = 'ttce'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time To Brake (TTB)":
            tracks_sample = TTB(tracks_curr, framerate)
            search_index_curr = 'ttb'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time To Kickdown (TTK)":
            reminder_holder.warning(f':hourglass: Coming soon...')
        elif metric_suboption == "Time To Steer (TTS)":
            tracks_sample = TTS(tracks_curr, framerate)
            search_index_curr = 'tts'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time To Collision (TTC)":
            tracks_sample = tracks_curr[tracks_curr['frame'] % framerate == 0].copy()
            search_index_curr = 'ttc'
            return True, tracks_sample, search_index_curr, tracks_curr
        elif metric_suboption == "Time Headway (THW)":
            tracks_sample = tracks_curr[tracks_curr['frame'] % framerate == 0].copy()
            search_index_curr = 'thw'
            return True, tracks_sample, search_index_curr, tracks_curr
    elif metric_option == "Velocity-Scale":
        if metric_suboption == "delta_v":
            reminder_holder.warning(f':collision: No collision was identified in highD dataset.')

    return False, None, None, tracks_curr


def find_vehicle_data_within_start_end_frame(tracks_original, egoId, targetIds, initialFrame, finalFrame):
    """
    Find vehicle data from uploaded csv within the start and end frame

    Parameters:
    ----------
    Inputs:
        tracks_original (df): a dataframe contains the csv file that the user uploaded 
        egoId (int): ID of the ego vehicle that was found by function "mainFunctionScenarioIdentification" 
        targetIds (list): IDs of the target vehicle that was found by function "mainFunctionScenarioIdentification" [tgtID1, tgtID2, ...]
        initialFrame (int): initial frame when the scenario aligned with scenario description
        finalFrame (int): final frame when the scenario aligned with scenario description

    Returns:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (list): a list containing multiple dataframes that contains the target vehicle data within the initial and final frame
                           [df1, df2, ...]
    ----------
    """
    # Find ego vehicle data
    egoVehData = tracks_original[(tracks_original['id'] == egoId) & (tracks_original['frame'] >= initialFrame) \
                                 & (tracks_original['frame'] <= finalFrame)].reset_index(drop=True)
    
    tgtVehsData = []
    # Find target vehicle data
    for targetId in targetIds:
        tgtVehData = tracks_original[(tracks_original['id'] == targetId) & (tracks_original['frame'] >= initialFrame) \
                                     & (tracks_original['frame'] <= finalFrame)].reset_index(drop=True)
        tgtVehsData.append(tgtVehData)

    return egoVehData, tgtVehsData


def calc_metric_value_for_desired_scenario_segment(egoVehData, tgtVehData, reminder_holder, metric_option, metric_suboption, \
                                                   CA_Input, tracks_original, frame_rate, target_value):
    """
    Calculate metric value for each frame for desired scenario segment

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame
        reminder_holder: st.empty() for warning message
        metric_option (str): metric classification selected by user
        metric_suboption (str): concrete metric selected by user
        CA_Input (list): a list contains tuples to express conflict area
        tracks_original (df): a dataframe contains the csv file that the user uploaded 
        frame_rate (int): framerate of the recorded data
        target_value (float): TTC target value that is needed for TET/TIT/TTCE

    Returns:
        Check the returns of different metric calculation metric
        Acceleration-Scale & Distance-Scale & Jerk-Scale: metric_df ['frame', metric_values]
        Time-Scale: metric value (float)
        Velocity-Scale: "No collision found"
    ----------
    """
    # reminder_holder.warning(f':thinking_face: Start to calculate {metric_suboption} for relevant vehicles...')

    if metric_option == "Acceleration-Scale":
        if metric_suboption == "Deceleration to safety time (DST)":
            metric_df = DST(egoVehData, tgtVehData)
            return metric_df
        elif metric_suboption == "Required longitudinal acceleration (RLoA)":
            metric_df = RLoA(egoVehData, tgtVehData)
            return metric_df
        elif metric_suboption == "Required lateral acceleration (RLaA)":
            metric_df = RLaA(egoVehData, tgtVehData)
            return metric_df
        elif metric_suboption == "Required acceleration (RA)":
            metric_df = RA(egoVehData, tgtVehData)
            return metric_df
    elif metric_option == "Distance-Scale":
        if metric_suboption == "Proportion of Stopping Distance (PSD)":
            metric_df = PSD(egoVehData, tgtVehData, CA_Input)
            return metric_df
        elif metric_suboption == "Distance Headway (DHW)":
            egoId = egoVehData['id'].values[0]
            initialFrame = egoVehData['frame'].values[0]
            finalFrame = egoVehData['frame'].values[-1]
            dhwList = [np.nan]*len(egoVehData)
            filteredData = tracks_original[(tracks_original['id'] == egoId) & (tracks_original['frame'] >= initialFrame) & (tracks_original['frame'] <= finalFrame)]
            for i in len(dhwList):
                curr_dhw = filteredData['dhw'][i]
                dhwList.append(curr_dhw)
            metric_df = pd.DataFrame({
                'frame': egoVehData['frame'],
                'dhw': dhwList    
            })
            return metric_df
    elif metric_option == "Jerk-Scale":
        if metric_suboption == "Longitudinal jerk (LongJ)":
            metric_df = LongJ(egoVehData, frame_rate)
            return metric_df
        elif metric_suboption == "Lateral jerk (LatJ)":
            metric_df = LatJ(egoVehData, frame_rate)
            return metric_df
    elif metric_option == "Time-Scale":
        if metric_suboption == "Encroachment Time (ET)":
            ET_Value = ET(egoVehData, CA_Input, frame_rate)
            return ET_Value
        elif metric_suboption == "Post-encroachment Time (PET)":
            petValue = PET(egoVehData, tgtVehData, CA_Input, frame_rate)
            return petValue
        elif metric_suboption == "Potential Time To Collision (PTTC)":
            metric_df = PTTC(egoVehData, tgtVehData, frame_rate)
            return metric_df
        elif metric_suboption == "Time Exposed TTC (TET)":
            tetValue = TET(egoVehData, target_value)
            return tetValue
        elif metric_suboption == "Time Integrated TTC (TIT)":
            titValue = TIT(egoVehData, target_value)
            return titValue
        elif metric_suboption == "Time To Closest Encounter (TTCE)":
            ttce = TTCE(egoVehData, target_value, frame_rate)
            return ttce
        elif metric_suboption == "Time To Brake (TTB)":
            ttbValue = TTB(egoVehData, tgtVehData)
            return ttbValue
        elif metric_suboption == "Time To Kickdown (TTK)":
            reminder_holder.warning(f':hourglass: Coming soon...')
        elif metric_suboption == "Time To Steer (TTS)":
            ttsValue = TTS(egoVehData, tgtVehData)
            return ttsValue
        elif metric_suboption == "Time To Collision (TTC)":
            metric_df = pd.DataFrame({
                'frame': egoVehData['frame'],
                'ttc': egoVehData['ttc']
            })
            return metric_df
        elif metric_suboption == "Time Headway (THW)":
            metric_df = pd.DataFrame({
                'frame': egoVehData['frame'],
                'thw': egoVehData['thw']
            })
            return metric_df
    elif metric_option == "Velocity-Scale":
        if metric_suboption == "delta_v":
            reminder_holder.warning(f':collision: No collision was identified in highD dataset.')
    pass


def extract_fictive_ego_by_threshold(metric_threshold, tracks, dataset_option, search_index):
    """
    extract_frames_by_threshold

    Args:
        metric_threshold (double): threshold of selected metric
        tracks (df): a dataframe that contains trajectories of vehicles 
        metric_option (str): metric selected by user
        dataset_option (str): name of the seleted dataset
        metric_name (str): name of custom defined metric
    Output:
        selected_frames_list (list): a list, containing a lot of dataframes
    """

    # Initialize empty list
    selected_frames_list = []

    # Find all id and info
    search_threshold_min = metric_threshold[0]
    search_threshold_max = metric_threshold[1]

    # select data according to metric threshold
    selected_ids = tracks.loc[(tracks[search_index] >= search_threshold_min) & (tracks[search_index] <= search_threshold_max), 'id'].unique()
    selected_data = tracks[tracks['id'].isin(selected_ids)]
    
    # distinguish different datasets
    for id_value in selected_ids:
        # Save into csv
        id_data = selected_data[selected_data['id'] == id_value].reset_index(drop=True)

        # different frameRate for different dataset
        if dataset_option == "AD4CHE":
            frame_rate = 30
        else:
            frame_rate = 25
        id_data['time'] = (id_data['frame'] - id_data['frame'][0])/frame_rate
        
        # additional info "angle, orientation, yaw_rate, ego_offset"
        if dataset_option == "AD4CHE":
            columns = ['time', 'frame', 'id', 'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity',
        'xAcceleration', 'yAcceleration', 'frontSightDistance',
        'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
        'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId',
        'leftFollowingId', 'rightPrecedingId', 'rightAlongsideId',
        'rightFollowingId', 'laneId', 'angle', 'orientation', 'yaw_rate ',
        'ego_offset']
        else:
            columns = ['time', 'frame', 'id', 'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity',
        'xAcceleration', 'yAcceleration', 'frontSightDistance',
        'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
        'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId',
        'leftFollowingId', 'rightPrecedingId', 'rightAlongsideId',
        'rightFollowingId', 'laneId']
            
        id_data = id_data[columns]

        # Store in list
        selected_frames_list.append(id_data)

    for selected_frame in selected_frames_list:
        if selected_frame.empty:
            print("empty")

    return selected_frames_list 


def extract_fictive_target_by_ego(selected_egos, tracks, dataset_option):
    """
    extract_fictive_target_by_ego

    Args:
        selected_ego (list): a list, containing a lot of dataframes
        dataset_option (str): name of selected dataset
    
    Output:
        fictive_target_dict (dictionary): a dictionary [key: ego_id, value: fictive_target_list]
    """

    fictive_target_dict = {}
    
    for selected_ego in selected_egos:
        # initialize for each scenario
        fictive_target_list = []

        # Find target id
        precedingId = selected_ego['precedingId']
        ego_id = selected_ego['id'].unique()[0]
        target_ids = precedingId[precedingId != 0].unique()
        for target_id in target_ids:
            # Save into csv
            id_data = tracks[tracks['id'] == target_id].reset_index(drop=True)

            if dataset_option == "AD4CHE":
                frame_rate = 30
            else:
                frame_rate = 25
            id_data['time'] = (id_data['frame'] - selected_ego['frame'][0])/frame_rate

            # addtional info "angle, orientation, yaw_rate, ego_offset" are provided in AD4CHE
            if dataset_option == "AD4CHE":
                columns = ['time', 'frame', 'id', 'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity',
                'xAcceleration', 'yAcceleration', 'frontSightDistance',
                'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
                'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId',
                'leftFollowingId', 'rightPrecedingId', 'rightAlongsideId',
                'rightFollowingId', 'laneId', 'angle', 'orientation', 'yaw_rate ',
                'ego_offset']
            else:
                columns = ['time', 'frame', 'id', 'x', 'y', 'width', 'height', 'xVelocity', 'yVelocity',
                'xAcceleration', 'yAcceleration', 'frontSightDistance',
                'backSightDistance', 'dhw', 'thw', 'ttc', 'precedingXVelocity',
                'precedingId', 'followingId', 'leftPrecedingId', 'leftAlongsideId',
                'leftFollowingId', 'rightPrecedingId', 'rightAlongsideId',
                'rightFollowingId', 'laneId']
            id_data = id_data[columns]

            # Store in list
            fictive_target_list.append(id_data) 
        
        fictive_target_dict[ego_id] = fictive_target_list

    return fictive_target_dict


def align_ego_and_target(selected_egos, selected_targets, dataset_option):
    """
    extract_fictive_target_by_ego

    Args:
        selected_ego (list): a list, containing a lot of dataframes
        selected_target (dictionary): a dictionary [key: ego_id, value: fictive_target_list]
        dataset_option (str): name of selected dataset
    Output:
        fictive_ego_list (list)
        fictive_target_dict (dictionary): a dictionary [key: ego_id, value: fictive_target_list]
    """
    if dataset_option == "AD4CHE":
        frame_rate = 30
    else:
        frame_rate = 25

    fictive_ego_list = []
    fictive_target_dict = {}

    for selected_ego in selected_egos:
        # ego id
        ego_id = selected_ego['id'][0]

        # ego start and end frame
        ego_start_frame = selected_ego['frame'][0]
        ego_end_frame = selected_ego['frame'].iloc[-1]

        # target start and end frame
        target_start_frame = float('-inf')
        target_end_frame = float('inf')

        selected_target = selected_targets[ego_id]
        for target in selected_target:
            # This step is suitable for TTC; DHW; THW. But not for metric need to be recalculated. 
            # --> 
            # These calculation demands downsample
            # skip too short life time target (less than 1 second)
            tgt_len = target['frame'].iloc[-1] - target['frame'][0]
            if tgt_len < frame_rate:
                continue

            # the latest start frame
            curr_target_start_frame = target['frame'][0]
            if curr_target_start_frame > target_start_frame:
                target_start_frame = curr_target_start_frame
            
            # the earliest end frame
            curr_target_end_frame = target['frame'].iloc[-1]
            if curr_target_end_frame < target_end_frame:
                target_end_frame = curr_target_end_frame

        # calculate scenario start and end frame
        scenario_start_frame = max(ego_start_frame, target_start_frame)
        scenario_end_frame = min(ego_end_frame, target_end_frame)

        # save aligned ego and target
        ego_aligned = selected_ego[(selected_ego['frame'] >= scenario_start_frame) & (selected_ego['frame'] <= scenario_end_frame)].reset_index(drop=True)
        ego_aligned['time'] = (ego_aligned['frame'] - scenario_start_frame)/frame_rate

        # skip the empty ego_aligned 
        if not ego_aligned.empty:
            fictive_target_list = []
            for target in selected_target:
                target_aligned = target[(target['frame'] >= scenario_start_frame) & (target['frame'] <= scenario_end_frame)].reset_index(drop=True)
                target_aligned['time'] = (target_aligned['frame'] - scenario_start_frame)/frame_rate # target_aligned could also be empty   
                if len(ego_aligned) == len(target_aligned):
                    fictive_target_list.append(target_aligned) 
            
            if len(fictive_target_list) > 0:
                fictive_ego_list.append(ego_aligned)
                fictive_target_dict[ego_id] = fictive_target_list

    return fictive_ego_list, fictive_target_dict


def noise_reduction(ori_dataframe, target_sample_rate, frame_rate):
    """
    noise_reduction/downsample

    Args:
        ori_dataframe (dataframe): the original dataframe, containing all vehicle information
        target_sample_rate (Hz): desired sampling rate
        frame_rate (Hz): Hertz of recorded video
    Output:
        modi_dataframe (dataframe): dataframe with reduced noise.
    """
    step_size = int(frame_rate/target_sample_rate)
    modi_dataframe = ori_dataframe[::step_size].reset_index(drop=True)

    return modi_dataframe


def search_scenario(tracks, metric_threshold, dataset_option, search_index, metric_name=""):
    """
    Search and downsample scenario from dataset when metric is NOT self-define 

    Parameters:
    ----------
    Inputs:
        input_path (str or dataframe): str: path of input data; df: a dataframe containing the self-defined metric value 
        metric_threshold (float): time-to-collision threshold to filter scenarios from dataset
        metric_option (str): selected metric by user 
        metric_name (str): name of the define metric
        dataset_option (str): name of the selected dataset
    Returns:
        fictive_ego_list_sampled (list): a list containing all fictive ego vehicles in format of dataframe
        fictive_target_dicts_sampled (dictionary): a dictionary containing all target vehicles, each ego
        vehicle corresponds to a list that contains several target vehicles in format of dataframe.
    ----------
    """

    # 2. Specify criticality metric threshold: currently using "ttc", [minDHW; # minTHW; # minTTC (etc.)]

    # 3. Extract fictive ego according to threshold 
    selected_ego = extract_fictive_ego_by_threshold(metric_threshold, tracks, dataset_option, search_index)

    # 4. Extract fictive target according to ego
    selected_target = extract_fictive_target_by_ego(selected_ego, tracks, dataset_option)

    # 5. Align the time of ego and target
    fictive_ego_list, fictive_target_dict = align_ego_and_target(selected_ego, selected_target, dataset_option)
    
    return fictive_ego_list, fictive_target_dict


def generate_xosc(input_path, output_path, metric_threshold, metric_option, dataset_option):
    """
    Generate OpenSCENARIO files 

    Parameters:
    ----------
    Inputs:
        input_path (str): path of input data 
        output_path: path of output data 
        metric_threshold: time-to-collision threshold to filter scenarios from dataset 
        dataset_option (str): dataset option selected by user
    Returns:
        ------
    ----------
    """
    data = pd.read_csv(input_path)
    fictive_ego_list_sampled, fictive_target_dicts_sampled = search_scenario(data, metric_threshold, metric_option, dataset_option)
    # Initialize progress bar
    progress_bar_xosc = st.progress(0)
    idx_progress_xosc = 0
    # Generate xosc for each ego vehicle
    for fictive_ego_sampled in fictive_ego_list_sampled:
        sim_time = len(fictive_ego_sampled)  
        target_tracks_sampled = fictive_target_dicts_sampled[fictive_ego_sampled['id'][0]]
        output_path_file = output_path + f"\\scenario_{fictive_ego_sampled['id'][0]}.xosc"
        xosc_generation(sim_time, output_path_file, fictive_ego_sampled, target_tracks_sampled)
        # Update progress bar
        time.sleep(1)
        progress_bar_xosc.progress((idx_progress_xosc + 1)/len(fictive_ego_list_sampled))
        idx_progress_xosc += 1


def if_scenario_within_threshold(metric_value_res, metric_threshold):
    """
    Judge if the metric value of searched scenario is within the desired threshold

    Parameters:
    ----------
    Inputs:
        metric_value_res (df/float): calculated result from function "calc_metric_value_for_desired_scenario_segment"
        metric_threshold (tuple): two floats representing "maximum value" and "minimum value" [metric_threshold = (min_value, max_value)]

    Returns:
        bool value (True/False): bool value representing if the scenario can meet the requirements of threshold
    ----------
    """
    # If the metric_value_res in the format of "dataframe"
    if isinstance(metric_value_res, pd.DataFrame):
        metric_name = metric_value_res.columns[1]
        metric_values = metric_value_res[metric_name]

        # Minimum and maximum of threshold
        min_threshold = metric_threshold[0]
        max_threshold = metric_threshold[1]

        return ((metric_values >= min_threshold) & (metric_values <= max_threshold)).any()

    # If the metric_value_res in the format of "float"
    else:
        if metric_value_res >= metric_threshold[0] and metric_value_res <= metric_threshold[1]:
            return True
        else:
            return False