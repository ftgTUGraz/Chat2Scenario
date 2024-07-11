from pyproj import Transformer
from shapely.geometry import Polygon, Point
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import csv
from collections import defaultdict
import pandas as pd

class CoordinateTransformer:
    def __init__(self, in_proj='epsg:4326', out_proj='epsg:32632'):
        self.transformer = Transformer.from_crs(in_proj, out_proj)

    def extract_coordinates(self, kml_file, placemark_names, x_utm_origin, y_utm_origin):
        """
        Extract coordinates of specified points from a KML file and convert them to local coordinates.

        Parameters:
        kml_file (str): KML file path
        placemark_names (list): List of specified placemark names
        x_utm_origin (float): UTM coordinate system X origin offset
        y_utm_origin (float): UTM coordinate system Y origin offset

        Returns:
        list: List of extracted local coordinates
        """
        tree = ET.parse(kml_file)
        root = tree.getroot()
        namespace = '{http://www.opengis.net/kml/2.2}'
        coords = []

        for placemark_name in placemark_names:
            for placemark in root.findall(f'.//{namespace}Placemark'):
                name = placemark.find(f'{namespace}name').text
                if name == placemark_name:
                    coordinates_text = placemark.find(f'.//{namespace}coordinates').text.strip()
                    coordinate_list = coordinates_text.split()
                    for coordinate in coordinate_list:
                        lon, lat, _ = map(float, coordinate.split(','))
                        x, y = self.transformer.transform(lat, lon)
                        local_x = x - x_utm_origin
                        local_y = y - y_utm_origin
                        coords.append((local_x, local_y))
                    print(f"Extracted coordinates for {name}: {coords}")
                    break

        return coords


class PolygonPlotter:
    def __init__(self):
        pass

    def create_polygon_and_plot(self, kml_files_and_names, labels, colors, x_utm_origin, y_utm_origin):
        """
        Create polygons and plot specified points extracted from multiple KML files.

        Parameters:
        kml_files_and_names (list): List of tuples containing (KML file path, list of placemark names)
        labels (list): Corresponding list of legend labels
        colors (list): Corresponding list of colors
        x_utm_origin (float): UTM coordinate system X origin offset
        y_utm_origin (float): UTM coordinate system Y origin offset
        """
        fig, ax = plt.subplots()
        transformer = CoordinateTransformer()

        for (kml_file, placemark_names), label, color in zip(kml_files_and_names, labels, colors):
            coords = transformer.extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin)

            if not coords:
                print(f"Error: No coordinates extracted for {label}")
                continue

            polygon = Polygon(coords)
            path_vertices = coords + [coords[0]]
            codes = [Path.MOVETO] + [Path.LINETO] * (len(coords) - 1) + [Path.CLOSEPOLY]
            path = Path(path_vertices, codes)
            patch = PathPatch(path, facecolor=color, edgecolor='black', alpha=0.5, label=label)
            ax.add_patch(patch)

        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.set_title("Visualization of Lanes and Polygons")
        ax.legend()
        ax.grid(True)
        ax.axis('equal')
        plt.show()


class TrackDataProcessor:
    def __init__(self):
        pass

    def extract_polygon_from_kml(self, kml_file, placemark_names, x_utm_origin, y_utm_origin):
        """
        Extract polygons of specified points from a KML file.

        Parameters:
        kml_file (str): KML file path
        placemark_names (list): List of specified placemark names
        x_utm_origin (float): UTM coordinate system X origin offset
        y_utm_origin (float): UTM coordinate system Y origin offset

        Returns:
        Polygon: Extracted polygon
        """
        transformer = CoordinateTransformer()
        coords = transformer.extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin)
        return Polygon(coords) if coords else None

    def determine_turn_type_and_lane(self, point, onramp_polygons, offramp_polygons, lanes_polygons):
        """
        Determine the turn type and lane ID of a trajectory point.

        Parameters:
        point (Point): Trajectory point
        onramp_polygons (dict): Dictionary of OnRamp polygons
        offramp_polygons (dict): Dictionary of OffRamp polygons
        lanes_polygons (list): List of tuples containing (lane_id, Polygon)

        Returns:
        tuple: (turn type, lane ID)
        """
        for ramp_name, (onramp_polygon, lane_id) in onramp_polygons.items():
            if onramp_polygon and onramp_polygon.contains(point):
                return f'on-ramp', lane_id

        for ramp_name, (offramp_polygon, lane_id) in offramp_polygons.items():
            if offramp_polygon and offramp_polygon.contains(point):
                return f'off-ramp', lane_id

        for lane_id, polygon in lanes_polygons:
            if polygon and polygon.contains(point):
                return '', lane_id

        return 'Unknown', None

    def update_track_data(self, input_file, output_file, onramp_polygons, offramp_polygons, lanes_polygons):
        tracks = defaultdict(list)

        with open(input_file, 'r') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['laneId', 'activity_type']
            for row in reader:
                x_center = float(row['xCenter'])
                y_center = float(row['yCenter'])
                point = Point(x_center, y_center)
                turn_type, lane_id = self.determine_turn_type_and_lane(point, onramp_polygons, offramp_polygons, lanes_polygons)
                row['laneId'] = lane_id
                row['activity_type'] = turn_type
                tracks[row['trackId']].append(row)

        for track_id, rows in tracks.items():
            on_ramp_seen = False
            off_ramp_seen = False
            last_on_ramp_index = None

            for i, row in enumerate(rows):
                if row['activity_type'] == 'on-ramp':
                    if not on_ramp_seen:
                        on_ramp_seen = True
                        last_on_ramp_index = i
                    else:
                        row['activity_type'] = ''
                        last_on_ramp_index = i
                elif row['activity_type'] == 'off-ramp':
                    if off_ramp_seen:
                        row['activity_type'] = ''
                    else:
                        off_ramp_seen = True
                    if on_ramp_seen and last_on_ramp_index is not None and last_on_ramp_index + 1 < len(rows):
                        rows[last_on_ramp_index + 1]['activity_type'] = 'follow lane'
                    last_on_ramp_index = None

            if on_ramp_seen and last_on_ramp_index is not None and last_on_ramp_index + 1 < len(rows):
                rows[last_on_ramp_index + 1]['activity_type'] = 'follow lane'

        with open(output_file, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for rows in tracks.values():
                writer.writerows(rows)

        print(f"Updated tracks have been saved to {output_file}")

    def extract_turn_type_and_lane(self, input_file, onramp_polygons, offramp_polygons, lanes_polygons):
        """
        Extract turn type and lane ID for each point in the input file.

        Parameters:
        input_file (str): Input CSV file path
        onramp_polygons (dict): Dictionary of OnRamp polygons
        offramp_polygons (dict): Dictionary of OffRamp polygons
        lanes_polygons (list): List of tuples containing (lane_id, Polygon)

        Returns:
        DataFrame: Updated DataFrame with turn type and lane ID
        """
        df = pd.read_csv(input_file)

        for index, row in df.iterrows():
            x_center = float(row['xCenter'])
            y_center = float(row['yCenter'])
            point = Point(x_center, y_center)
            turn_type, lane_id = self.determine_turn_type_and_lane(point, onramp_polygons, offramp_polygons, lanes_polygons)
            df.at[index, 'laneId'] = lane_id
            df.at[index, 'activity_type'] = turn_type

        return df
