import pandas as pd
import pickle
import streamlit as st
# from utils.helper_original_scenario import *

def intersection_judge(list1, list2):
    """
    Judge if two lists have intersections

    Parameters:
    -----------
    Inputs:
    list1 (list): A list contains two values corresponding to a lower bound and a upper bound
    list2 (list): A list contains two values corresponding to a lower bound and a upper bound

    Returns:
    list: begin and end frame of the intersected
    ----------
    """
    if len(list1) == 0 or len(list2) == 0:
        return []

    a, b = list1
    c, d = list2

    if max(a, c) <= min(b, d):
        return [max(a, c), min(b, d)]
    else:
        return []


def pos_calc(laneDiff, ego_drive_direction, delta_x_tgt_ego, req_tgt_type):
    """
    Target vehicle position w.r.t. ego vehicle calculation

    Parameters:
    -----------
    Inputs:
        laneDiff (int): lane ID difference between the target vehicle and the ego vehicle [tgt_laneId - ego_laneId]
        ego_drive_direction (int): the difference between the end and start position of ego vehicle [ego_end_x - ego_start_x] for driving direction claculation
        delta_x_tgt_ego (int): the difference between the target vehicle position and ego vehicle position [tgt_x - ego_x] start/end

    Returns:
        lane position (str): target vehicle position w.r.t. the ego vehicle 
    ----------
    """
    '''
    # same lane
    if abs(laneDiff) == 0:
        # driving direction "along" x-axis
        if ego_drive_direction > 0:
            if delta_x_tgt_ego > 0:
                return 'front'
            elif delta_x_tgt_ego < 0:
                return 'behind'
        # driving direction "against" x-axis
        else:
            if delta_x_tgt_ego < 0:
                return 'front'
            elif delta_x_tgt_ego > 0:
                return 'behind'
    # adjacent lane
    elif abs(laneDiff) == 1:
        # driving direction "along" x-axis
        if ego_drive_direction > 0:
            if laneDiff == 1:
                return 'right adjacent lane'
            elif laneDiff == -1:
                return 'left adjacent lane'
        # driving direction "against" x-axis
        else:
            if laneDiff == 1:
                return 'left adjacent lane'
            elif laneDiff == -1:
                return 'right adjacent lane'
    # lane next to adjacent lane
    elif abs(laneDiff) == 2:
        # driving direction "along" x-axis
        if ego_drive_direction > 0:
            if laneDiff == 2:
                return 'lane next to right adjacent lane'
            elif laneDiff == -2:
                return 'lane next to left adjacent lane'
        # driving direction "against" x-axis
        else:
            if laneDiff == 2:
                return 'lane next to left adjacent lane'
            elif laneDiff == -2:
                return 'lane next to right adjacent lane'
    '''
    def same_lane_position(delta_x):
        if delta_x > 0:
            return 'front'
        elif delta_x < 0:
            return 'behind'
    def same_lane_position_2(delta_x):
        if delta_x > 0:
            return 'lead'
        elif delta_x < 0:
            return 'rear'
    # Handle different target types
    if req_tgt_type == 'same lane':
        if abs(laneDiff) == 0:
            if ego_drive_direction > 0:
                return same_lane_position(delta_x_tgt_ego)
            else:
                return same_lane_position(-delta_x_tgt_ego)
    
    elif req_tgt_type == 'adjacent lane':
        if abs(laneDiff) == 1:
            if ego_drive_direction > 0:
                if laneDiff == 1:
                    return 'right adjacent lane'
                elif laneDiff == -1:
                    return 'left adjacent lane'
            else:
                if laneDiff == 1:
                    return 'left adjacent lane'
                elif laneDiff == -1:
                    return 'right adjacent lane'
    
    elif req_tgt_type == 'lane next to adjacent lane':
        if abs(laneDiff) == 2:
            if ego_drive_direction > 0:
                if laneDiff == 2:
                    return 'lane next to right adjacent lane'
                elif laneDiff == -2:
                    return 'lane next to left adjacent lane'
            else:
                if laneDiff == 2:
                    return 'lane next to left adjacent lane'
                elif laneDiff == -2:
                    return 'lane next to right adjacent lane'
    
    elif req_tgt_type == 'lead':
        if ego_drive_direction > 0:
            if laneDiff == 0:
                return same_lane_position_2(delta_x_tgt_ego)
            elif laneDiff == 1 and delta_x_tgt_ego > 0:
                return 'right lead'
            elif laneDiff == -1 and delta_x_tgt_ego > 0:
                return 'left lead'
        else:
            if laneDiff == 0:
                return same_lane_position_2(-delta_x_tgt_ego)
            elif laneDiff == 1 and delta_x_tgt_ego < 0:
                return 'left lead'
            elif laneDiff == -1 and delta_x_tgt_ego < 0:
                return 'right lead'

    elif req_tgt_type == 'rear':
        if ego_drive_direction > 0:
            if laneDiff == 0:
                return same_lane_position_2(delta_x_tgt_ego)
            elif laneDiff == 1 and delta_x_tgt_ego < 0:
                return 'right rear'
            elif laneDiff == -1 and delta_x_tgt_ego < 0:
                return 'left rear'
        else:
            if laneDiff == 0:
                return same_lane_position_2(-delta_x_tgt_ego)
            elif laneDiff == 1 and delta_x_tgt_ego > 0:
                return 'left rear'
            elif laneDiff == -1 and delta_x_tgt_ego > 0:
                return 'right rear'
            
