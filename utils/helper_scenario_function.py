"""
Author: Yongqi Zhao
Date Created: 2023-12-14
Copy Right: TU Graz FTG ADAS Group
Email: yongqi.zhao@tugraz.at
"""
from scenariogeneration import xosc
import math
from helper_data_functions import *
import matplotlib.pyplot as plt

def create_catalog(catalogname="VehicleCatalog", path="../xosc/Catalogs/Vehicles"):

    catalog = xosc.Catalog()
    catalog.add_catalog(catalogname, path)

    return catalog


def create_roadnetwork(roadfile_path= "../xodr/DJI_0001.xodr"):

    # road = xosc.RoadNetwork(roadfile="../xodr/DJI_0001.xodr", scenegraph="../models/e6mini.osgb")
    road = xosc.RoadNetwork(roadfile=roadfile_path)

    return road


def create_parameter_declearations(name="$HostVehicle", value="car_white"):

    paramdec = xosc.ParameterDeclarations()
    paramdec.add_parameter(xosc.Parameter(name, xosc.ParameterType.string, value))

    return paramdec


def create_entities(entityname, width=2, length=5, height=1.8, x_center=2.0, y_center=0, z_center=0.9):

    # bb = xosc.BoundingBox(width, length, height, x_center, y_center, z_center)
    # fa = xosc.Axle(0.523598775598, 0.8, 1.68, 2.98, 0.4)
    # ba = xosc.Axle(0.523598775598, 0.8, 1.68, 0, 0.4)
    # white_veh = xosc.Vehicle("car_white", xosc.VehicleCategory.car, bb, fa, ba, 69, 10, 10)

    # white_veh.add_property_file("../models/car_white.osgb")
    # white_veh.add_property("model_id", "0")
    
    # utilize the default vehicle catalog 
    cataref = xosc.CatalogReference("VehicleCatalog", "$HostVehicle") 

    ## create entities
    objname = entityname
    entities = xosc.Entities()
    entities.add_scenario_object(objname, cataref)

    return entities


def create_init_action(init_speed, init_pos_x, init_pos_y, init_pos_h, entityname):

    init = xosc.Init()
    step_time = xosc.TransitionDynamics(xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1)

    objspeed = xosc.AbsoluteSpeedAction(init_speed, step_time)
    objstart = xosc.TeleportAction(xosc.WorldPosition(init_pos_x, init_pos_y, 0, init_pos_h, 0, 0))

    init.add_init_action(entityname, objspeed)
    init.add_init_action(entityname, objstart)

    return init


def create_story(entityname):

    # parameter declaration for story
    storyparam = xosc.ParameterDeclarations()
    storyparam.add_parameter(
        xosc.Parameter("$owner", xosc.ParameterType.string, entityname)
    )
    story = xosc.Story("mystory", storyparam)
    
    return story


def create_act():

    starttrigger = xosc.ValueTrigger(
        "starttrigger",
        0,
        xosc.ConditionEdge.none,
        xosc.SimulationTimeCondition(0, xosc.Rule.greaterOrEqual),
    )
    act = xosc.Act("my_act", starttrigger)

    return act


def create_action(id_, framerate, start_frame,\
                  init_state, curr_id, end_frame):

    time_list = []
    x_list = []
    position_list = []

    # late appear: extend missing state
    # if init_x != id_["x"][0]:
    if id_["frame"][0] != start_frame:

        missing_time_list = []
        missing_x_list = []
        missing_pos_list = []
        missing_frame = id_["frame"][0] - 1

        for i in range(1, missing_frame+1):
            curr_time = i/framerate
            missing_time_list.append(curr_time)
            curr_pos_x = init_state["init_x"] - init_state["init_speed"]*curr_time # plus or minus depends on the driving direction
            missing_x_list.append(curr_pos_x)
            missing_pos_list.append(xosc.WorldPosition(curr_pos_x, init_state["init_y"], 0, init_state["init_orientation"]+math.pi, 0, 0))

        time_list.extend(missing_time_list)
        x_list.extend(missing_x_list)
        position_list.extend(missing_pos_list)

    for i in id_["frame"]:
        t = i/framerate
        time_list.append(t)
        
    for i in range(len(id_["frame"])):
        x_list.append(id_["x"][i])
        position_list.append(xosc.WorldPosition(id_["x"][i], -id_["y"][i], 0, id_["orientation"][i]+math.pi, 0, 0))

    # early disappear: extend missing state
    if id_["frame"][-1] != end_frame:
        # end state
        end_state_time = id_["frame"][-1]/framerate
        end_pos_x = id_["x"][-1]
        end_pos_y = -id_["y"][-1]
        end_vel = id_["sumV"][-1]
        end_orientation = id_["orientation"][-1] + math.pi
        
        missing_time_list = []
        missing_x_list = []
        missing_pos_list = []
        missing_frame = end_frame - id_["frame"][-1]

        for i in range(id_["frame"][-1]+1, end_frame+1):
            curr_time = i/framerate
            missing_time_list.append(curr_time)
            curr_pos_x = end_pos_x - end_vel*(curr_time-end_state_time)
            missing_x_list.append(curr_pos_x)
            missing_pos_list.append(xosc.WorldPosition(curr_pos_x, end_pos_y, 0, end_orientation, 0, 0))
        
        time_list.extend(missing_time_list)
        x_list.extend(missing_x_list)
        position_list.extend(missing_pos_list)

    polyline = xosc.Polyline(time_list, position_list)

    # define trajectory according to polyline: true means trajectory closed at the end
    traj = xosc.Trajectory("my_trajectory", False)
    traj.add_shape(polyline)

    # trajact = xosc.FollowTrajectoryAction(traj, xosc.FollowingMode.position, xosc.ReferenceContext.relative, 1, 0)
    trajact = xosc.FollowTrajectoryAction(traj, xosc.FollowingMode.position)
    
    label = f"id_{curr_id}_revise"
    plt.plot(time_list, x_list, label= label)

    return trajact

