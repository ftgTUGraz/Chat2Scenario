"""
Author: Yongqi Zhao
Date Created: 2023-11-28
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
Reference: https://criticality-metrics.readthedocs.io/en/latest/
"""
from shapely.geometry import Point, Polygon, LineString
import numpy as np
import math
import sympy as sp
import pandas as pd
from scipy.spatial.distance import euclidean
import random
from scipy.optimize import bisect

"""
current problem: computation time --> how to reduce the computation time --> search process
"""

def ET(egoVehData, CA, framerate):
    """
    Encroachment Time 

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        CA (list): a list of tuple to represent "conflict area" e.g., CA =  [(x1, y1), (x2, y2), (x3, y3), ... (xn, yn)]
        framerate (Hz): frame rate of the dataset

    Returns:
        ET_current (float): a float number that represents the ET 
    ----------
    """
    # define conflict area using polygon
    conflict_area = Polygon(CA)
    
    # function to check if a point is inside the polygon
    def is_point_in_polygon(x, y):
        point = Point(x, y)
        return conflict_area.contains(point)

    # Convert the 'x' and 'y' columns into a list of Points
    points = [Point(xy) for xy in zip(egoVehData['x'], egoVehData['y'])]
    curr_traj = LineString(points)

    if not curr_traj.intersects(conflict_area):
        return np.nan
    else:
        frame_entry = None
        frame_exit = None
        counter = 1
        # iterate states of current id
        for i, state in egoVehData.iterrows():
            x = state['x']
            y = state['y']
            # get entry and exit frame
            if is_point_in_polygon(x, y) and counter==1: # entry time
                frame_entry = state['frame']
                counter += 1
            elif not is_point_in_polygon(x, y) and counter==2: # exit time
                frame_exit = state['frame']
                counter += 1
            # calculate ET
            if frame_entry != None and frame_exit != None:
                ET_current = (frame_exit-frame_entry)/framerate
                return ET_current

                    
def PET(egoVehData, tgtVehData, CA, frame_rate):
    """
    Post-encroachment Time 

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame
        CA (list): a list of tuple to represent "conflict area" e.g., CA =  [(x1, y1), (x2, y2), (x3, y3), ... (xn, yn)]
        framerate (Hz): frame rate of the dataset

    Returns:
        tracks_sample (df): a dataframe including PET besides original info    
    ----------
    Assuming A1 leaves Conflict Area (CA) before or at the time A2 enters it     
    ----------
    """
    # define conflict area using polygon
    conflict_area = Polygon(CA)

    # function to check if a point is inside the polygon
    def is_point_in_polygon(x, y):
        point = Point(x, y)
        return conflict_area.contains(point)
    
    # Check if the ego and target vehicle cross with CA
    egoPoints = [Point(xy) for xy in zip(egoVehData['x'], egoVehData['y'])]
    egoLine = LineString(egoPoints)
    tgtPoints = [Point(xy) for xy in zip(tgtVehData['x'], tgtVehData['y'])]
    tgtLine = LineString(tgtPoints)
    if egoLine.intersects(conflict_area) and tgtLine.intersects(conflict_area):
        # search the time when ego vehicle exits the polygon
        pre_point_in = None
        t_exit = None
        follow_Id = None
        for index, ego_row in egoVehData.iterrows():
            curr_point = Point(ego_row['x'], ego_row['y'])
            is_inside = conflict_area.contains(curr_point)
            if pre_point_in and not is_inside:
                # time when the vehicle exit
                t_exit = ego_row['frame']
                break
            pre_point_in = is_inside

        # search the time when following vehicle enters the polygon
        t_entry = None
        if t_exit is not None:
            pre_point_out = True
            for index, follow_row in tgtVehData.iterrows():
                curr_point = Point(follow_row['x'], follow_row['y'])
                is_inside = conflict_area.contains(curr_point)
                if pre_point_out and is_inside:
                    t_entry = follow_row['frame']
                    break
            pre_point_out = not is_inside
        
        if t_entry is not None and t_exit is not None:
            # calculate the PET of current scenario
            PET_Value = (t_entry - t_exit)/frame_rate
            return PET_Value
    else:
        return np.nan