def find_start_end_frame_of_latAct(curr_latActs, req_latAct):
    """
    Find the start and the end frame from current lateral activity based on the required activity

    Parameters:
    -----------
    Inputs:
        curr_latActs (df): a dataframe containing columns to describe the activities 
        [frame, id, LateralActivity, laneId, x, y]
        req_latAct (str): required lateral activity

    Returns:
        latActFram (list): a list containing two values, representing the start and end frames.
        [each of sublist contains two values representing the begining and end frame of required lateral activities]
    ----------
    """
    latActFram = []
    for index, row in curr_latActs.iterrows(): 
        if row['LateralActivity'] == req_latAct:
            begFrame = row['frame']
            endFrame = curr_latActs.iloc[index+1]['frame']
            latActFram.append(begFrame)
            latActFram.append(endFrame)
            break # Note in one scenario there could be multiple lateral activities, only consider the first 
    
    return latActFram


def find_start_end_frame_of_lonAct(curr_lonActs, req_lonAct):
    """
    Find the start and the end frame from current longitudinal activity based on the required activity

    Parameters:
    -----------
    Inputs:
        curr_lonActs (df): a dataframe containing columns to describe the activities 
        [frame, id, LongitudinalActivity, laneId, x, y]
        req_lonAct (str): required lateral activity

    Returns:
        lonActFram (list): a list containing two values, representing the start and end frames.
        [each of sublist contains two values representing the begining and end frame of required lateral activities]
    ----------
    """
    lonActFram = []
    for index, row in curr_lonActs.iterrows(): 
        if row['LongitudinalActivity'] == req_lonAct:
            begFrame = row['frame']
            endFrame = curr_lonActs.iloc[index+1]['frame']
            lonActFram.append(begFrame)
            lonActFram.append(endFrame)
            break # Note in one scenario there could be multiple lateral activities, only consider the first 
    
    return lonActFram