def create_everything(unique_ids, id_information, frame_len_threshold, framerate, left_lane_ids, right_lane_ids, entities, cataref, init, start_frame, end_frame, act):
    for curr_id in unique_ids:

        entityname = f"obj_{curr_id}"
        id_ = get_data_for_scenario(id_information, curr_id)
        # skip objects with too short frames
        # print(id_["frame"])
        if len(id_["frame"]) < frame_len_threshold:
            continue
        # plot and visualization
        label = f"id_{curr_id}_ori"

        id_time = [x/30 for x in id_["frame"]]
        # plt.plot(id_time, id_["x"], label=label)
        init_state = calculate_initial_state(id_, framerate, left_lane_ids, right_lane_ids)
        entityname = f"obj_{curr_id}"
        entities.add_scenario_object(entityname, cataref)
        create_init(init, init_state, entityname)
        manGroupName, manName, eventName, actionname = create_name(entityname)
        manGroup, man, event, trigger = create_xosc(entityname)
        trajaction = create_action(id_, framerate, start_frame, init_state, curr_id, end_frame)

        # add everything into Act
        event.add_action(actionname, trajaction)
        event.add_trigger(trigger)
        man.add_event(event)
        manGroup.add_actor(entityname)
        manGroup.add_maneuver(man)
        act.add_maneuver_group(manGroup)



""" 
# def create_scenario(id_["frame"], id_["x"], id_["y"], id_sumV, mean_width_id, mean_height_id, id_orientation, entityname, framerate, output_path, sim_time=10):
    
    # get ininital info
    init_speed = id_sumV[0]
    init_pos_x = id_["x"][0]
    init_pos_y = -id_["y"][0] # trajectory should be in accordance with map (check the coordinate of x and y)
    init_pos_h = id_orientation[0]


    # ##### create catalogs #####
    # catalog = create_catalog()

    # ##### create road #####
    # road = create_roadnetwork()

    # ##### create parameters for OpenSCENARIO #####
    # paramdec = create_parameter_declearations()

    ##### create entities (entities should be created using for-loop, depends on how many objects are included) ####
    entities = create_entities(entityname, mean_height_id, mean_width_id)


    ###### begin of the StoryBoard ######
    #### create storyboard
    init = create_init_action(init_speed, init_pos_x, init_pos_y, init_pos_h, entityname)
    storyboard_stoptrigger =  xosc.ValueTrigger(
                "stop_simulation",
                0,
                xosc.ConditionEdge.rising,
                xosc.SimulationTimeCondition(sim_time, xosc.Rule.greaterThan),
                "stop",
            )
    storyboard = xosc.StoryBoard(init, stoptrigger=storyboard_stoptrigger)

    #### create story 
    story = create_story(entityname)

    ### create act
    act = create_act()

    ## create maneuver group
    manGroup = xosc.ManeuverGroup("maneueverGroup")
    # create maneuver
    man = xosc.Maneuver("maneuver")
    # create event 
    event = xosc.Event("event", xosc.Priority.parallel)
    # create start trigger for event
    trigcond = xosc.TimeHeadwayCondition(entityname, 1/30, xosc.Rule.greaterThan)
    trigger = xosc.EntityTrigger("mytesttrigger", 0.2, xosc.ConditionEdge.rising, trigcond, entityname)
    # create action
    trajaction = create_action(id_["frame"], id_["x"], id_["y"], id_orientation, framerate)


    # combine everything
    event.add_trigger(trigger)
    event.add_action("myaction", trajaction)
    man.add_event(event)
    manGroup.add_maneuver(man)
    manGroup.add_actor(entityname)
    act.add_maneuver_group(manGroup)
    story.add_act(act)
    storyboard.add_story(story)
    scenario = xosc.Scenario(
        name="myScenario",
        author="DD2Scenario",
        parameters= paramdec,
        entities= entities,
        storyboard=storyboard,
        roadnetwork=road,
        catalog=catalog
    )

    # write scenario into specific folder
    scenario.write_xml(output_path)
    

"""