def PTTC(egoVehData, tgtVehData):
    """
    Potential Time To Collision

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        metric_df (df): a dataframe that contains the frame number and the metric value
    ----------
    """
    # define function to calculate Euclidean distance
    def euclidean_dist(x1, y1, x2, y2):
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    only_zeros = np.all(egoVehData['precedingId'].values == 0)
    if not only_zeros: # preceding ID exists
        dst_list = []
        a2_long_list = []
        for (index1, egoRow), (index2, tgtRow) in zip(egoVehData.iterrows(), tgtVehData.iterrows()):
            # get all parameters for PTTC calculation
            x1 = egoRow['x']
            y1 = egoRow['y']
            x2 = tgtRow['x']
            y2 = tgtRow['y']
            a2_long = tgtRow['xAcceleration']
            a2_long_list.append(a2_long)
            dst = euclidean_dist(x1, y1, x2, y2)
            dst_list.append(dst)
        
        frameList = []
        pttcList = []
        # calculate euclidean distance derivation
        dst_dot_list = np.diff(dst_list)
        for i in range(len(dst_dot_list)):
            frameList.append(egoVehData['frame'][i])
            # a_long 
            a2_long = a2_long_list[i+1]
            # dst
            dst = dst_list[i+1]
            # dst dot
            dst_dot = dst_dot_list[i]
            # calculate PTTC
            under_sqrt = dst_dot**2 + 2*(-a2_long)*dst
            PTTC_Value = np.nan
            if not math.isnan(under_sqrt) and a2_long != 0:
                if under_sqrt >= 0:
                    PTTC_Value = (1/(-a2_long))*(-dst_dot + np.sqrt(dst_dot**2 + 2*(-a2_long)*dst))
                else:
                    PTTC_Value = (1/(-a2_long))*(-dst_dot + np.sqrt(dst_dot**2 - 2*(-a2_long)*dst))
            pttcList.append(PTTC_Value)

        metric_df = pd.DataFrame({
            'frame': frameList,
            'pttc': pttcList
        })

        return metric_df
    else:
        return np.nan





def PrET():
    """
    Predictive Enroachment Time

    Parameters:
    ----------
    Inputs:

    Returns:
       
    ----------
    Prediction information is not available, not appliable in our case
    ----------
    """
    pass


def TET(egoVehData, target_value):
    """
    Time Exposed TTC (Time-to-Collision) 

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        target_value (float): given target value of TTC 

    Returns:
        TET_Value (float): tet value 
    ----------
    """

    # time exposed TTC 
    TET_Value = ((egoVehData['ttc'] <= target_value) & (egoVehData['precedingId'] != 0)).sum()

    return TET_Value


def THW():
    """
    Time Headway 

    Parameters:
    ----------
    Inputs:

    Returns:
        
    ----------
    """
    # already exist in dataset
    pass


def TIT(egoVehData, target_value):
    """
    Time Integrated TTC (TIT)

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        framerate (Hz): frame rate of the dataset
        target_value: given target value 

    Returns:
        TIT (float): calculated Time Integrated TTC 
    ----------
    """

    TIT_Value = 0
    for index, ego_row in egoVehData.iterrows():
        if ego_row['precedingId'] != 0:
            curr_ttc = ego_row['ttc']
            if curr_ttc <= target_value:
                curr_tit = 1*(target_value - curr_ttc)
                TIT_Value += curr_tit
            else:
                curr_tit = 0*(target_value - curr_ttc)
                TIT_Value += curr_tit

    return TIT_Value


def TTCE(egoVehData, tgtVehData, framerate):
    """
    Time To Closest Encounter

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame
        framerate (Hz): frame rate of the dataset

    Returns:
        ttce (float): calculated ttce
    ----------
    """
    min_dst = float('inf')
    ttce = None
    ego_tgt_dst_list = []
    scenario_start_frame = egoVehData['frame'].values[0]
    ttce_frame = None

    for (index1, ego_row), (index2, tgt_row) in zip(egoVehData.iterrows(), tgtVehData.iterrows()):
        curr_frame = ego_row['frame']
        ego_pos = [ego_row['x'], ego_row['y']]
        # target vehicle
        ego_tgt_dst = euclidean(ego_pos, [tgt_row['x'].values[0], tgt_row['y'].values[0]])
        ego_tgt_dst_list.append(ego_tgt_dst)

        # minimum dst
        if len(ego_tgt_dst_list) != 0 and min(ego_tgt_dst_list) < min_dst:
            min_dst = min(ego_tgt_dst_list)
            ttce_frame = curr_frame

    # calculate ttce
    ttce = (ttce_frame - scenario_start_frame)/framerate

    return ttce