def get_activity_from_LLM_response(LLM_response):
    """
    refine the activity from LLM response

    Parameters:
    -----------
    Inputs:
        LLM_response (dict): a dictionary containing LLM response

    Returns:
        req_ego_latAct (str): required lateral activity of ego vehicle
        req_ego_lonAct (str): required longitudinal activity of ego vehicle 
        req_tgt_startPos (str): required start position of target vehicle 
        req_tgt_endPos (str): required end position of target vehicle 
        req_tgt_latAct (str): required lateral activity of target vehicle 
        req_tgt_longAct (str): required longitudinal activity of target vehicle
    ----------
    """

    ## Ego 
    req_ego_latAct = LLM_response['Ego Vehicle']['Ego lateral activity'][0]
    req_ego_lonAct = LLM_response['Ego Vehicle']['Ego longitudinal activity'][0]

    ## Target
    # Target start position
    tgt_startPos = LLM_response['Target Vehicle #1']['Target start position']
    start_item = list(tgt_startPos.items())[0]
    req_tgt_startPos = start_item[1][0]
    req_tgt_startPos_type = start_item[0]
    # Target end position
    tgt_endPos = LLM_response['Target Vehicle #1']['Target end position']
    end_item = list(tgt_endPos.items())[0]
    req_tgt_endPos = end_item[1][0]
    req_tgt_endPos_type = end_item[0]

    # Target lateral and longitudinal activity
    req_tgt_latAct = LLM_response['Target Vehicle #1']['Target behavior']['target lateral activity'][0]
    req_tgt_longAct = LLM_response['Target Vehicle #1']['Target behavior']['target longitudinal activity'][0]

    return req_ego_latAct, req_ego_lonAct, req_tgt_startPos, req_tgt_endPos, req_tgt_latAct, req_tgt_longAct, req_tgt_startPos_type, req_tgt_endPos_type


