from pyproj import Proj, Transformer
from shapely.geometry import Polygon, Point
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import csv
from collections import defaultdict

# Define the projection transformation
in_proj = 'epsg:4326'  # WGS84
out_proj = 'epsg:32632'  # UTM zone 32N

# Use Transformer class for transformation
transformer = Transformer.from_crs(in_proj, out_proj)

def extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin):
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
                    x, y = transformer.transform(lat, lon)
                    local_x = x - x_utm_origin
                    local_y = y - y_utm_origin
                    coords.append((local_x, local_y))
                print(f"Extracted coordinates for {name}: {coords}")
                break

    return coords

def create_polygon_and_plot(kml_files_and_names, labels, colors, x_utm_origin, y_utm_origin):
    fig, ax = plt.subplots()

    for (kml_file, placemark_names), label, color in zip(kml_files_and_names, labels, colors):
        coords = extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin)

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

def extract_polygon_from_kml(kml_file, placemark_names, x_utm_origin, y_utm_origin):
    coords = extract_coordinates(kml_file, placemark_names, x_utm_origin, y_utm_origin)
    return Polygon(coords) if coords else None

def determine_turn_type_and_lane(point, onramp_polygons, offramp_polygons, lanes_polygons):
    for ramp_name, (onramp_polygon, lane_id) in onramp_polygons.items():
        if onramp_polygon and onramp_polygon.contains(point):
            return f'OnRamp', lane_id

    for ramp_name, (offramp_polygon, lane_id) in offramp_polygons.items():
        if offramp_polygon and offramp_polygon.contains(point):
            return f'OffRamp', lane_id
    
    for lane_id, polygon in lanes_polygons:
        if polygon and polygon.contains(point):
            return 'KeepRamp', lane_id
    
    return 'Unknown', None

def update_track_data(input_file, output_file, onramp_polygons, offramp_polygons, lanes_polygons):
    tracks = defaultdict(list)

    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['laneId', 'activity_type']
        for row in reader:
            x_center = float(row['xCenter'])
            y_center = float(row['yCenter'])
            point = Point(x_center, y_center)
            turn_type, lane_id = determine_turn_type_and_lane(point, onramp_polygons, offramp_polygons, lanes_polygons)
            row['laneId'] = lane_id
            row['activity_type'] = turn_type
            tracks[row['trackId']].append(row)

    for track_id, rows in tracks.items():
        activities = set(row['activity_type'] for row in rows)
        if any('OnRamp' in activity for activity in activities) and any('OffRamp' in activity for activity in activities):
            final_activity = 'OnRamp|OffRamp'
        elif any('OnRamp' in activity for activity in activities):
            final_activity = next(activity for activity in activities if 'OnRamp' in activity)
        elif any('OffRamp' in activity for activity in activities):
            final_activity = next(activity for activity in activities if 'OffRamp' in activity)
        else:
            final_activity = 'KeepRamp'
        
        for row in rows:
            row['activity_type'] = final_activity

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for rows in tracks.values():
            writer.writerows(rows)

    print(f"Updated tracks have been saved to {output_file}")