def TTB(egoVehData, tgtVehData):
    """
    Time To Brake

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        ttbValue 
    ----------
    Reference: 
    Nalic, D., Mihalj, T., Orucevic, F., Schabauer, M., Lex, C., Sinz, W., & Eichberger, A. (2022). 
    Criticality assessment method for automated driving systems by introducing fictive vehicles and variable criticality thresholds. 
    Sensors, 22(22), 8780.
    """

    # Acceleration threshold reference:
    # Miller, I., King, D., Wilkinson, C., & Siegmund, G. P. (2023). 
    # Decelerations for Vehicles with Anti-lock Brake Systems (ABS) on Dry Asphalt and Concrete Road Surfaces (No. 2023-01-0616). 
    # SAE Technical Paper.
    g = 9.81
    dece_low_max = 0.871*g
    dece_high_max = 1.081*g
    a_max = -1 * random.uniform(dece_low_max, dece_high_max)

    # iterate over id
    for (index1, ego_row), (index2, tgt_row) in zip(egoVehData.iterrows(), tgtVehData.iterrows()):
        if ego_row['precedingId'] != 0:
            v_rel = abs(ego_row['xVelocity']) - abs(tgt_row['xVelocity'].values[0])
            if v_rel > 0:
                d_curr = abs(ego_row['x'] - tgt_row['x'].values[0])
                dst2b = -(v_rel**2/(2*a_max))
                TTB_Value = (d_curr - dst2b)/(v_rel)
                if TTB_Value >= 0 and TTB_Value <= ego_row['ttc']:
                    return TTB_Value

    return np.nan


def TTK(tracks, framerate, TTK_threshold):
    """
    Time To Kickdown

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe created by pd.read_csv()
        framerate (Hz): frame rate of the dataset
        TTK_threshold: threshold of Time To Brake

    Returns:
        ego_ids (list): a list contains the ids of ego vehicle
        
    ----------
    Reference: Hillenbrand, J., Spieker, A. M., & Kroschel, K. (2006). 
    A multilevel collision mitigation approach—Its situation assessment, decision making, and performance tradeoffs. 
    IEEE Transactions on intelligent transportation systems, 7(4), 528-540.
    """
    pass
    # # For simplicity, assuming constant acceleration, the position is given by 1/2 * a * t^2 + v_initial * t
    # def x_ego(t, v_ego_initial, a_ego):
    #     return 0.5 * a_ego * t**2 + v_ego_initial * t

    # # Assuming the object is moving at a constant velocity, so no acceleration component is needed
    # def x_obj(t, v_obj_initial):
    #     return v_obj_initial * t

    # # Assuming a simple linear relationship for demonstration purposes
    # def h(v_ego_ttk):
    #     return a_ego * v_ego_ttk

    # ego_ids = []

    # # filter rows where "frame" is 1 or a multiple of 30
    # tracks_sample = tracks[tracks['frame'] % framerate == 0].copy()

    # # group according to id
    # grouped = tracks_sample.groupby('id')

    # # iterate over id
    # for id, group in grouped:
    #     isZero = np.all(group['precedingId'].values == 0)
    #     if not isZero:
    #         for index, ego_row in group.iterrows():
    #             if ego_row['precedingId'] != 0 and ego_row['ttc'] > 0:
    #                 target_row = tracks_sample[(tracks_sample['id'] == ego_row['precedingId']) & (tracks_sample['frame'] == ego_row['frame'])]
    #                 t_start = 0 #start of time interval
    #                 t_end = ego_row['ttc']
    #                 v_ego_initial = ego_row['xVelocity']
    #                 a_ego = ego_row['xAcceleration']
    #                 v_obj_initial = target_row['xVelocity'].values[0]
    #                 l_obj = target_row['width'].values[0]
    #                 l_ego = ego_row['width']
                    
    #                 # The function to find the root of (equation to calculate TTK)
    #                 def equation_to_solve(ttk):
    #                     # Here we calculate TTE (Time to Event) assuming it is the time when both objects meet
    #                     v_ego_ttk = max(0, v_ego_initial + a_ego * ttk) # velocity of the ego vehicle at TTK
    #                     x_ego_ttk = x_ego(ttk, v_ego_initial, a_ego)    # position of the ego vehicle at TTK
    #                     x_obj_ttk = x_obj(ttk, v_obj_initial)            # position of the object at TTK
    #                     tte = (x_obj_ttk + l_obj + l_ego - x_ego_ttk) / (v_ego_ttk - v_obj_initial)

    #                     # Return the equation that needs to be solved
    #                     return x_ego(tte, v_ego_initial, a_ego) - x_ego_ttk - (v_ego_ttk * (tte - ttk)) - (0.5 * h(v_ego_ttk) * (tte - ttk)**2)
                    
    #                 # Check if the signs of the function at the boundaries of the interval are different
    #                 fa = equation_to_solve(t_start)
    #                 fb = equation_to_solve(t_end)

    #                 if fa * fb > 0:
    #                     # The signs are not different, we need to find a new interval where the signs are different
    #                     # We will expand the interval to search for a sign change
    #                     while fa * fb > 0 and b < 1e6:  # setting a limit to prevent an infinite loop
    #                         b *= 2  # Expand the search interval
    #                         fb = equation_to_solve(b)
    #                         if fa * fb < 0:  # Check if the sign changed
    #                             break
    #                     else:
    #                         break

    #                 ttk_solution = bisect(equation_to_solve, t_start, t_end, xtol=1e-5, full_output=False)

    #                 if ttk_solution >= TTK_threshold[0] and ttk_solution <= TTK_threshold[1]:
    #                     ego_ids.append(ego_row['id'])
    #                     break
                 
    # return ego_ids