def mainFunctionScenarioIdentification(tracks_36, key_label, latActDict, longActDict, interactIdDict, progress_bar):
    """
    main function to search the desired scenarios

    Parameters:
    -----------
    Inputs:
        track_36 (df): track read by pd.read_csv()
        key_label (dict): LLM response
        latActDict (dict): [key: egoID; value: df['frame', 'id', 'LateralActivity', 'lateral', 'x', 'y']]
        longActDict (dict): [key: egoID; value: df['frame', 'id', 'LongitudinalActivity', 'lateral', 'x', 'y']]
        interactIdDict (dict): [key: id; value: ID of interacting targets] 
        progress_bar (st.progress(0)): initialize the progress bar

    Returns:
        scenarioLists (list): a list contains multiple sublist in the format of [egoID, [tgtID], begFrame, endFrame]
    ----------
    """

    req_ego_latAct, req_ego_lonAct, req_tgt_startPos, req_tgt_endPos, \
    req_tgt_latAct, req_tgt_longAct , req_tgt_startPos_type, req_tgt_endPos_type = get_activity_from_LLM_response(key_label)

    scenarioLists = []
    ## Search from vehicle activity file: the following conditions should be judged:
    # 1. Ego lateral activity
    # 2. Target lateral activity
    # 3. Target position
    for key in latActDict:
        scenarioList = []

        # Current ego vehicle and interacting targets
        curr_ego = key # current ego id
        curr_ego_latActs = latActDict[curr_ego] # current ego lateral activities
        curr_ego_lonActs = longActDict[curr_ego] # current ego longitudinal activities
        curr_interact_tgts = interactIdDict[curr_ego] # targets interacting with current ego

        # Judge the ego vehicle lateral activity
        if req_ego_latAct not in curr_ego_latActs['LateralActivity'].values:
            continue
        egoLatActFram = find_start_end_frame_of_latAct(curr_ego_latActs, req_ego_latAct)
        
        tgt_list = []
        for curr_interact_tgt in curr_interact_tgts:

            # Judge the target vehicle lateral activity
            curr_interact_tgt_latAct = latActDict[curr_interact_tgt]
            if req_tgt_latAct not in curr_interact_tgt_latAct['LateralActivity'].values:
                continue
            tgtLatActFram = find_start_end_frame_of_latAct(curr_interact_tgt_latAct, req_tgt_latAct)
            
            # Find the intersection between ego and target frames
            inter = intersection_judge(egoLatActFram, tgtLatActFram)
            if len(inter) == 0:
                continue

            # Current ego info
            curr_ego_start_row = tracks_36[(tracks_36['id'] == curr_ego) & (tracks_36['frame'] == inter[0])].reset_index(drop=True)
            curr_ego_end_row = tracks_36[(tracks_36['id'] == curr_ego) & (tracks_36['frame'] == inter[1])].reset_index(drop=True)
            curr_ego_life = tracks_36[(tracks_36['id'] == curr_ego)& tracks_36['frame'].between(inter[0], inter[1])].reset_index(drop=True)
            # Current target info
            curr_tgt_start_row = tracks_36[(tracks_36['id'] == curr_interact_tgt) & (tracks_36['frame'] == inter[0])].reset_index(drop=True)
            curr_tgt_end_row = tracks_36[(tracks_36['id'] == curr_interact_tgt) & (tracks_36['frame'] == inter[1])].reset_index(drop=True)
            
            # lane ID
            curr_ego_start_lane = curr_ego_start_row['laneId'][0]
            curr_ego_end_lane = curr_ego_end_row['laneId'][0]
            curr_tgt_start_lane = curr_tgt_start_row['laneId'][0]
            curr_tgt_end_lane = curr_tgt_end_row['laneId'][0]

            # Calculate the target vehicle position at start  
            ego_drive_direction = curr_ego_end_row['x'][0] - curr_ego_start_row['x'][0]
            delta_x_tgt_ego_start = curr_tgt_start_row['x'][0] - curr_ego_start_row['x'][0]
            laneDiffStart = curr_tgt_start_lane - curr_ego_start_lane
            curr_tgt_pos_start = pos_calc(laneDiffStart, ego_drive_direction, delta_x_tgt_ego_start, req_tgt_startPos_type)

            # If current target vehicle was not once the precedingId of the current ego vehicle, then skip
            if curr_interact_tgt not in curr_ego_life['precedingId'].values:
                continue

            if curr_tgt_pos_start == req_tgt_startPos: # Judge the start position
                # Calculate the target vehicle position at end
                delta_x_tgt_ego_end = curr_tgt_end_row['x'][0] - curr_ego_end_row['x'][0]
                laneDiffEnd = curr_tgt_end_lane - curr_ego_end_lane
                curr_tgt_pos_end = pos_calc(laneDiffEnd, ego_drive_direction, delta_x_tgt_ego_end, req_tgt_endPos_type)
                if curr_tgt_pos_end == req_tgt_endPos: # Judge the end position
                    # If longitudinal activity is omitted, get current targetID and BegFrame, EndFrame
                    if req_ego_lonAct ==  'NA' and req_tgt_longAct == 'NA':
                        tgt_list.append(curr_interact_tgt)
                        interFinal = []
                        interFinal.append(inter[0])
                        interFinal.append(inter[1])
                        continue

                    # Judge the ego vehicle longitudinal activity: if 'NA', omit longitudinal
                    if req_ego_lonAct not in curr_ego_lonActs['LongitudinalActivity'].values:
                            continue
                    # Judge the target vehicle longitudinal activity: 
                    curr_tgt_lonAct = longActDict[curr_interact_tgt]
                    if req_tgt_longAct not in curr_tgt_lonAct['LongitudinalActivity'].values:
                        continue
                    egoLonActFram = find_start_end_frame_of_lonAct(curr_ego_lonActs, req_ego_lonAct)
                    tgtLonActFram = find_start_end_frame_of_lonAct(curr_tgt_lonAct, req_tgt_longAct)
                    # intersected frames of longitudinal activity of ego and target
                    interLon = intersection_judge(egoLonActFram, tgtLonActFram)
                    if len(interLon) != 0:
                        # Intersected frames of lateral and longitudinal
                        interFinal = intersection_judge(inter, interLon)
                        if len(interFinal) != 0:
                            tgt_list.append(curr_tgt_start_row['id'][0])
                            break
        
        if len(tgt_list) != 0:
            scenarioList.append(curr_ego)
            scenarioList.append(tgt_list)
            scenarioList.append(interFinal[0])
            scenarioList.append(interFinal[1])

        # Append the scenario list into another list
        if len(scenarioList) != 0:
            scenarioLists.append(scenarioList)
    
    return scenarioLists


# if __name__ == "__main__":


#     ## option
#     selected_opts = "xosc"
#     output_path = "C:/Users/ilovetug/Downloads"

#     # Quantitive evaluation of framework
#     # 1. following scenario (ignore the longitudinal activity)
#     following = {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'same lane': ['front']}, 
#     'Target end position': {'same lane': ['front']}, 
#     'Target behavior': {'target longitudinal activity': ['NA'], 
#     'target lateral activity': ['follow lane']}}}

