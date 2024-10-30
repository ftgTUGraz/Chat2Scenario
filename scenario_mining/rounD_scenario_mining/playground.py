import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from pyproj import Transformer
import map_data.RounD_map_data.RounD_data as RounD_data
import pandas as pd

class Playground:
    def __init__(self, index):
        self.index = index
        self.lane_polygons = {}
        self.exit_lane8 = 0  # Set to 0 during initialization if needed in determine_roundabout_activity
        self.initialize_lane_polygons()

    def initialize_lane_polygons(self):
        if self.index == 0:
            # Use lanes_polygons from RounD_data
            for i, polygon in enumerate(RounD_data.lanes_polygons):
                lane_id = self.get_lane_id_from_index(i)
                self.add_polygon_to_lane(lane_id, polygon)
        elif self.index == 1:
            # Use lanes_polygons1 from RounD_data
            for i, polygon in enumerate(RounD_data.lanes_polygons1):
                lane_id = self.get_lane_id_from_index(i)
                self.add_polygon_to_lane(lane_id, polygon)
        elif 2 <= self.index <= 23:
            # Use lanes_polygons2_23 from RounD_data
            for i, polygon in enumerate(RounD_data.lanes_polygons2_23):
                lane_id = self.get_lane_id_from_index(i, index_2_23=True)
                self.add_polygon_to_lane(lane_id, polygon)
        else:
            print(f"Invalid index or index out of range ({self.index}). No operation executed.")

    def get_lane_id_from_index(self, i, index_2_23=False):
        if i == 0:
            return 1
        elif i == 1:
            return 18 if index_2_23 else 12
        else:
            return i

    def add_polygon_to_lane(self, lane_id, polygon):
        if lane_id not in self.lane_polygons:
            self.lane_polygons[lane_id] = []
        self.lane_polygons[lane_id].append(polygon)

    def get_lane_id(self, point):
        for lane_id, polygons in self.lane_polygons.items():
            for polygon in polygons:
                if polygon.contains(point):
                    return lane_id
        return None

    def simplify_lane_sequence(self, lane_sequence):
        simplified_sequence = []
        previous_lane = None
        for lane in lane_sequence:
            if lane != previous_lane:
                simplified_sequence.append(lane)
                previous_lane = lane
        return simplified_sequence

    def determine_roundabout_activity(self, lane_id, track_lane_sequence, current_index):
        if self.index == 0:
            return self.determine_roundabout_activity_index_0(lane_id, track_lane_sequence, current_index)
        elif self.index == 1:
            return self.determine_roundabout_activity_index_1(lane_id, track_lane_sequence, current_index)
        elif 2 <= self.index <= 23:
            return self.determine_roundabout_activity_index_2_23(lane_id)
        else:
            return None

    def determine_roundabout_activity_index_0(self, lane_id, track_lane_sequence, current_index):
        """
        Determine the activity type based on the current lane_id and track_lane_sequence.
        
        Parameters:
        lane_id (int): The ID of the lane in which the vehicle is currently located.
        track_lane_sequence (list): The sequence of lane IDs for the current trackId.
        current_index (int): The current index within the track_lane_sequence being processed.
        
        Returns:
        str: The activity type ('enter', 'inside', 'exit') based on lane_id and lane sequence.
        """

        if lane_id in [2, 3, 4, 5]:
            return "enter"
        elif lane_id in [1, 12]:
            return "inside"
        elif lane_id in [6, 8, 10, 11]:
            if lane_id == 8:
                self.exit_lane8 = 1
            return "exit"
        elif lane_id == 9:
            # Check if this is the first entry for this trackId
            if current_index == 0 or track_lane_sequence[0] == 9:
                return "enter"
            # Check the previous lane_id if it exists
            elif self.exit_lane8 == 1:
                return "exit"
        return None

    def determine_roundabout_activity_index_1(self, lane_id, track_lane_sequence, current_index):
        """
        Determine the activity type based on the current lane_id and track_lane_sequence.
        
        Parameters:
        lane_id (int): The ID of the lane in which the vehicle is currently located.
        track_lane_sequence (list): The sequence of lane IDs for the current trackId.
        current_index (int): The current index within the track_lane_sequence being processed.
        
        Returns:
        str: The activity type ('enter', 'inside', 'exit') based on lane_id and lane sequence.
        """

        if lane_id in [2, 3, 4, 6, 7]:
            return "enter"
        elif lane_id in [1, 12]:
            return "inside"
        elif lane_id in [8, 9, 10, 11]:
            if lane_id == 8:
                self.exit_lane8 = 1
            return "exit"
        elif lane_id == 5:
            # Check if this is the first entry for this trackId
            if current_index == 0 or track_lane_sequence[0] == 5:
                return "enter"
            # Check the previous lane_id if it exists
            elif self.exit_lane8 == 1:
                return "exit"
        return None

    def determine_roundabout_activity_index_2_23(self, lane_id):
        """
        Determine the activity type based on the current lane_id and track_lane_sequence.
        
        Parameters:
        lane_id (int): The ID of the lane in which the vehicle is currently located.
        track_lane_sequence (list): The sequence of lane IDs for the current trackId.
        current_index (int): The current index within the track_lane_sequence being processed.
        
        Returns:
        str: The activity type ('enter', 'inside', 'exit') based on lane_id and lane sequence.
        """

        if lane_id in [2, 3, 4, 5, 6, 7, 8, 9]:
            return "enter"
        elif lane_id in [10, 11, 12, 13]:
            return "exit"
        elif lane_id in [1, 18]:
            return "inside"
        return None

    def update_track_file(self, tracks_file):
        # Reset file pointer to the beginning
        tracks_file.seek(0)
        # Use pandas to read the CSV file
        df_origin = pd.read_csv(tracks_file)
        # Find unique frames and sample every N frames to get consistent frame intervals
        unique_frames = sorted(df_origin['frame'].unique())
        consistent_frames = unique_frames[::25]
        # Filter the data to include only these frames
        df = df_origin[df_origin['frame'].isin(consistent_frames)].reset_index(drop=True)
        # Initialize new 'laneId' and 'activity_type' columns
        df['laneId'] = None
        df['activity_type'] = None
        # Group DataFrame by 'trackId'
        grouped = df.groupby('trackId')
        for track_id, group in grouped:
            lane_ids = []
            indices = []
            for index, row in group.iterrows():
                x_center = float(row['xCenter'])
                y_center = float(row['yCenter'])
                point = Point(x_center, y_center)
                # Determine lane_id
                lane_id = self.get_lane_id(point)
                lane_ids.append(lane_id)
                indices.append(index)
                # Update 'laneId' column in DataFrame
                df.at[index, 'laneId'] = lane_id
            # Simplify lane sequence
            simplified_sequence = self.simplify_lane_sequence(lane_ids)
            # Iterate through each index to calculate 'activity_type'
            for i, (index, lane_id) in enumerate(zip(indices, lane_ids)):
                if lane_id is not None:
                    activity_type = self.determine_roundabout_activity(lane_id, lane_ids, i)
                    df.at[index, 'activity_type'] = activity_type
        return df

    # Additional methods such as plot_multiple_polygons, write_lane_polygons_to_file can be included if needed