def TTS(egoVehData, tgtVehData):
    """
    Time To Steer

    Parameters:
    ----------
    Inputs:
        egoVehData (df): a dataframe that contains the ego vehicle data within the initial and final frame
        tgtVehData (df): a dataframe that contains the target vehicle data within the initial and final frame

    Returns:
        TTS_Value (): a list contains the ids of ego vehicle
        
    ----------
    Reference: Nalic, D., Mihalj, T., Orucevic, F., Schabauer, M., Lex, C., Sinz, W., & Eichberger, A. (2022). 
    Criticality assessment method for automated driving systems by introducing fictive vehicles and variable criticality thresholds. 
    Sensors, 22(22), 8780.
    """

    # Acceleration threshold reference:
    # Xu, J., Yang, K., Shao, Y., & Lu, G. (2015). 
    # An experimental study on lateral acceleration of cars in different environments in Sichuan, Southwest China. 
    # Discrete Dynamics in nature and Society, 2015.
    a_max_y = 1.8

    # iterate over id
    for (index1, ego_row), (index2, tgt_row) in zip(egoVehData.iterrows(), tgtVehData.iterrows()):
        if ego_row['precedingId'] != 0 and ego_row['ttc'] > 0:
            v_rel = abs(ego_row['xVelocity']) - abs(tgt_row['xVelocity'].values[0])
            if v_rel > 0:
                dy = 4
                dst2s = math.sqrt((2*dy)/a_max_y)*v_rel
                d_curr = abs(ego_row['x'] - tgt_row['x'].values[0])
                TTS_Value = (d_curr - dst2s)/(v_rel)
                if TTS_Value >= 0 and TTS_Value <= ego_row['ttc']:
                    return TTS_Value

    return np.nan


def TTM():
    """
    Time To Maneuver

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe created by pd.read_csv()
        framerate (Hz): frame rate of the dataset
        TTM_threshold: threshold of Time To Maneuver
    Returns:
        ego_ids (list): a list contains the ids of ego vehicle
    ----------
    """
    pass

def TTR():
    """
    Time To React

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe created by pd.read_csv()
        framerate (Hz): frame rate of the dataset
        TTM_threshold: threshold of Time To Maneuver
    Returns:
        ego_ids (list): a list contains the ids of ego vehicle
    ----------
    """

    pass


def WTTC():
    """
    Worst Time To Collision (WTTC)

    Parameters:
    ----------
    Inputs:
        tracks (df): a dataframe created by pd.read_csv()
        framerate (Hz): frame rate of the dataset
        TTM_threshold: threshold of Time To Maneuver
    Returns:
        ego_ids (list): a list contains the ids of ego vehicle
    ----------
    """
    # predicted trajectories from all actors are needed
    # this metric is only for online evaluation
    pass