#     # 2. cut-in scenario (ignore the longitudinal activity; left & right)
#     cut_in_left = {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'adjacent lane': ['left adjacent lane']}, 
#     'Target end position': {'same lane': ['front']}, 
#     'Target behavior': {'target longitudinal activity': ['NA'], 
#     'target lateral activity': ['lane change right']}}}

#     cut_in_right = {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'adjacent lane': ['right adjacent lane']}, 
#     'Target end position': {'same lane': ['front']}, 
#     'Target behavior': {'target longitudinal activity': ['NA'], 
#     'target lateral activity': ['lane change left']}}}

#     # 3. cut-out left 
#     cut_out_left = {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'same lane': ['front']}, 
#     'Target end position': {'adjacent lane': ['left adjacent lane']}, 
#     'Target behavior': {'target longitudinal activity': ['NA'], 
#     'target lateral activity': ['lane change left']}}}

#     cut_out_right = {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'same lane': ['front']}, 
#     'Target end position': {'adjacent lane': ['right adjacent lane']}, 
#     'Target behavior': {'target longitudinal activity': ['NA'], 
#     'target lateral activity': ['lane change right']}}}

#     # 4. left evasion
#     left_evasion = {'Ego Vehicle': {'Ego longitudinal activity': ['NA'], 
#     'Ego lateral activity': ['lane change left']}, 
#     'Target Vehicle #1': {'Target start position': {'same lane': ['front']}, 
#     'Target end position': {'adjacent lane': ['right adjacent lane']}, 
#     'Target behavior': {'target longitudinal activity': ['NA'], 
#     'target lateral activity': ['follow lane']}}}

#     right_evasion = {'Ego Vehicle': {'Ego longitudinal activity': ['keep velocity'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'same lane': ['behind']}, 
#     'Target end position': {'adjacent lane': ['right']}, 
#     'Target behavior': {'target longitudinal activity': ['acceleration'], 
#     'target lateral activity': ['lane change right']}}}

#     ## LLM Response
#     key_label = {'Ego Vehicle': {'Ego longitudinal activity': ['keep velocity'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'adjacent lane': ['left adjacent lane']}, 
#     'Target end position': {'same lane': ['front']}, 
#     'Target behavior': {'target longitudinal activity': ['acceleration'], 
#     'target lateral activity': ['lane change right']}}}

#     example = {'Ego Vehicle': {'Ego longitudinal activity': ['keep velocity'], 
#     'Ego lateral activity': ['follow lane']}, 
#     'Target Vehicle #1': {'Target start position': {'adjacent lane': ['left adjacent lane']}, 
#     'Target end position': {'same lane': ['front']}, 
#     'Target behavior': {'target longitudinal activity': ['acceleration'], 
#     'target lateral activity': ['lane change right']}}}


#     # Original track
#     oriTracksDf = pd.read_csv("C:\\PhD\\Dataset\\highD\\data\\36_tracks.csv")

#     ## Vehicle activity
#     with open("C:\\PhD\\0_scenario_generation_IEEEIV_PaperAccepted\\Vehicle_Activity\\track_36_act\\interactIdDict.pickle", 'rb') as handle:
#         interactIdDict = pickle.load(handle)
#     latActDict = pd.read_pickle("C:\\PhD\\0_scenario_generation_IEEEIV_PaperAccepted\\Vehicle_Activity\\track_36_act\\latActDict.pickle", compression=None)
#     # with open("C:\\PhD\\0_scenario_generation_IEEEIV_PaperAccepted\\Vehicle_Activity\\track_36_act\\latActDict.pickle", 'rb') as handle:
#     #     latActDict = pickle.load(handle)
#     longActDict = pd.read_pickle("C:\\PhD\\0_scenario_generation_IEEEIV_PaperAccepted\\Vehicle_Activity\\track_36_act\\longActDict.pickle", compression=None)
#     # with open("C:\\PhD\\0_scenario_generation_IEEEIV_PaperAccepted\\Vehicle_Activity\\track_36_act\\longActDict.pickle", 'rb') as handle:
#     #     longActDict = pickle.load(handle)

