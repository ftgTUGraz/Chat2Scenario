import csv
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from pyproj import Transformer

def parse_kml_coordinates(kml_file):
    tree = ET.parse(kml_file)
    root = tree.getroot()
    
    namespace = '{http://www.opengis.net/kml/2.2}'
    
    coordinates = []
    for placemark in root.findall(f'.//{namespace}Placemark'):
        for coords in placemark.findall(f'.//{namespace}coordinates'):
            coord_text = coords.text.strip()
            coord_list = coord_text.split()
            for coord in coord_list:
                lon, lat, alt = map(float, coord.split(','))
                coordinates.append((lon, lat))
    
    return coordinates

def transform_coordinates(coords, x_utm_origin, y_utm_origin):
    transformer = Transformer.from_crs("epsg:4326", "epsg:32632")  # UTM zone 32N
    transformed_coords = []
    for lon, lat in coords:
        x, y = transformer.transform(lat, lon)
        local_x = x - x_utm_origin
        local_y = y - y_utm_origin
        transformed_coords.append((local_x, local_y))
    return transformed_coords

def read_tracks(file_path):
    tracks = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            track_id = int(row['trackId'])
            x_center = float(row['xCenter'])
            y_center = float(row['yCenter'])
            tracks.append((track_id, x_center, y_center))
    return tracks

def get_lane_id(point, lane_polygons):
    for lane_id, polygons in lane_polygons.items():
        for polygon in polygons:
            if polygon.contains(point):
                return lane_id
    return None

def simplify_lane_sequence(lane_sequence):
    simplified_sequence = []
    previous_lane = None
    for lane in lane_sequence:
        if lane != previous_lane:
            simplified_sequence.append(lane)
            previous_lane = lane
    return simplified_sequence

def determine_activity_type(lane_sequence):
    if len(lane_sequence) < 2:
        return None
    
    lane_id_start = lane_sequence[0]
    lane_id_end = lane_sequence[-1]
    
    if (lane_id_start in [2, 3] and lane_id_end == 11) or \
       (lane_id_start in [4, 5] and lane_id_end == 12) or \
       (lane_id_start in [6, 7] and lane_id_end == 13) or \
       (lane_id_start in [8, 9] and lane_id_end == 10):
        return "turn right"
    elif (lane_id_start in [2, 3] and lane_id_end == 12) or \
         (lane_id_start in [4, 5] and lane_id_end == 13) or \
         (lane_id_start in [6, 7] and lane_id_end == 10) or \
         (lane_id_start in [8, 9] and lane_id_end == 11):
        return "go straight"
    elif (lane_id_start in [2, 3] and lane_id_end == 13) or \
         (lane_id_start in [4, 5] and lane_id_end == 10) or \
         (lane_id_start in [6, 7] and lane_id_end == 11) or \
         (lane_id_start in [8, 9] and lane_id_end == 12):
        return "turn left"
    elif (lane_id_start in [2, 3] and lane_id_end == 10) or \
         (lane_id_start in [4, 5] and lane_id_end == 11) or \
         (lane_id_start in [6, 7] and lane_id_end == 12) or \
         (lane_id_start in [8, 9] and lane_id_end == 13):
        return "U-turn"
    elif any(lane in lane_sequence for lane in [14, 15, 16, 17]):
        return "turn right"
    return None

def plot_multiple_polygons(lane_polygons, x_utm_origin, y_utm_origin):
    fig, ax = plt.subplots()
    colormap = plt.colormaps['hsv']
    
    for i, (lane_id, polygons) in enumerate(lane_polygons.items()):
        color = colormap(i / len(lane_polygons))  # Use hsv colormap for diverse colors
        for j, polygon in enumerate(polygons):
            # Plot the polygon
            x, y = polygon.exterior.xy
            ax.fill(x, y, alpha=0.5, fc=color, ec='black', label=f'Lane {lane_id}')
    
    ax.set_aspect('equal', 'box')
    plt.xlabel('Local X (m)')
    plt.ylabel('Local Y (m)')
    plt.title('Transformed Polygons')
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys())
    plt.show()

def main():
    # List of KML files
    kml_files = {
        1: ['playground2-23_lane1-outer.kml', 'playground2-23_lane1_inner.kml'],
        2: ['playground2-23_lane2.kml'],
        3: ['playground2-23_lane3.kml'],
        4: ['playground2-23_lane4.kml'],
        5: ['playground2-23_lane5.kml'],
        6: ['playground2-23_lane6.kml'],
        7: ['playground2-23_lane7.kml'],
        8: ['playground2-23_lane8.kml'],
        9: ['playground2-23_lane9.kml'],
        10: ['playground2-23_lane10.kml'],
        11: ['playground2-23_lane11.kml'],
        12: ['playground2-23_lane12.kml'],
        13: ['playground2-23_lane13.kml'],
        14: ['playground2-23_lane14.kml'],
        15: ['playground2-23_lane15.kml'],
        16: ['playground2-23_lane16.kml'],
        17: ['playground2-23_lane17.kml']
    }

    # UTM origin coordinates
    x_utm_origin = 301221.3650
    y_utm_origin = 5641501.3410

    lane_polygons = {}
    
    # Parse each KML file and transform coordinates
    for lane_id, files in kml_files.items():
        polygons = []
        for kml_file in files:
            coords = parse_kml_coordinates(kml_file)
            transformed_coords = transform_coordinates(coords, x_utm_origin, y_utm_origin)
            polygon = Polygon(transformed_coords)
            polygons.append(polygon)
        lane_polygons[lane_id] = polygons

    # Plot polygons
    plot_multiple_polygons(lane_polygons, x_utm_origin, y_utm_origin)

    # Read track data
    tracks_file = '02_tracks.csv'  # Path to the track data file
    tracks = read_tracks(tracks_file)

    track_lane_sequences = {}

    # Determine lane for each track point
    for track_id, x_center, y_center in tracks:
        point = Point(x_center, y_center)
        lane_id = get_lane_id(point, lane_polygons)
        if lane_id:
            if track_id not in track_lane_sequences:
                track_lane_sequences[track_id] = []
            track_lane_sequences[track_id].append(lane_id)

    # Read original track data and add new columns
    updated_tracks = []
    with open(tracks_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames + ['laneId', 'lane_sequence', 'activity_type']
        index = 0
        last_track_id = 0
        for row in reader:
            track_id = int(row['trackId'])
            if last_track_id != track_id:
                index = 0
                last_track_id =  track_id
            if track_id in track_lane_sequences:
                lane_sequence = simplify_lane_sequence(track_lane_sequences[track_id])
                if index < len(track_lane_sequences[track_id]):
                    row['laneId'] = track_lane_sequences[track_id][index]
                    index += 1
                lane_sequence = [lane for lane in lane_sequence if lane is not None]
                row['lane_sequence'] = lane_sequence
                row['activity_type'] = determine_activity_type(lane_sequence)
            else:
                row['laneId'] = None
                row['lane_sequence'] = None
                row['activity_type'] = None
            updated_tracks.append(row)

    # Write updated track data
    updated_tracks_file = '02_updated_tracks.csv'
    with open(updated_tracks_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in updated_tracks:
            writer.writerow(row)

if __name__ == "__main__":
    main()