#     progress_bar = st.progress(0)
#     scenarioList = mainFunctionScenarioIdentification(oriTracksDf, example, latActDict, longActDict, interactIdDict, progress_bar)
    
    # numScenario = len(scenarioLists)
    # print(f'{numScenario} scenarios are found!')
    # print(scenarioLists)

    # # Saving the list
    # with open('.\pre_cutout_left.pkl', 'wb') as file:
    #     pickle.dump(scenarioLists, file)

#     # xosc_index = 1
#     # for desired_scenario in scenarioLists:
#     #     print(desired_scenario)

#     #     # Get the ego vehicle information
#     #     egoVehID = desired_scenario[0]
#     #     egoVehTraj = oriTracksDf[oriTracksDf['id']==egoVehID].reset_index(drop=True)

#     #     # Find intersection of frames with the current target vehicle
#     #     common_frames = set(egoVehTraj['frame'])
#     #     tgtVehIDs = desired_scenario[1]
#     #     tgtVehTraj_common = []
#     #     for tgtVehID in tgtVehIDs:
#     #         tgtVehTraj = oriTracksDf[oriTracksDf['id'] == tgtVehID].reset_index(drop=True)
#     #         common_frames = common_frames.intersection(set(tgtVehTraj['frame']))
            
#     #     # Now common_frames contains only frames that are common across all target vehicles and the ego vehicle
#     #     egoVehTraj_common = egoVehTraj[egoVehTraj['frame'].isin(common_frames)].copy().reset_index(drop=True)

#     #     # Ego vehicle trajectory post-processing: 1) add time; 2) move position; 3) flip y 
#     #     ego_time = (egoVehTraj_common['frame'] - egoVehTraj_common['frame'].iloc[0])/25
#     #     egoVehTraj_common['time'] = ego_time
#     #     egoVehTraj_common['x'] = egoVehTraj_common['x'] + 0.5*egoVehTraj_common['width']
#     #     egoVehTraj_common['y'] = egoVehTraj_common['y'] + 0.5*egoVehTraj_common['height']
#     #     egoVehTraj_common['y'] = -egoVehTraj_common['y']

#     #     tgtVehTrajs_common = []
#     #     # Get common trajectory data for all target vehicles
#     #     for tgtVehID in tgtVehIDs:
#     #         tgtVehTraj = oriTracksDf[oriTracksDf['id'] == tgtVehID]
#     #         tgtVehTraj_common = tgtVehTraj[tgtVehTraj['frame'].isin(common_frames)].copy().reset_index(drop=True)
#     #         # Target vehicle trajectory post-processing: 1) ad "time"; 2) move position; 3) flip y value  
#     #         tgt_time = (tgtVehTraj_common['frame'] - tgtVehTraj_common['frame'].iloc[0])/25
#     #         tgtVehTraj_common['time'] = tgt_time
#     #         tgtVehTraj_common['x'] = tgtVehTraj_common['x'] + 0.5*tgtVehTraj_common['width']
#     #         tgtVehTraj_common['y'] = tgtVehTraj_common['y'] + 0.5*tgtVehTraj_common['height']
#     #         tgtVehTraj_common['y'] = -tgtVehTraj_common['y']
#     #         tgtVehTrajs_common.append(tgtVehTraj_common)
            

#     #     # Create input for "xosc_generation" and "IPG_CarMaker_text_generation"
#     #     sim_time = len(egoVehTraj_common)/25
#     #     output_path_xosc = output_path + '\\' + f'Chat2Scenario_xosc_{xosc_index}.xosc'
#     #     output_path_text = output_path + '\\' + f'Chat2Scenario_text_{xosc_index}.txt'
#     #     ego_track = egoVehTraj_common
#     #     tgt_tracks = tgtVehTrajs_common
        
#     #     if selected_opts == "xosc":
#     #         xosc_generation(sim_time, output_path_xosc, ego_track, tgt_tracks)
        
#     #     xosc_index += 1
        
